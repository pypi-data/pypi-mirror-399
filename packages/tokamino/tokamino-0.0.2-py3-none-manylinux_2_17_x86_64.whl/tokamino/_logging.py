"""
Logging configuration for tokamino.

By default, tokamino is silent (no log output). Enable logging with:

    >>> import tokamino
    >>> tokamino.setup_logging("DEBUG")

Or via environment variable:

    $ TOKAMINO_LOG=DEBUG python script.py

Log Levels
----------
- DEBUG: Detailed internal state, method calls, timing
- INFO: Model loading, significant operations
- WARNING: Deprecated features, fallback behavior
- ERROR: Failures that are caught and handled
"""

import logging
import os

# Create the library root logger
logger = logging.getLogger("tokamino")
logger.addHandler(logging.NullHandler())  # Silent by default


def setup_logging(
    level: str | int = "INFO",
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%H:%M:%S",
) -> None:
    """
    Enable tokamino logging.

    Call this to see log output from tokamino. By default, the library
    is silent and produces no log messages.

    Args:
        level: Log level - "DEBUG", "INFO", "WARNING", "ERROR", or a
            logging constant like logging.DEBUG. Default is "INFO".

        format: Log message format. Default includes timestamp, level,
            logger name, and message.

        datefmt: Timestamp format. Default is "HH:MM:SS".

    Example:
        >>> import tokamino

        >>> # Enable INFO level logging
        >>> tokamino.setup_logging()

        >>> # Enable DEBUG for detailed output
        >>> tokamino.setup_logging("DEBUG")

        >>> # Custom format
        >>> tokamino.setup_logging("DEBUG", format="%(levelname)s: %(message)s")
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Remove NullHandler if present
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.NullHandler):
            logger.removeHandler(handler)

    # Add stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format, datefmt=datefmt))
    logger.addHandler(handler)
    logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a tokamino module.

    This is a convenience function for internal use. It returns a child
    logger under the "tokamino" namespace.

    Args:
        name: Module name, typically __name__.

    Returns:
        A logger instance.
    """
    return logging.getLogger(name)


# Auto-enable logging via environment variable
_env_level = os.environ.get("TOKAMINO_LOG")
if _env_level:
    setup_logging(_env_level)
