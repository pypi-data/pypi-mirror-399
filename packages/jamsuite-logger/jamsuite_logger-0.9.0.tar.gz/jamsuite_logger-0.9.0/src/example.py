import logging
import sys
from logging.config import dictConfig

# configure logging
dictConfig(
    {
        "version": 1,
        "formatters": {
            "json": {"()": "jamsuite.logger.JSONFormatter", "pretty": True},
        },
        "handlers": {
            "json_handler": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "json",
            },
        },
        "loggers": {
            "root": {
                "level": "INFO",
                "handlers": ["json_handler"],
            },
        },
    }
)

# let's log!
log = logging.getLogger(__name__)
log.info({"message": "Hello Mom!", "kid": "charm"})
