# Composable Structured Logging for Python

## Overview 

Composability is achieved by mixing-in JamSuite Logger's formatters. The first formatter in the chain being a serializer which converts the dictionary to a formatted string. All other formatters that follow treat LogRecord message as a dictionary, adding data fields to it. 

Example:

```
class JSONFormatter(JSONSerializer, MetadataMixin, BaseFormatter):
    ...
```

## Architecture Goals

* Keep it simple
* Each mixin functionality is tested independently.
* Build on-top of standard Python logging facilities
* Composable: Be able to remix/add functionality to customize your own logger.
* Extensible: Be able to extend the classes to easily add or alter its functionality.
* Functional: Main logic available in functions for easy reuse.
* Encourage the user to make their own formatter (it's easy!) rather than trying to cover all cases in the main library.
* Well tested and in production use

## Serialization Types

* Support JSON only for now
* Support common JSON structures for logging (ex. ELK/[Elastic Common Schema (ECS)](https://www.elastic.co/docs/reference/ecs), Grafana/Loki, VictoriaMetrics, NetData, etc.)
* Consider other serializers in the future (ex. [logfmt](https://brandur.org/logfmt) (_is there a defined standard for logmft?_))

## Out of Scope

* Schema enforced logging (ex. to serialize to Avro)
* Trying to be the fastest logger in the land
* Trying to become the defacto solution 

## Relevant Docs

Shortcuts from Python Logging documentation:

* [Logger.debug()](https://docs.python.org/3/library/logging.html#logging.Logger.debug)
* [Formatter Objects](https://docs.python.org/3/library/logging.html#formatter-objects)
* [LogRecord Objects](https://docs.python.org/3/library/logging.html#logrecord-objects)
* [LogRecord Attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes)

Logging standards:

* [Elastic Common Schema: Field Reference](https://www.elastic.co/docs/reference/ecs/ecs-field-reference)
* [OpenTelemetry: General logs attributes](https://opentelemetry.io/docs/specs/semconv/general/logs/)
* [VictoriaLogs: Key Concepts](https://docs.victoriametrics.com/victorialogs/keyconcepts/)

## Alternatives

* `python-json-logger` ([Pypi](https://pypi.org/project/python-json-logger/), [GitHub](https://github.com/nhairs/python-json-logger), [Docs](https://nhairs.github.io/python-json-logger/latest/)) - the OG of JSON logging. Looks great and is well supported but everything is built off of one BaseJsonFormatter, relying on configuration over composability.
* `loguru` ([Pypi](https://pypi.org/project/loguru/), [GitHub](https://github.com/Delgan/loguru), [Docs](https://loguru.readthedocs.io/en/stable/)) - Looks cool, but does not rely on standard logging internally.
* `structlog` ([Pypi](https://pypi.org/project/structlog/), [GitHub](https://github.com/hynek), [Docs](https://www.structlog.org/en/stable/)) - Mature, forward thinking project with great ecosystem and support. However, event though the system integrates well with Python logging, the main interface is through structlog. Note the stdlib.py file alone is 1200 lines, more than the entirety of JamSuite Logger.