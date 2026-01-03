"""
Bulk loading utilities for SQL databases.

Provides dialect-aware bulk loading from files to database tables.
Supports SQL Server (BCP), PostgreSQL (COPY), MySQL (LOAD DATA), and DuckDB.
"""

import pathlib
import subprocess
from typing import Optional, Union

import pandas as pd

from ..utils.logging import log_debug, log_error, log_info
from .dialects import Dialect
from .quoting import quote_identifier


def _validate_bulk_load_params(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    server: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    dialect: Dialect = Dialect.SQLSERVER,
) -> pathlib.Path:
    """Validate bulk load parameters and return resolved path."""
    if not file_path:
        raise ValueError("file_path must be provided")

    path_obj = pathlib.Path(file_path)
    if not path_obj.exists():
        raise ValueError(f"File does not exist: {path_obj}")

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name must be a non-empty string")
    if not isinstance(database, str) or not database.strip():
        raise ValueError("database must be a non-empty string")

    if dialect == Dialect.SQLSERVER:
        if not server:
            raise ValueError("server is required for SQL Server")
        if not username:
            raise ValueError("username is required for SQL Server")
        if not password:
            raise ValueError("password is required for SQL Server")

    return path_obj


def bulk_load_sqlserver(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    server: str,
    username: str,
    password: str,
    schema: str = "dbo",
    delimiter: str = ",",
    verbose: bool = False,
) -> None:
    """
    Bulk load a file into SQL Server using BCP.

    Args:
        file_path: Path to the data file.
        table_name: Target table name.
        database: Database name.
        server: SQL Server instance name.
        username: SQL Server username.
        password: SQL Server password.
        schema: Schema name (default: dbo).
        delimiter: Field delimiter (default: comma).
        verbose: If True, logs progress messages.

    Raises:
        ValueError: On invalid inputs.
        subprocess.CalledProcessError: If BCP command fails.
    """
    path_obj = _validate_bulk_load_params(
        file_path, table_name, database, server, username, password, Dialect.SQLSERVER
    )

    qualified_table = f"{database}.{schema}.{table_name}"

    bcp_args = [
        "bcp",
        qualified_table,
        "in",
        str(path_obj),
        "-c",
        f"-t{delimiter}",
        "-S",
        server,
        "-U",
        username,
        "-P",
        password,
    ]

    log_info(f"Executing BCP load to {qualified_table}", verbose)
    log_debug(
        f"BCP args: {bcp_args[:-1] + ['***REDACTED***']}",
        verbose,
    )

    try:
        process = subprocess.run(
            bcp_args,
            shell=False,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log_info(f"Successfully loaded data to {qualified_table}", verbose)
        if process.stdout:
            log_debug(f"BCP output: {process.stdout.decode()}", verbose)
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        log_error(f"BCP load failed: {error_msg}", verbose)
        raise


def bulk_load_postgres(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    schema: str = "public",
    connection_string: Optional[str] = None,
    delimiter: str = ",",
    header: bool = True,
    verbose: bool = False,
) -> str:
    """
    Generate a PostgreSQL COPY command for bulk loading.

    Args:
        file_path: Path to the data file.
        table_name: Target table name.
        database: Database name.
        schema: Schema name (default: public).
        connection_string: Optional psql connection string.
        delimiter: Field delimiter (default: comma).
        header: If True, skip header row.
        verbose: If True, logs progress messages.

    Returns:
        The COPY command as a string.

    Raises:
        ValueError: On invalid inputs.
    """
    path_obj = _validate_bulk_load_params(
        file_path, table_name, database, dialect=Dialect.POSTGRES
    )

    qualified_table = f"{quote_identifier(schema, Dialect.POSTGRES)}.{quote_identifier(table_name, Dialect.POSTGRES)}"

    header_clause = "HEADER" if header else ""
    copy_cmd = (
        f"\\COPY {qualified_table} FROM '{path_obj}' "
        f"WITH (FORMAT csv, DELIMITER '{delimiter}', {header_clause})"
    )

    log_info(f"Generated COPY command for {qualified_table}", verbose)
    return copy_cmd


def bulk_load_mysql(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    delimiter: str = ",",
    enclosed_by: str = '"',
    lines_terminated_by: str = "\\n",
    ignore_lines: int = 1,
    verbose: bool = False,
) -> str:
    """
    Generate a MySQL LOAD DATA command for bulk loading.

    Args:
        file_path: Path to the data file.
        table_name: Target table name.
        database: Database name.
        delimiter: Field delimiter (default: comma).
        enclosed_by: Field enclosure character.
        lines_terminated_by: Line terminator.
        ignore_lines: Number of header lines to skip.
        verbose: If True, logs progress messages.

    Returns:
        The LOAD DATA command as a string.

    Raises:
        ValueError: On invalid inputs.
    """
    path_obj = _validate_bulk_load_params(
        file_path, table_name, database, dialect=Dialect.MYSQL
    )

    qualified_table = f"{quote_identifier(database, Dialect.MYSQL)}.{quote_identifier(table_name, Dialect.MYSQL)}"

    load_cmd = (
        f"LOAD DATA LOCAL INFILE '{path_obj}' "
        f"INTO TABLE {qualified_table} "
        f"FIELDS TERMINATED BY '{delimiter}' "
        f"ENCLOSED BY '{enclosed_by}' "
        f"LINES TERMINATED BY '{lines_terminated_by}' "
        f"IGNORE {ignore_lines} LINES"
    )

    log_info(f"Generated LOAD DATA command for {qualified_table}", verbose)
    return load_cmd


def bulk_load_duckdb(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str = "memory",
    schema: str = "main",
    verbose: bool = False,
) -> str:
    """
    Generate a DuckDB COPY command for bulk loading.

    Args:
        file_path: Path to the data file.
        table_name: Target table name.
        database: Database name (default: memory).
        schema: Schema name (default: main).
        verbose: If True, logs progress messages.

    Returns:
        The COPY command as a string.

    Raises:
        ValueError: On invalid inputs.
    """
    path_obj = _validate_bulk_load_params(
        file_path, table_name, database, dialect=Dialect.DUCKDB
    )

    qualified_table = f"{quote_identifier(schema, Dialect.DUCKDB)}.{quote_identifier(table_name, Dialect.DUCKDB)}"

    # DuckDB can infer format from file extension
    suffix = path_obj.suffix.lower()
    if suffix == ".parquet":
        copy_cmd = f"COPY {qualified_table} FROM '{path_obj}' (FORMAT PARQUET)"
    elif suffix == ".csv":
        copy_cmd = f"COPY {qualified_table} FROM '{path_obj}' (FORMAT CSV, HEADER)"
    else:
        copy_cmd = f"COPY {qualified_table} FROM '{path_obj}'"

    log_info(f"Generated COPY command for {qualified_table}", verbose)
    return copy_cmd


def bulk_load(
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    dialect: Dialect = Dialect.SQLSERVER,
    schema: Optional[str] = None,
    server: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    delimiter: str = ",",
    verbose: bool = False,
) -> Optional[str]:
    """
    Bulk load a file to a database table using the appropriate dialect method.

    Args:
        file_path: Path to the data file.
        table_name: Target table name.
        database: Database name.
        dialect: SQL dialect to use.
        schema: Schema name (dialect-specific default if None).
        server: Server name (required for SQL Server).
        username: Username (required for SQL Server).
        password: Password (required for SQL Server).
        delimiter: Field delimiter.
        verbose: If True, logs progress messages.

    Returns:
        For SQL Server, returns None (executes directly).
        For other dialects, returns the command string.

    Raises:
        ValueError: On invalid inputs.
        NotImplementedError: If dialect is unsupported.
    """
    if dialect == Dialect.SQLSERVER:
        bulk_load_sqlserver(
            file_path=file_path,
            table_name=table_name,
            database=database,
            server=server,  # type: ignore
            username=username,  # type: ignore
            password=password,  # type: ignore
            schema=schema or "dbo",
            delimiter=delimiter,
            verbose=verbose,
        )
        return None

    if dialect == Dialect.POSTGRES:
        return bulk_load_postgres(
            file_path=file_path,
            table_name=table_name,
            database=database,
            schema=schema or "public",
            delimiter=delimiter,
            verbose=verbose,
        )

    if dialect == Dialect.MYSQL:
        return bulk_load_mysql(
            file_path=file_path,
            table_name=table_name,
            database=database,
            delimiter=delimiter,
            verbose=verbose,
        )

    if dialect == Dialect.DUCKDB:
        return bulk_load_duckdb(
            file_path=file_path,
            table_name=table_name,
            database=database,
            schema=schema or "main",
            verbose=verbose,
        )

    raise NotImplementedError(f"Dialect not supported: {dialect}")


def write_dataframe_and_load(
    df: pd.DataFrame,
    file_path: Union[str, pathlib.Path],
    table_name: str,
    database: str,
    dialect: Dialect = Dialect.SQLSERVER,
    schema: Optional[str] = None,
    server: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    delimiter: str = ",",
    verbose: bool = False,
) -> Optional[str]:
    """
    Write a DataFrame to a file and bulk load it to a database.

    Args:
        df: The DataFrame to write.
        file_path: Path where the file will be saved.
        table_name: Target table name.
        database: Database name.
        dialect: SQL dialect to use.
        schema: Schema name.
        server: Server name (required for SQL Server).
        username: Username (required for SQL Server).
        password: Password (required for SQL Server).
        delimiter: Field delimiter.
        verbose: If True, logs progress messages.

    Returns:
        For SQL Server, returns None (executes directly).
        For other dialects, returns the command string.

    Raises:
        TypeError: If df is not a DataFrame.
        ValueError: On invalid inputs.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    path_obj = pathlib.Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Write based on file extension
    suffix = path_obj.suffix.lower()
    if suffix == ".parquet":
        df.to_parquet(path_obj, index=False)
    elif suffix == ".csv":
        df.to_csv(path_obj, index=False, sep=delimiter)
    else:
        df.to_csv(path_obj, index=False, sep=delimiter)

    log_info(f"DataFrame written to {path_obj}", verbose)

    return bulk_load(
        file_path=path_obj,
        table_name=table_name,
        database=database,
        dialect=dialect,
        schema=schema,
        server=server,
        username=username,
        password=password,
        delimiter=delimiter,
        verbose=verbose,
    )
