import logging
import uuid
from io import StringIO
from typing import Optional

import pytest

from jamsuite.logger import get_log_level

from .utils import load_class_from_string


@pytest.fixture
def log_buffer() -> StringIO:
    """Provides a StringIO stream to capture log output."""
    return StringIO()


@pytest.fixture
def logger_factory(log_buffer):
    created_handlers = []
    created_loggers = []

    def create_logger(name: Optional[str] = None, formatter: Optional[str | logging.Formatter] = None, level: str | int = logging.DEBUG):
        """
        Create an isolated logger with a StringIO handler for testing.
        """
        # Generate unique name to avoid conflicts
        if not name:
            name = f"test_logger_{uuid.uuid4().hex[:8]}"

        level = get_log_level(level)
        # create formatter
        if isinstance(formatter, str):
            FormatterClass = load_class_from_string(formatter)  # noqa: N806
            formatter = FormatterClass()

        # create handler from log_buffer
        handler = logging.StreamHandler(log_buffer)
        handler.setFormatter(formatter)
        handler.setLevel(level)
        created_handlers.append(handler)

        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
        created_loggers.append(name)

        return logger

    yield create_logger

    # Cleanup: Remove all handlers and loggers
    for handler in created_handlers:
        handler.close()

    for logger_name in created_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.filters.clear()
        # Remove from logging manager
        if logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[logger_name]

    log_buffer.close()
