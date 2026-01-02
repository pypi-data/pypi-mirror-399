import inspect
import json
import logging
from pathlib import Path

import pytest

from jamsuite.logger import DictMixin, ErrorMixin, JSONSerializer


class TestErrorFormatter(JSONSerializer, ErrorMixin, DictMixin, logging.Formatter):
    __test__ = False


@pytest.fixture
def log_message():
    return "Message here"


@pytest.fixture
def log_exception():
    return Exception("Rosie Tuesday")


@pytest.fixture
def log(logger_factory):
    yield logger_factory(formatter=TestErrorFormatter())


def test_exc_info_no_message(log, log_exception):
    """
    Steps:

    1 - log err_info with no message

    Result:

    * Raise TypeError from logging package
    """
    with pytest.raises(TypeError):
        log.error(exc_info=log_exception)


def test_exc_info_and_message(log, log_buffer, log_message, log_exception):
    """
    Steps:

    1 - log exc_info and message

    Result:

    * Both message and exception are present in log output
    * Exception without traceback has not traceback in the log output
    """
    log.error(log_message, exc_info=log_exception)
    log_entry = json.loads(log_buffer.getvalue())
    assert log_entry["message"] == log_message
    assert log_entry["log_exception"] == f"Exception({log_exception})"
    assert "log_traceback" not in log_entry


def test_exc_info_and_traceback(log, log_buffer, log_message, log_exception):
    """
    Steps:

    1 - raise exception
    2 - log it with message

    Result:

    * Both message and exception are present in log output
    * Exception has traceback with the one line from the test
    """
    try:
        raise log_exception
    except Exception as e:
        log.error(log_message, exc_info=e)

    log_entry = json.loads(log_buffer.getvalue())
    assert log_entry["message"] == log_message
    assert log_entry["log_exception"] == f"Exception({log_exception})"
    test_func = inspect.stack()[0].function
    test_path = str(Path(__file__).relative_to(Path.cwd()))
    assert len(log_entry["log_traceback"]) == 1
    assert test_func in log_entry["log_traceback"][0]
    assert test_path in log_entry["log_traceback"][0]
