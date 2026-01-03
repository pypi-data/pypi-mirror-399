"""
DataFrame operations and utilities for data transformation.

This module provides functions for:
- DataFrame column cleaning and type conversion
- Parquet schema generation and conversion
- SQL Server schema generation
- Memory-aware file reading with optional Polars support
- Chunked file reading for large files
- Partitioned Parquet writing
"""

from .frames import (
    clean_dataframe_columns,
    generate_parquet_schema,
    generate_sql_server_create_table_string,
    pandas_to_parquet_table,
    try_cast_string_columns_to_numeric,
    write_to_file_and_sql,
)
from .readers import (
    read_file_chunked,
    read_file_iter,
    read_file_smart,
    read_file_to_parquets,
    stream_to_parquets,
)

__all__ = [
    # DataFrame operations
    "try_cast_string_columns_to_numeric",
    "clean_dataframe_columns",
    "generate_parquet_schema",
    "pandas_to_parquet_table",
    "generate_sql_server_create_table_string",
    "write_to_file_and_sql",
    # Memory-aware readers
    "read_file_chunked",
    "read_file_iter",
    "read_file_to_parquets",
    "stream_to_parquets",
    "read_file_smart",
]
