import logging

# colors for pretty output!
# https://stackoverflow.com/a/56944256
# also https://chrisyeh96.github.io/2020/03/28/terminal-colors.html
COLOR_GREY = "\x1b[38;20m"
COLOR_GREEN = "\x1b[32;20m"
COLOR_BLUE = "\x1b[94;20m"
COLOR_YELLOW = "\x1b[33;20m"
COLOR_RED = "\x1b[31;20m"
COLOR_BOLD_RED = "\x1b[31;1m"
COLOR_RESET = "\x1b[0m"

LOG_COLORS = {
    logging.DEBUG: COLOR_GREEN,
    logging.INFO: COLOR_BLUE,
    logging.WARNING: COLOR_YELLOW,
    logging.ERROR: COLOR_RED,
    logging.CRITICAL: COLOR_BOLD_RED,
}
