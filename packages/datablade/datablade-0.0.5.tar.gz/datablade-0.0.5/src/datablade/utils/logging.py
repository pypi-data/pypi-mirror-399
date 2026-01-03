"""
Logging utilities for datablade.

Provides a configurable logger that can be used across all modules.
By default, logs to console at INFO level. Users can configure
handlers, levels, and formatters as needed.
"""

import logging
import pathlib
from typing import Any, Optional

# Create the datablade logger
_logger = logging.getLogger("datablade")
_logger.setLevel(logging.DEBUG)  # Allow all levels; handlers control output

# Default console handler (can be replaced by user)
_default_handler: Optional[logging.Handler] = None


def _ensure_handler() -> None:
    """Ensure at least one handler is configured."""
    global _default_handler
    if not _logger.handlers and _default_handler is None:
        _default_handler = logging.StreamHandler()
        _default_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        _default_handler.setFormatter(formatter)
        _logger.addHandler(_default_handler)


def get_logger() -> logging.Logger:
    """
    Get the datablade logger instance.

    Returns:
        The configured datablade logger.
    """
    _ensure_handler()
    return _logger


def configure_logging(
    level: int = logging.INFO,
    handler: Optional[logging.Handler] = None,
    format_string: Optional[str] = None,
    *,
    log_file: Optional[str | pathlib.Path] = None,
    format: Optional[str] = None,
) -> logging.Logger:
    """
    Configure the datablade logger.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO).
        handler: Optional custom handler. If None, uses StreamHandler.
        format_string: Optional format string for log messages.

    Returns:
        The configured logger instance.
    """
    global _default_handler

    if format is not None:
        if format_string is not None:
            raise ValueError("Provide only one of format_string or format")
        format_string = format

    # Remove existing handlers
    for h in _logger.handlers[:]:
        _logger.removeHandler(h)
    _default_handler = None

    # Add new handler
    if handler is None:
        if log_file is not None:
            log_path = pathlib.Path(log_file)
            if log_path.parent:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_path, encoding="utf-8")
        else:
            handler = logging.StreamHandler()

    handler.setLevel(level)

    if format_string:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    handler.setFormatter(formatter)

    _logger.addHandler(handler)
    _default_handler = handler

    return _logger


def log(
    message: Any,
    level: int = logging.INFO,
    verbose: bool = True,
) -> None:
    """
    Log a message at the specified level if verbose is True.

    Args:
        message: The message to log (converted to string).
        level: Logging level (default: INFO).
        verbose: If False, message is not logged.

    Returns:
        None
    """
    if not verbose:
        return

    _ensure_handler()
    _logger.log(level, str(message))


def log_debug(message: Any, verbose: bool = True) -> None:
    """Log a DEBUG level message."""
    log(message, logging.DEBUG, verbose)


def log_info(message: Any, verbose: bool = True) -> None:
    """Log an INFO level message."""
    log(message, logging.INFO, verbose)


def log_warning(message: Any, verbose: bool = True) -> None:
    """Log a WARNING level message."""
    log(message, logging.WARNING, verbose)


def log_error(message: Any, verbose: bool = True) -> None:
    """Log an ERROR level message."""
    log(message, logging.ERROR, verbose)


# Backward compatibility alias
def print_verbose(message: Any, verbose: bool = True) -> None:
    """
    Print a message if verbose is True.

    This is a backward-compatible alias for log_info.

    Args:
        message: The message to print (converted to string).
        verbose: If True, the message will be logged.

    Returns:
        None
    """
    log_info(message, verbose)
