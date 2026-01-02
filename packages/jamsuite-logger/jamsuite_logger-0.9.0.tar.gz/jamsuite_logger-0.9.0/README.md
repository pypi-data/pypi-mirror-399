# JamSuite Logger

```
                                                 
                                                 
   ██  ▄▄▄  ▄▄   ▄▄ ▄█████ ▄▄ ▄▄ ▄▄ ▄▄▄▄▄▄ ▄▄▄▄▄ 
   ██ ██▀██ ██▀▄▀██ ▀▀▀▄▄▄ ██ ██ ██   ██   ██▄▄  
████▀ ██▀██ ██   ██ █████▀ ▀███▀ ██   ██   ██▄▄▄ 
                          .                  
                          |    _  _  _  _ ._.
                          |___(_)(_](_](/,[  
                                 ._|._|                              
```
<!-- 

https://patorjk.com/software/taag/#p=display&f=ANSI%20Compact&t=JamSuite&x=none 
https://patorjk.com/software/taag/#p=display&f=Contessa&t=Logger&x=none

-->

Structured JSON Logging for Python



# Logging convention

JamSuite Logger provides a JSONFormatter that converts the log message to JSON. If the message is a simple string, it gets set as the `message` attribute inside the log message. 

## Standard attributes

JamSuite's JSONFormatter will add attributes that start with the `log_` prefix to each message including the timestamp, source file, and level.

## String messages logged as JSON

```python
>>> log.info("just log a string")
{
  "log_time": "2025-12-14 10:13:33,989",
  "log_source": "__main__",
  "log_level": "INFO",
  "message": "just log a string"
}
```

## Dictionaries logged as JSON

Most commonly, you'll use dictionaries to represent the log message.

```python
>>> log.info({"message":"Hey Ma, look at me!","user":"Your Kid!"})
{
  "log_time": "2025-12-14 10:11:31,177",
  "log_source": "__main__",
  "log_level": "INFO",
  "message": "Hey Ma, look at me!",
  "user": "Your Kid!"
}
```

## Exception Logging

If you put an exception inside the message its message will get added to the JSON log message.

```python
>>> e = Exception("woah there!")
>>> log.info(e)
{
  "log_time": "2025-12-14 10:15:38,324",
  "log_source": "__main__",
  "log_level": "INFO",
  "message": "woah there!"
}
```

To capture exception information, set exc_info kwarg as you would in Python logging.

```python
>>> try:
...     raise(Exception("woah there!"))
... except Exception as e:
...     log.error("Caught exception in try block", exc_info=e)
... 
{
  "log_time": "2025-12-14 10:18:06,249",
  "log_source": "__main__",
  "log_level": "ERROR",
  "message": "Caught exception in try block",
  "log_exception": "Exception(woah there!)",
  "log_traceback": [
    "<stdin> line 2 in <module>: "
  ]
}
```

