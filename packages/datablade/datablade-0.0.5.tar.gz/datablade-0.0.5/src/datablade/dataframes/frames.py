import pathlib
import subprocess
from typing import Any, Optional

import numpy as np
import pandas as pd
import pyarrow as pa

from ..utils.logging import log_debug, log_error, log_info, log_warning

_BYTES_LIKE_TYPES = (bytes, bytearray, memoryview)


def _is_bytes_like(value: Any) -> bool:
    return isinstance(value, _BYTES_LIKE_TYPES)


def _infer_object_pa_type(col_data: pd.Series) -> pa.DataType:
    non_null = col_data.dropna()
    if non_null.empty:
        return pa.string()

    sample = non_null.iloc[:100].tolist()

    if all(_is_bytes_like(v) for v in sample):
        return pa.binary()
    if all(isinstance(v, str) for v in sample):
        return pa.string()
    if all(isinstance(v, (bool, np.bool_)) for v in sample):
        return pa.bool_()
    if all(
        isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_))
        for v in sample
    ):
        min_value = min(sample)
        max_value = max(sample)
        if min_value >= np.iinfo(np.int8).min and max_value <= np.iinfo(np.int8).max:
            return pa.int8()
        if min_value >= np.iinfo(np.int16).min and max_value <= np.iinfo(np.int16).max:
            return pa.int16()
        if min_value >= np.iinfo(np.int32).min and max_value <= np.iinfo(np.int32).max:
            return pa.int32()
        return pa.int64()
    if all(isinstance(v, (float, np.floating)) for v in sample):
        return pa.float64()

    try:
        inferred = pa.infer_type(sample)
        if pa.types.is_binary(inferred) or pa.types.is_large_binary(inferred):
            return pa.binary()
        if pa.types.is_string(inferred) or pa.types.is_large_string(inferred):
            return pa.string()
        if pa.types.is_boolean(inferred):
            return pa.bool_()
        if pa.types.is_integer(inferred):
            return pa.int64()
        if pa.types.is_floating(inferred):
            return pa.float64()
        if pa.types.is_timestamp(inferred) or pa.types.is_date(inferred):
            return inferred
    except Exception:
        pass

    return pa.string()


def try_cast_string_columns_to_numeric(
    df: Optional[pd.DataFrame] = None,
    convert_partial: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Attempt to cast DataFrame string columns to numeric values where possible.

    Args:
        df: The DataFrame to process. If None, returns None.
        convert_partial: If True, columns with some values convertible to numeric types
            will be converted to numeric types with NaNs where conversion failed.
            If False, only columns where all values can be converted will be converted.
        verbose: If True, prints progress messages.

    Returns:
        DataFrame with string columns converted to numeric types where possible,
        or None if no DataFrame is provided.
    """
    if df is None:
        log_warning(
            "No DataFrame provided; exiting try_cast_string_columns_to_numeric.",
            verbose,
        )
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    for col in df.columns:
        if df[col].dtype == "object":
            non_null = df[col].dropna()
            if not non_null.empty and non_null.iloc[:100].map(_is_bytes_like).any():
                log_debug(
                    f"Column '{col}' contains bytes-like values; skipping numeric coercion.",
                    verbose,
                )
                continue
            converted = pd.to_numeric(df[col], errors="coerce")
            has_nan = converted.isnull().any()
            if not has_nan:
                df[col] = converted
                log_info(f"Column '{col}' successfully converted to numeric.", verbose)
            else:
                if convert_partial:
                    df[col] = converted
                    log_info(
                        f"Column '{col}' partially converted to numeric with NaNs where conversion failed.",
                        verbose,
                    )
                else:
                    log_debug(
                        f"Column '{col}' could not be fully converted to numeric; leaving as is.",
                        verbose,
                    )
    return df


def clean_dataframe_columns(
    df: Optional[pd.DataFrame] = None, verbose: bool = False
) -> pd.DataFrame:
    """
    Clean the DataFrame columns by flattening MultiIndex, converting to strings,
    and removing duplicates.

    Args:
        df: The DataFrame to clean. If None, returns None.
        verbose: If True, prints progress messages.

    Returns:
        The cleaned DataFrame with:
        - Flattened MultiIndex columns
        - String column names
        - Duplicate columns removed (keeping first occurrence)
        Returns None if no DataFrame is provided.
    """
    if df is None:
        log_warning("No DataFrame provided; exiting clean_dataframe_columns.", verbose)
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    # Step 1: Flatten MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(map(str, col)).strip() for col in df.columns.values]
        log_info("Flattened MultiIndex columns.", verbose)

    # Step 2: Convert non-string column names to strings
    df.columns = df.columns.map(str)
    log_debug("Converted column names to strings.", verbose)

    # Step 3: Remove duplicate columns, keeping the first occurrence
    duplicates = df.columns.duplicated()
    if duplicates.any():
        duplicate_cols = df.columns[duplicates]
        log_warning(f"Duplicate columns found: {list(duplicate_cols)}", verbose)
        df = df.loc[:, ~duplicates]
        log_info("Removed duplicate columns, keeping the first occurrence.", verbose)

    return df


def generate_parquet_schema(
    df: Optional[pd.DataFrame] = None, verbose: bool = False
) -> pa.Schema:
    """
    Generate a PyArrow Schema from a pandas DataFrame with optimized data types.

    Args:
        df: The DataFrame to generate the schema from. If None, returns None.
        verbose: If True, prints progress messages.

    Returns:
        PyArrow Schema object with optimized types (smallest integer type that fits the data),
        or None if no DataFrame is provided.
    """
    if df is None:
        log_warning("No DataFrame provided; exiting generate_parquet_schema.", verbose)
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    fields = []
    for column in df.columns:
        col_data = df[column]
        col_name = column
        dtype = col_data.dtype

        # Determine if the column contains any nulls
        nullable = col_data.isnull().any()

        # Map pandas dtype to PyArrow type
        pa_type = None

        if pd.api.types.is_integer_dtype(dtype):
            # Check the range to determine the smallest integer type
            non_null = col_data.dropna()
            if non_null.empty:
                pa_type = pa.int64()
            else:
                min_value = non_null.min()
                max_value = non_null.max()
                if (
                    min_value >= np.iinfo(np.int8).min
                    and max_value <= np.iinfo(np.int8).max
                ):
                    pa_type = pa.int8()
                elif (
                    min_value >= np.iinfo(np.int16).min
                    and max_value <= np.iinfo(np.int16).max
                ):
                    pa_type = pa.int16()
                elif (
                    min_value >= np.iinfo(np.int32).min
                    and max_value <= np.iinfo(np.int32).max
                ):
                    pa_type = pa.int32()
                else:
                    pa_type = pa.int64()

        elif pd.api.types.is_float_dtype(dtype):
            pa_type = pa.float64()

        elif pd.api.types.is_bool_dtype(dtype):
            pa_type = pa.bool_()

        elif isinstance(dtype, pd.DatetimeTZDtype):
            tz = getattr(getattr(col_data.dt, "tz", None), "zone", None) or str(
                col_data.dt.tz
            )
            pa_type = pa.timestamp("ms", tz=tz)

        elif pd.api.types.is_datetime64_any_dtype(dtype):
            pa_type = pa.timestamp("ms")

        elif pd.api.types.is_timedelta64_dtype(dtype):
            pa_type = pa.duration("ns")

        elif isinstance(dtype, pd.CategoricalDtype):
            pa_type = pa.string()

        elif pd.api.types.is_object_dtype(dtype):
            pa_type = _infer_object_pa_type(col_data)

        else:
            pa_type = pa.string()

        # Create a field
        field = pa.field(col_name, pa_type, nullable=nullable)
        fields.append(field)

    schema = pa.schema(fields)
    return schema


def pandas_to_parquet_table(
    df: Optional[pd.DataFrame] = None,
    convert: bool = True,
    partial: bool = False,
    preserve_index: bool = False,
    verbose: bool = False,
) -> pa.Table:
    """
    Generate a PyArrow Table from a pandas DataFrame with automatic type conversion.

    Args:
        df: The DataFrame to convert. If None, returns None.
        convert: If True, attempts to cast string columns to numeric types.
        partial: If True with convert, allows partial conversion with NaNs.
        preserve_index: If True, preserves the DataFrame index in the table.
        verbose: If True, prints progress messages.

    Returns:
        PyArrow Table object with optimized schema, or None if DataFrame is None
        or conversion fails.
    """
    if df is None:
        log_warning("No DataFrame provided; exiting pandas_to_parquet_table.", verbose)
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    def _unique_col_name(existing: set[str], desired: str) -> str:
        if desired not in existing:
            return desired
        i = 1
        while f"{desired}_{i}" in existing:
            i += 1
        return f"{desired}_{i}"

    def _materialize_index_columns(input_df: pd.DataFrame) -> pd.DataFrame:
        if isinstance(input_df.index, pd.MultiIndex):
            index_names: list[str] = []
            for i, name in enumerate(input_df.index.names):
                index_names.append(name or f"__index_level_{i}__")

            existing = set(map(str, input_df.columns))
            index_names = [_unique_col_name(existing, str(n)) for n in index_names]

            idx_df = input_df.index.to_frame(index=False)
            idx_df.columns = index_names
            out_df = pd.concat([idx_df, input_df.reset_index(drop=True)], axis=1)
            return out_df

        index_name = (
            str(input_df.index.name)
            if input_df.index.name is not None
            else "__index_level_0__"
        )
        existing = set(map(str, input_df.columns))
        index_name = _unique_col_name(existing, index_name)

        out_df = input_df.copy()
        out_df.insert(0, index_name, out_df.index.to_numpy(copy=False))
        out_df = out_df.reset_index(drop=True)
        return out_df

    df = clean_dataframe_columns(df=df, verbose=verbose)

    if preserve_index:
        df = _materialize_index_columns(df)

    if convert:
        df = try_cast_string_columns_to_numeric(
            df=df, convert_partial=partial, verbose=verbose
        )

    schema = generate_parquet_schema(df=df, verbose=verbose)
    try:
        # We materialize index into regular columns above so that the schema can
        # fully describe the resulting table and the index is preserved even
        # when an explicit schema is supplied.
        table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
        return table
    except Exception as e:
        log_error(f"Error generating PyArrow Table: {e}", verbose)
        raise


def generate_sql_server_create_table_string(
    df: Optional[pd.DataFrame] = None,
    catalog: str = "database",
    schema: str = "dbo",
    table: str = "table",
    dropexisting: bool = True,
    verbose: bool = False,
) -> str:
    """
    Generate a SQL Server CREATE TABLE statement from a pandas DataFrame.

    Args:
        df: The DataFrame to generate the schema from. If None, returns None.
        catalog: The database catalog name.
        schema: The schema name (default: 'dbo').
        table: The table name.
        dropexisting: If True, includes DROP TABLE IF EXISTS statement.
        verbose: If True, prints progress messages.

    Returns:
        SQL Server CREATE TABLE statement string with optimized column types,
        or None if no DataFrame is provided.
    """
    if df is None:
        log_warning(
            "No DataFrame provided; exiting generate_sql_server_create_table_string.",
            verbose,
        )
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(catalog, str) or not catalog.strip():
        raise ValueError("catalog must be a non-empty string")
    if not isinstance(schema, str) or not schema.strip():
        raise ValueError("schema must be a non-empty string")
    if not isinstance(table, str) or not table.strip():
        raise ValueError("table must be a non-empty string")

    from ..sql.ddl import generate_create_table
    from ..sql.dialects import Dialect

    return generate_create_table(
        df=df,
        catalog=catalog,
        schema=schema,
        table=table,
        drop_existing=dropexisting,
        dialect=Dialect.SQLSERVER,
        verbose=verbose,
    )


def write_to_file_and_sql(
    df: pd.DataFrame,
    file_path: str,
    table_name: str,
    sql_server: str,
    database: str,
    username: str,
    password: str,
    verbose: bool = False,
) -> None:
    """
    Write a DataFrame to a CSV file and import it to SQL Server using BCP.

    Args:
        df: The DataFrame to write.
        file_path: Path where the CSV file will be saved.
        table_name: Name of the SQL Server table.
        sql_server: SQL Server instance name.
        database: Database name.
        username: SQL Server username.
        password: SQL Server password.
        verbose: If True, prints progress messages.

    Raises:
        subprocess.CalledProcessError: If BCP command fails.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("file_path must be a non-empty string")
    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name must be a non-empty string")
    if not isinstance(sql_server, str) or not sql_server.strip():
        raise ValueError("sql_server must be a non-empty string")
    if not isinstance(database, str) or not database.strip():
        raise ValueError("database must be a non-empty string")
    if not isinstance(username, str) or not username.strip():
        raise ValueError("username must be a non-empty string")
    if not isinstance(password, str) or not password:
        raise ValueError("password must be provided")

    path_obj = pathlib.Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path_obj, index=False)
    log_info(f"DataFrame written to file {path_obj}.", verbose)

    qualified_table = f"{database}.dbo.{table_name}"
    bcp_args = [
        "bcp",
        qualified_table,
        "in",
        str(path_obj),
        "-c",
        "-t,",
        "-S",
        sql_server,
        "-U",
        username,
        "-P",
        password,
    ]

    log_debug(
        f"Executing BCP load to {qualified_table} on server {sql_server} as user {username}.",
        verbose,
    )
    process = subprocess.run(
        bcp_args,
        shell=False,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode == 0:
        log_info(
            f"DataFrame successfully written to SQL Server table {table_name}.", verbose
        )
    else:
        error_msg = process.stderr.decode()
        log_error(
            f"Error writing DataFrame to SQL Server table {table_name}: {error_msg}",
            verbose,
        )
        raise subprocess.CalledProcessError(
            process.returncode,
            bcp_args,
            output=process.stdout,
            stderr=process.stderr,
        )
