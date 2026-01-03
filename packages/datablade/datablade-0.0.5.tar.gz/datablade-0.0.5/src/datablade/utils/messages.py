"""
Messaging utilities for datablade.

This module provides backward-compatible message functions.
For new code, prefer using datablade.utils.logging directly.
"""

# Re-export from logging module for backward compatibility
from .logging import (
    configure_logging,
    get_logger,
    log,
    log_debug,
    log_error,
    log_info,
    log_warning,
    print_verbose,
)

__all__ = [
    "print_verbose",
    "log",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "get_logger",
    "configure_logging",
]
