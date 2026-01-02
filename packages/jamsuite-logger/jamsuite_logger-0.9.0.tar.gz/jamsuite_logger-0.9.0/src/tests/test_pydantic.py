import sys
from logging.config import dictConfig

from pydantic import BaseModel

from jamsuite.logger import get_logger


class A(BaseModel):
    a: str
    b: int
    c: dict[str, "A"]


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

log = get_logger(__name__)
log.info(A(a="Hey", b=3, c={"Foo": A(a="There", b=4, c={})}))
log.info(A(a="Hey", b=3, c={"Foo": A(a="There", b=4, c={})}))
