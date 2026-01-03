"""
SQL utilities for datablade.

Provides dialect-aware quoting, DDL generation, and bulk loading.
Supports SQL Server, PostgreSQL, MySQL, and DuckDB.
"""

from .bulk_load import (
    bulk_load,
    bulk_load_duckdb,
    bulk_load_mysql,
    bulk_load_postgres,
    bulk_load_sqlserver,
    write_dataframe_and_load,
)
from .ddl import generate_create_table
from .ddl_pyarrow import generate_create_table_from_parquet
from .dialects import Dialect
from .quoting import quote_identifier

__all__ = [
    "Dialect",
    "quote_identifier",
    "generate_create_table",
    "generate_create_table_from_parquet",
    "bulk_load",
    "bulk_load_sqlserver",
    "bulk_load_postgres",
    "bulk_load_mysql",
    "bulk_load_duckdb",
    "write_dataframe_and_load",
]
