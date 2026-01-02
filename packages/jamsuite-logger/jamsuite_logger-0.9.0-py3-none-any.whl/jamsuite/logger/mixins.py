from .helpers import (
    RE_SENSITIVE_ATTR,
    format_dict,
    format_exception,
    format_template_debug,
    format_traceback_as_list,
    redact_secrets,
    set_nested_val,
)


class DictMixin:
    # From Docs: There are four keyword arguments in kwargs which are inspected: exc_info, stack_info, stacklevel and extra.
    # https://docs.python.org/3/library/logging.html#logging.Logger.debug

    def __init__(self, *args, **kwargs):
        self.message_key = kwargs.pop("message_key", "message")
        super().__init__(*args, **kwargs)

    def format(self, record) -> dict:
        """
        formats a records message into a dictionary

        does not handle exceptions or timestamps

        How would we expect a message like: log.info('good stuff', my_obj, error, extra=)
        to get logged?

        {
             "message": "good stuff",
             "args": [
                my_obj,
                error,
             ]
        }

        How would we expect a message like: log.info('good stuff', my_obj, error)
        to get logged?

        """
        return format_dict(record, message_key=self.message_key)


class ErrorMixin:
    def __init__(self, *args, **kwargs):
        self.exception_key = kwargs.pop("exception_key", "log_exception")
        self.template_debug_key = kwargs.pop("template_debug_key", "log_template_debug")
        self.traceback_key = kwargs.pop("traceback_key", "log_traceback")
        super().__init__(*args, **kwargs)

    def format(self, record) -> dict:
        """
        formats exception from record into msg dict

        you can log exceptions using exc_info, for example:

        ```
        try:
            ...
        catch Exception as e:
            log.error("an error occurred!", exc_info=e)
        ```

        You can also log exception as

        Right now, as-is, this will serialize as:

        Q. How do we add in support for record.stack_info (OR .sinfo)?  https://docs.python.org/3/library/logging.html#logrecord-attributes

        --> Needs more investigation
        """
        msg = super().format(record)

        if record.exc_info:
            self._add_exception_info(msg, record.exc_info)
        elif isinstance(msg["message"], Exception):
            # if message is an exception, log it as such
            self._add_exception_info(msg, msg["message"])
            del msg["message"]

        return msg

    def _add_exception_info(self, msg, exc):
        "convenience func to set exception values in message"
        set_nested_val(msg, self.exception_key, format_exception(exc))
        try:
            # for Jinja TemplateSyntaxErrors
            set_nested_val(msg, self.template_debug_key, format_template_debug(exc[1].template_debug))
        except (AttributeError, TypeError):
            pass
        if tb := format_traceback_as_list(exc):
            set_nested_val(msg, self.traceback_key, tb)


class TimestampMixin:
    """
    Add timestamp to the log message dictionary. By default adds the timestamp to `log_time` key in the dictionary.

    You can specifiy a different timestamp_key in the constructor to the Formatter:
    (ex. `TimestampFormatter(timestamp_key='@timestamp')` or `TimestampFormatter(timestamp_key='_meta.time')`).

    Uses standard Python Formatter.formatTime to format the time, per the `datefmt` setting

    See: https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime for more info
    """

    def __init__(self, *args, **kwargs):
        self.timestamp_key = kwargs.pop("timestamp_key", "log_time")
        super().__init__(*args, **kwargs)

    def format(self, record) -> dict:
        msg = super().format(record)
        # add timestamp info
        record.asctime = self.formatTime(record, self.datefmt)
        set_nested_val(msg, self.timestamp_key, record.asctime)
        return msg


class MetadataMixin:
    """
    Add timestamp, level, and source to the log message dictionary.

    By default, adds:

    * timestamp to `log_time` key
    * source (record.name) to `log_source` key
    * level to `log_level` key

    You can specifiy a different keys timestamp_key in the constructor to the Formatter:

    For example `MetadataFormatter(timestamp_key='_time', source_key='log.logger', level_key='log.level')` will produce
    log messages like:

    ```
    {
        "_time": "2025-12-16T16:15:40.000Z",
        "log": {
            "logger": "my.module",
            "level": "INFO"
        },
    }
    ```

    Uses standard Python Formatter.formatTime to format the time, per the `datefmt` setting.
    See: https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime for more info

    Question: How do I add more Metadata? For example I want record.lineno in my logfile. How do I add that?

    Simple, make your own formatter. It would look like this:

    ```python
    from jamsuite import logger

    # extend MetadataFormatter to add more metadata
    class MyMetadataFormatter(logger.MetadataFormatter):
        def format(self, record) -> dict:
            msg = super().format(record)
            # add your extra Metadata here
            msg["lineno"] = record.lineno
            return msg

    # Compose your MyJSONFormatter to use your extended Metadata
    class MyJSONFormatter(logger.JSONSerializer, MyMetadataFormatter, logger.ErrorFormatter, logger.DictFormatter):
        pass
    ```

    Then use MyJSONFormatter in your logging config.

    See [LogRecord.attributes documentation](https://docs.python.org/3/library/logging.html#logrecord-attributes)
    for what attributes are available.
    """

    def __init__(self, *args, **kwargs):
        self.timestamp_key = kwargs.pop("timestamp_key", "log_time")
        self.source_key = kwargs.pop("source_key", "log_source")
        self.level_key = kwargs.pop("level_key", "log_level")
        super().__init__(*args, **kwargs)

    def format(self, record) -> dict:
        msg = super().format(record)
        # add timestamp info
        record.asctime = self.formatTime(record, self.datefmt)
        set_nested_val(msg, self.timestamp_key, record.asctime)
        set_nested_val(msg, self.source_key, record.name)
        set_nested_val(msg, self.level_key, record.levelname)
        return msg


try:
    from pydantic import BaseModel as PydanticBaseModel

    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False


class PydanticMixin:
    """
    if any first level value in message is a Pydantic model, serializes it using `model_dump(mode='json')`
    """

    def format(self, record) -> dict:
        if not HAVE_PYDANTIC:
            return super().format(record)

        msg = super().format(record)
        # don't mutate a dict while iterating over it
        msg_keys = list(msg.keys())
        for k in msg_keys:
            v = msg[k]
            if isinstance(v, PydanticBaseModel):
                msg[k] = v.model_dump(mode="json")
        return msg


class SecretMaskMixin:
    """
    Masks secret values in the log message by matching dictionary keys to a regex
    """

    def __init__(self, *args, **kwargs):
        """
        Params:

        - secrets_regex (regex) defaults to look for
          keys that contain the word SECRET, PASSWORD, or KEY, ignoring case
        """
        self.secrets_regex = kwargs.pop("secrets_regex", RE_SENSITIVE_ATTR)
        super().__init__(*args, **kwargs)

    def format(self, record):
        msg = super().format(record)
        redact_secrets(record.msg, regex=self.secrets_regex)
        return msg
