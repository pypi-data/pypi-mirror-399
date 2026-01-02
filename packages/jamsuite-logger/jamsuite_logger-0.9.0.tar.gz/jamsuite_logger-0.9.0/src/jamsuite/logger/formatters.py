import logging

from . import colors
from .mixins import DictMixin, ErrorMixin, MetadataMixin, PydanticMixin
from .serializers import JSONSerializer


class ColorFormatter(logging.Formatter):
    """
    Logging formatter supporting colorized output to the console

    You can customize the colors by setting `color_codes` in the Formatter constructor
    mapping log levels to ASCII color characters

    Note color codes include the ASCII control characters.
    See https://jafrog.com/2013/11/23/colors-in-terminal.html for more info.

    ```
    import logging

    ColorFormatter(color_codes={
        logging.DEBUG: '\x1b[32;3m',
        logging.INFO: '\x1b[34m',
        logging.WARNING: '\x1b[33;3m',
        logging.ERROR: '\x1b[31;1m',
        logging.CRITICAL: '\x1b[31;3m',
    })
    ```

    You can also change the ASCII reset character if you need to through the "reset_code" kwarg.
    """

    def __init__(self, *args, **kwargs):
        self.COLOR_CODES = kwargs.pop("color_codes", colors.LOG_COLORS)
        self.RESET_CODE = kwargs.pop("reset_code", colors.COLOR_RESET)
        super().__init__(*args, **kwargs)

    def format(self, record):
        if record.levelno in self.COLOR_CODES:
            record.color_on = self.COLOR_CODES[record.levelno]
            record.color_off = self.RESET_CODE
            return f"{record.color_on}{super().format(record)}{record.color_off}"
        return super().format(record)


class BaseFormatter(MetadataMixin, ErrorMixin, DictMixin, logging.Formatter):
    """
    Formats message as Dict and adds any error info (via DictFormatter and ErrorFormatter)

    Question: What if I want to customize how errors are added?

    Then you should extend ErrorFormatter (or make your own!) and build a new BaseFormatter
    for your use case.

    ex.
    ```
    class MyBaseFormatter(MetadataFormatter, MyErrorFormatter, DictFormatter):
        pass
    ```
    """

    pass


class JSONFormatter(JSONSerializer, PydanticMixin, BaseFormatter):
    pass


class ConsoleFormatter(ColorFormatter, JSONFormatter):
    """
    Logging formatter supporting colorized output and pretty JSON for the console
    """

    def __init__(self, *args, pretty=True, **kwargs):
        super().__init__(*args, pretty=pretty, **kwargs)
