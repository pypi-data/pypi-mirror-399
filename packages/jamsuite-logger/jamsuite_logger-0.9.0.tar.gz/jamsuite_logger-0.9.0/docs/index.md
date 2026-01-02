# How to Use

## 1. Configure Python Logging

Configure Python Logging to use JamSuite formatter. 

```
import sys
from logging.config import dictConfig

dictConfig({
    "version": 1,
    "formatters": {
        "json": "jamsuite.logger.JSONFormatter",
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
})
```

**TIP:** For DEV environments, try the `jamsuite.logger.ConsoleFormatter` for colorized output and pretty JSON.

## 2. Use regular ol' Python logging in your code

### Log a dictionary for structured output

```
from logging import getLogger

log = getLogger(__name__)

log.info({"message":"Hey Ma, look at me!","user":"Your Kid!"})
```

### Log a single message

```
from logging import getLogger

log = getLogger(__name__)

log.info("I am special")
```

### Log exceptions

Loging `exc_info` will add Exception and Traceback to the log output.

```
from logging import getLogger

log = getLogger(__name__)

try:
    go_to_moon()
except Exception as e:
    log.error({"message":"We had a problem", "where": "Outer Space"}, exc_info: e)
```

You can also just log an exception, and that will also add Exception and Traceback to the log output.

```
from logging import getLogger

log = getLogger(__name__)

try:
    go_to_moon()
except Exception as e:
    log.error(e)
```


### Example Output

```
{
  "log_time": "2025-12-14 10:11:31,177",
  "log_source": "__main__",
  "log_level": "INFO",
  "message": "Hey Ma, look at me!",
  "user": "Your Kid!"
}
```