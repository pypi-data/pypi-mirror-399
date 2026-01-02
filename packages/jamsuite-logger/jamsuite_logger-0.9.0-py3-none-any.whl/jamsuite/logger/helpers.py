import logging
import os
import re
import traceback
from collections.abc import MutableMapping
from pathlib import Path

###
#
#   Convenience Funcs
#
###


def get_log_level(level: str | int) -> int:
    """
    set a log level either by number (ex. logging.WARNING) or string (ex. "DEBUG")

    raises ValueError if string value not found in logging.getLevelNamesMapping()
    """
    if isinstance(level, str):
        # convert str to int
        level_arg = level
        if not (level := logging.getLevelNamesMapping().get(level_arg)):
            raise ValueError(f"No log level found for {level_arg!r}")
    return level


def get_logger(name):
    """
    wrapper for logging.getLogger

    Usage:

        ```
        from jamsuite.logger import get_logger
        logger = get_logger(__name__)
        ```
    """
    return logging.getLogger(name)


def format_exception(e):
    """
    Given an exception, or tuple from exc_info, returns a string representation

    If the string representation is multiple lines, returns each line in a list
    """
    # if e is a tuple from exc_info, grab the exception
    # see https://docs.python.org/3/library/sys.html#sys.exc_info

    if isinstance(e, tuple):
        e = e[1]

    # stree = f"{type(e).__name__}({str(e)})"
    # convert exception to string, split into individual lines, remove empty lines
    lines = list(filter(None, str(e).split("\n")))

    # if only one line, return it as string
    if len(lines) == 1:
        return f"{type(e).__name__}({lines[0]})"
    return [type(e).__name__] + lines


# keep this as str instead of PosixPath for format_traceback_as_list()
SRCROOT = os.getenv("SRCROOT", str(Path.cwd()))


def format_traceback_as_list(e=None, filters=None, skip=0) -> list[str]:
    """
    returns a formatted traceback

    - remove leading path from filename for brevity
    - strip extra whitespace from the _original_line

    Args:
        e - an exception, or tuple from exc_info
        filters - any lines that start with these will be removed
        skip - don't include last ## lines
    """
    l = []  # noqa: E741
    if e:
        stack = traceback.extract_tb(e[2] if isinstance(e, tuple) else e.__traceback__)
    else:
        # don't include the call to format_traceback_as_list()
        skip = skip + 1
        stack = traceback.extract_stack()

    for frame_summary in stack:
        filename = frame_summary.filename
        # make filename more concise
        site_packages = filename.find("site-packages")
        if site_packages >= 0:
            # remove everything before site-packages, if present
            filename = filename[site_packages + 14 :]
        elif filename.startswith(SRCROOT):
            # remove everything through src folder
            filename = filename[len(SRCROOT) + 1 :]
        if filters and any(filename.startswith(f) for f in filters):
            continue
        original_lines = getattr(frame_summary, "_original_lines", getattr(frame_summary, "_original_line", ""))
        l.append(f"{filename} line {frame_summary.lineno} in {frame_summary.name}: {original_lines.strip()}")
    return l[:-skip] if skip else l


def format_traceback_nopytest(e=None, filters=["pytest", "_pytest", "pluggy"]):
    """filters out pytest from traceback"""
    return format_traceback_as_list(e=e, filters=filters, skip=1)


def format_template_debug(d):
    """
    Given a template_debug dict (d) from Jinja TemplateError, returns

    - remove leading path from filename for brevity
    - strip extra whitespace from the _original_line
    """
    return f"{d['name'][len(SRCROOT) + 1 :]} line {d['line']} in {d['during'].strip()}"


def format_multiline(s: str) -> str | list[str]:
    """
    splits multi-line string into a list of strings
    if string is not multiline, returns string as-is
    """
    m = s.split("\n")
    return m[0] if len(m) == 1 else m


def format_dict(record: logging.LogRecord, message_key="message") -> dict:
    """
    Formats log message as dict
    and sets the message to record.message
    also returning the message

    Formatting logic:
        + if record.msg is empty, sets empty dict {}
        + if record.msg is already a MutableMapping, sets it as-is
        + otherwise embeds record.message as "message" in the dict
        + If msg is a multiline string, converts it to a list

    Does not do anything with exceptions or timestamps
    """
    try:
        # if we already have record.message as dict return it
        if record.message and isinstance(record.message, MutableMapping):
            return record.message
    except AttributeError:
        pass

    # empty message return empty dict
    if not record.msg:
        m = {}

    # if message is already a MutableMapping (dict), return it
    if isinstance(record.msg, MutableMapping):
        m = record.msg
    else:
        # embed string message in dict, break multiline string into list
        m = {message_key: format_multiline(record.getMessage())}

    # TODO: Handle extra and defaults

    # keep the formatted message in the LogRecord
    record.message = m
    return m


def set_nested_val(d, path, value, delimiter="."):
    """
    Sets a value in a nested dictionary using a dot-separated string path.
    """
    keys = path.split(delimiter)

    # Iterate over all keys except the last one
    for key in keys[:-1]:
        # specific check to ensure we don't try to treat a non-dict as a dict
        # if an intermediate key exists but isn't a dict, we overwrite it
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]

    # Set the value for the last key
    d[keys[-1]] = value


RE_URL_WITH_PASSWORD = re.compile(r'("[^"]*//[^/"]*@)([^:/"]*)([^"]*")')
RE_SENSITIVE_ATTR = re.compile(r"SECRET|PASSWORD|KEY", re.IGNORECASE)


def redact_secrets(d: MutableMapping, _level=1, regex=RE_SENSITIVE_ATTR, max_depth=1):
    """
    recurse through `d` up to `MAX_DEPTH` levels deep and replace
    values w/ "********" for any keys which match regex

    arguments:
    - `d` - log message dictionary

    kwarg params:
     - `regex` - regex to match against dictionary keys.
       (default=`RE_SENSITIVE_ATTR`, keys that contain the word SECRET, PASSWORD, or KEY, ignoring case)
     - `max_depth` how many levels to traverse the logging dictionary
    """
    if _level > max_depth:
        return
    for k, v in d.items():
        if RE_SENSITIVE_ATTR.match(k):
            d[k] = "********"
        elif isinstance(v, MutableMapping):
            redact_secrets(d, _level + 1, regex=regex, max_depth=max_depth)
