"""
datablade - A suite of functions providing standard syntax across data engineering projects.

The package is organized into four main modules:
- dataframes: DataFrame operations, transformations, and memory-aware file reading
- io: Input/output operations for external data
- utils: General utility functions and logging
- sql: Multi-dialect SQL generation, quoting, and bulk loading

For backward compatibility, all functions are also available from datablade.core.
"""

# Also maintain core for backward compatibility
# Import from new organized structure
from . import core, dataframes, io, sql, utils
from .blade import Blade
from .dataframes import read_file_chunked, read_file_smart, read_file_to_parquets
from .sql import Dialect, bulk_load, generate_create_table

# Convenience re-exports for commonly used functions
from .utils.logging import configure_logging, get_logger

__version__ = "0.0.5"

__all__ = [
    "dataframes",
    "io",
    "utils",
    "sql",
    "core",  # Maintain backward compatibility
    # Convenience re-exports
    "configure_logging",
    "get_logger",
    "read_file_smart",
    "read_file_chunked",
    "read_file_to_parquets",
    "Dialect",
    "generate_create_table",
    "bulk_load",
    "Blade",
]
