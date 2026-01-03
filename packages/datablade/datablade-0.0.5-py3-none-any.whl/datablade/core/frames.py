"""Backward-compatibility re-exports.

This module intentionally contains no independent implementations.
All functionality is provided by the newer modules in datablade.dataframes.
"""

from ..dataframes.frames import (  # noqa: F401
    clean_dataframe_columns,
    generate_parquet_schema,
    generate_sql_server_create_table_string,
    pandas_to_parquet_table,
    try_cast_string_columns_to_numeric,
    write_to_file_and_sql,
)

__all__ = [
    "try_cast_string_columns_to_numeric",
    "clean_dataframe_columns",
    "generate_parquet_schema",
    "pandas_to_parquet_table",
    "generate_sql_server_create_table_string",
    "write_to_file_and_sql",
]
