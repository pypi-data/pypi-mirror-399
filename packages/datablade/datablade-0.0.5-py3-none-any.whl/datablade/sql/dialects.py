from enum import Enum


class Dialect(str, Enum):
    """Supported SQL dialects for datablade DDL helpers."""

    SQLSERVER = "sqlserver"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    DUCKDB = "duckdb"
