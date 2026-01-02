"""Logging for A package with level-specific, contex aware messages.

- Use `XUTK_LOG_LEVEL` environment variable to set logging level
  level: One of 'DEBUG', 'INFO', 'ARNING', 'ERROR'
  - Alternatively, use function `set_log_level()`
- Use `CtxLogger` to initialize specific logger
"""

import colorama
import logging
import os
import sys
from typing import Dict, Any


class _ColorfulFormatter(logging.Formatter):
    """A custom logging formatter that adds color to log messages.

    This formatter uses colorama to add ANSI color codes to log messages
    based on their severity level, making them easier to distinguish
    in terminal output.
    """

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format the message part of the log record with color.

        This method is called by the parent format() method and only
        adds color to the levelname while preserving all other standard
        formatting behavior.

        Args:
            record: The log record to format

        Returns:
            A formatted string with colored level name
        """
        # Color mapping for log levels
        log_colors = {
            "NOTSET": colorama.Fore.WHITE,
            "DEBUG": colorama.Fore.CYAN,
            "INFO": colorama.Fore.GREEN,
            "WARNING": colorama.Fore.YELLOW + colorama.Style.BRIGHT,
            "ERROR": colorama.Fore.RED + colorama.Style.BRIGHT,
            "CRITICAL": colorama.Fore.RED + colorama.Style.BRIGHT,
        }

        # Passing colored levelname to parent's formatMessage
        original_levelname = record.levelname
        record.levelname = (
            f"{log_colors.get(original_levelname, '')}"
            + f"{original_levelname}{colorama.Style.RESET_ALL}"
        )
        try:
            # Use parent's formatMessage to handle the actual formatting
            result = super().formatMessage(record)
        finally:
            # Restore original levelname
            record.levelname = original_levelname

        return result


class CtxLogger:
    """Logger with built-in context formatting and level methods."""

    caller_names: set[str]
    _logger: logging.Logger
    _color_flag: bool

    def __init__(self, name: str = "xutk") -> None:
        """Initialize the CtxLogger with basic configuration.

        Args:
            name: Logger name (defaults to 'xutk'). Creates a new logger or returns
                  existing one if name matches.

        Configures logging level from XUTK_LOG_LEVEL (PKG_LOG_LEVEL)
        environment variable or set_log_level() (defaults to INFO)
        and sets up a basic console handler with standard formatting.

        Also override color output setting by environment variable
        XUTK_LOG_COLOR (PKG_LOG_COLOR), True (true) or False (false).
        """
        self._logger = logging.getLogger(name)
        self.caller_names = {"caller", "plotter", "loader", "processor"}
        self._init_handler_and_color(name)

    def _init_handler_and_color(self, name: str) -> None:
        color_opt = os.getenv(name.upper() + "_LOG_COLOR", "auto").lower()
        color_flag = False
        if "auto" == color_opt:
            color_flag = sys.stdout.isatty()
        elif color_opt in {"true", "1", "yes", "y"}:
            color_flag = True
        if color_flag:
            colorama.init()
        self._color_flag = color_flag

        if not self._logger.handlers:
            # Set level from environment or default to INFO
            logger_level = name.upper() + "_LOG_LEVEL"
            level = os.getenv(logger_level, "INFO").upper()
            self._logger.setLevel(getattr(logging, level, logging.INFO))

            handler = logging.StreamHandler()
            formatter = (
                _ColorfulFormatter(
                    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
                )
                if self._color_flag
                else logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
                )
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _log_with_context(
        self, level: int, context: Dict[str, Any], message: str
    ) -> None:
        """Add to log internally."""
        callers = [(k, v) for k, v in context.items() if k in self.caller_names]
        caller_str = ""
        try:
            caller_str = callers[0][1]
        except IndexError:
            pass

        if self._color_flag:
            message = (
                str(colorama.Style.BRIGHT) + message + str(colorama.Style.RESET_ALL)
            )

        ctx_items = [
            f"{k}: {v}" for k, v in context.items() if k not in self.caller_names
        ]
        ctx_str = "; ".join(ctx_items)

        self._logger.log(
            level,
            f"{caller_str}: {message}"
            + f"{' | ' if len(ctx_str) > 0 else ''}{ctx_str}",
        )

    def debug(self, context: Dict[str, Any], message: str) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, context, message)

    def info(self, context: Dict[str, Any], message: str) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, context, message)

    def warning(self, context: Dict[str, Any], message: str) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, context, message)

    def error(self, context: Dict[str, Any], message: str) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, context, message)

    def get_log_level(self) -> int:
        """Get log level (number)."""
        return self._logger.getEffectiveLevel()


def set_log_level(level: str, logger_name: str = "xutk") -> None:
    """Set log level programmatically.

    Args:
        level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR'
               (Neither 'NOTSET' nor 'CRITICAL' are provided)
        logger_name: Name of the logger to configure (defaults to 'xutk')
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
