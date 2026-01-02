# Configuration

You can pass configuration options in your Python logging config using a dictionary like so:

```
...
    "formatters": {
        "json": {"()":"jamsuite.logger.JSONFormatter", "pretty": True},
    },
...
```

## Timestamp & Metadata Configuration

|Attribute|Default|Note(s)|
|---------|-------|-------|
|timestamp_key|log_time|LogRecord `record.asctime`|
|source_key|log_source|LogRecord `record.name`|
|level_key|log_level|LogRecord `record.levelname`|

For example `JSONFormatter(timestamp_key='_time', source_key='log.logger', level_key='log.level')` will produce
log messages like:

```
{
    "_time": "2025-12-15T16:15:40.000Z",
    "log": {
        "logger": "my.module",
        "level": "INFO"
    },
}
```

Uses standard Python Formatter.formatTime to format the time, per the `datefmt` setting.
See: [https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime](https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime) for more info

## Error Configuration

|Attribute|Default|Note(s)|
|---------|-------|-------|
|


