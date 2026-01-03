"""
General utility functions for common operations.

This module provides functions for:
- String manipulation and SQL name quoting
- List operations (flattening)
- Logging and messaging
- Path standardization
"""

from .lists import flatten
from .logging import print_verbose  # backward compatibility
from .logging import (
    configure_logging,
    get_logger,
    log,
    log_debug,
    log_error,
    log_info,
    log_warning,
)
from .strings import pathing, sql_quotename

__all__ = [
    "sql_quotename",
    "pathing",
    "flatten",
    # Logging
    "get_logger",
    "configure_logging",
    "log",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "print_verbose",
]
