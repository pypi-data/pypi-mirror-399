# API Documentation

## Formatters 

::: jamsuite.logger
    handler: python
    options:    
      show_source: false
      heading_level: 3
      members:
      - BaseFormatter
      - JSONFormatter
      - ConsoleFormatter
      - ColorFormatter

## Mixins

::: jamsuite.logger
    handler: python
    options:    
      show_source: false
      heading_level: 3
      members:
      - DictMixin
      - ErrorMixin
      - MetadataMixin
      - PydanticMixin
      - TimestampMixin

## Helpers

::: jamsuite.logger
    handler: python
    options:    
      show_source: false
      heading_level: 3
      members:
      - get_log_level
      - get_logger
      - format_exception
      - format_traceback_as_list
      - format_traceback_nopytest
      - format_template_debug
      - format_multiline
      - format_dict
      - set_nested_val
      - redact_secrets