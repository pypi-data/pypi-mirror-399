from typing import Any, List, Optional

import pandas as pd

from ..utils.messages import print_verbose
from .dialects import Dialect
from .quoting import quote_identifier


def _infer_sql_type(series: pd.Series, dialect: Dialect) -> str:  # noqa: C901
    """Infer a SQL column type for a pandas Series given a dialect."""
    dtype = series.dtype

    def _is_bytes_like(value: Any) -> bool:
        return isinstance(value, (bytes, bytearray, memoryview))

    def _is_bytes_like_series(s: pd.Series) -> bool:
        if not pd.api.types.is_object_dtype(s.dtype):
            return False
        non_null = s.dropna()
        if non_null.empty:
            return False
        sample = non_null.iloc[:100]
        # require all sampled values to be bytes-like
        return bool(sample.map(_is_bytes_like).all())

    if dialect == Dialect.SQLSERVER:
        if pd.api.types.is_integer_dtype(dtype):
            non_null = series.dropna()
            if non_null.empty:
                return "bigint"
            min_value = non_null.min()
            max_value = non_null.max()
            if min_value >= 0 and max_value <= 255:
                return "tinyint"
            if min_value >= -32768 and max_value <= 32767:
                return "smallint"
            if min_value >= -2147483648 and max_value <= 2147483647:
                return "int"
            return "bigint"
        if pd.api.types.is_float_dtype(dtype):
            return "float"
        if pd.api.types.is_bool_dtype(dtype):
            return "bit"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime2"
        if _is_bytes_like_series(series):
            return "varbinary(max)"
        # strings / objects
        non_null = series.dropna()
        if non_null.empty:
            max_length = 1
        else:
            lengths = non_null.astype(str).map(len)
            max_length = int(lengths.max()) if not lengths.empty else 1
        if pd.api.types.is_object_dtype(dtype) or isinstance(
            dtype, pd.CategoricalDtype
        ):
            return f"nvarchar({max_length if max_length <= 4000 else 'max'})"
        return "nvarchar(max)"

    if dialect == Dialect.POSTGRES:
        if pd.api.types.is_integer_dtype(dtype):
            non_null = series.dropna()
            if non_null.empty:
                return "bigint"
            min_value = non_null.min()
            max_value = non_null.max()
            if min_value >= -32768 and max_value <= 32767:
                return "smallint"
            if min_value >= -2147483648 and max_value <= 2147483647:
                return "integer"
            return "bigint"
        if pd.api.types.is_float_dtype(dtype):
            return "double precision"
        if pd.api.types.is_bool_dtype(dtype):
            return "boolean"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "timestamp"
        if _is_bytes_like_series(series):
            return "bytea"
        non_null = series.dropna()
        if non_null.empty:
            max_length = 1
        else:
            lengths = non_null.astype(str).map(len)
            max_length = int(lengths.max()) if not lengths.empty else 1
        return f"varchar({max_length})" if max_length <= 65535 else "text"

    if dialect == Dialect.MYSQL:
        if pd.api.types.is_integer_dtype(dtype):
            non_null = series.dropna()
            if non_null.empty:
                return "BIGINT"
            min_value = non_null.min()
            max_value = non_null.max()
            if min_value >= -32768 and max_value <= 32767:
                return "SMALLINT"
            if min_value >= -2147483648 and max_value <= 2147483647:
                return "INT"
            return "BIGINT"
        if pd.api.types.is_float_dtype(dtype):
            return "DOUBLE"
        if pd.api.types.is_bool_dtype(dtype):
            return "TINYINT(1)"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "DATETIME"
        if _is_bytes_like_series(series):
            return "LONGBLOB"
        non_null = series.dropna()
        if non_null.empty:
            max_length = 1
        else:
            lengths = non_null.astype(str).map(len)
            max_length = int(lengths.max()) if not lengths.empty else 1
        return f"VARCHAR({max_length})" if max_length <= 65535 else "TEXT"

    if dialect == Dialect.DUCKDB:
        if pd.api.types.is_integer_dtype(dtype):
            return (
                "BIGINT" if pd.api.types.is_signed_integer_dtype(dtype) else "UBIGINT"
            )
        if pd.api.types.is_float_dtype(dtype):
            return "DOUBLE"
        if pd.api.types.is_bool_dtype(dtype):
            return "BOOLEAN"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "TIMESTAMP"
        if _is_bytes_like_series(series):
            return "BLOB"
        return "VARCHAR"

    raise NotImplementedError(f"Dialect not supported: {dialect}")


def _qualify_name(
    catalog: Optional[str], schema: Optional[str], table: str, dialect: Dialect
) -> str:
    if dialect == Dialect.SQLSERVER:
        # catalog and schema are both used when provided
        if catalog:
            return (
                f"{quote_identifier(catalog, dialect)}."
                f"{quote_identifier(schema or 'dbo', dialect)}."
                f"{quote_identifier(table, dialect)}"
            )
        return (
            f"{quote_identifier(schema or 'dbo', dialect)}."
            f"{quote_identifier(table, dialect)}"
        )

    if schema:
        return f"{quote_identifier(schema, dialect)}.{quote_identifier(table, dialect)}"
    return quote_identifier(table, dialect)


def generate_create_table(
    df: pd.DataFrame,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
    table: str = "table",
    drop_existing: bool = True,
    dialect: Dialect = Dialect.SQLSERVER,
    verbose: bool = False,
) -> str:
    """
    Generate a CREATE TABLE statement for the given dialect.

    Args:
        df: Source DataFrame.
        catalog: Optional catalog/database name.
        schema: Optional schema name (defaults per dialect).
        table: Target table name.
        drop_existing: If True, include a DROP TABLE IF EXISTS stanza.
        dialect: SQL dialect.
        verbose: If True, prints progress messages.

    Returns:
        CREATE TABLE statement as string.

    Raises:
        ValueError: On missing/invalid inputs.
        TypeError: If df is not a DataFrame.
        NotImplementedError: If dialect unsupported.
    """
    if df is None:
        raise ValueError("df must be provided")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(table, str) or not table.strip():
        raise ValueError("table must be a non-empty string")
    if catalog is not None and (not isinstance(catalog, str) or not catalog.strip()):
        raise ValueError("catalog, if provided, must be a non-empty string")
    if schema is not None and (not isinstance(schema, str) or not schema.strip()):
        raise ValueError("schema, if provided, must be a non-empty string")

    qualified_name = _qualify_name(catalog, schema, table, dialect)
    lines: List[str] = []

    for column in df.columns:
        series = df[column]
        nullable = series.isnull().any()
        sql_type = _infer_sql_type(series, dialect)
        null_str = "NULL" if nullable else "NOT NULL"
        lines.append(
            f"    {quote_identifier(str(column), dialect)} {sql_type} {null_str}"
        )

    body = ",\n".join(lines)

    drop_clause = ""
    if drop_existing:
        if dialect == Dialect.SQLSERVER:
            if catalog:
                drop_clause = (
                    f"USE {quote_identifier(catalog, dialect)};\n"
                    f"IF OBJECT_ID('{qualified_name}') IS NOT NULL "
                    f"DROP TABLE {qualified_name};\n"
                )
            else:
                drop_clause = f"IF OBJECT_ID('{qualified_name}') IS NOT NULL DROP TABLE {qualified_name};\n"
        else:
            drop_clause = f"DROP TABLE IF EXISTS {qualified_name};\n"

    statement = f"{drop_clause}CREATE TABLE {qualified_name} (\n{body}\n);"
    print_verbose(f"Generated CREATE TABLE for {qualified_name}", verbose)
    return statement
