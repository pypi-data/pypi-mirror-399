from __future__ import annotations

import logging
from typing import List, Optional

from ..utils.messages import print_verbose
from .ddl import _qualify_name
from .dialects import Dialect
from .quoting import quote_identifier

logger = logging.getLogger("datablade")


def _require_pyarrow():
    try:
        import pyarrow as pa  # type: ignore
        import pyarrow.parquet as pq  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Parquet DDL generation requires 'pyarrow'. Install with: pip install pyarrow"
        ) from exc

    return pa, pq


def _sql_type_from_arrow(data_type, dialect: Dialect) -> Optional[str]:  # noqa: C901
    """Map a pyarrow.DataType to a SQL type string.

    Returns None when there is no clean mapping and the caller should drop the column.
    """

    pa, _ = _require_pyarrow()

    # Dictionary-encoded columns behave like their value type for DDL purposes.
    if pa.types.is_dictionary(data_type):
        return _sql_type_from_arrow(data_type.value_type, dialect)

    # Nested/complex types: no clean general mapping across dialects.
    if (
        pa.types.is_struct(data_type)
        or pa.types.is_list(data_type)
        or pa.types.is_large_list(data_type)
        or pa.types.is_fixed_size_list(data_type)
        or pa.types.is_map(data_type)
        or pa.types.is_union(data_type)
    ):
        return None

    if dialect == Dialect.SQLSERVER:
        if pa.types.is_boolean(data_type):
            return "bit"
        if pa.types.is_int8(data_type) or pa.types.is_int16(data_type):
            return "smallint"
        if pa.types.is_int32(data_type):
            return "int"
        if pa.types.is_int64(data_type):
            return "bigint"
        if pa.types.is_uint8(data_type) or pa.types.is_uint16(data_type):
            return "int"
        if pa.types.is_uint32(data_type):
            return "bigint"
        if pa.types.is_uint64(data_type):
            return "decimal(20, 0)"
        if pa.types.is_float16(data_type) or pa.types.is_float32(data_type):
            return "real"
        if pa.types.is_float64(data_type):
            return "float"
        if pa.types.is_decimal(data_type):
            precision = min(int(data_type.precision), 38)
            scale = int(data_type.scale)
            return f"decimal({precision}, {scale})"
        if pa.types.is_date(data_type):
            return "date"
        if pa.types.is_time(data_type):
            return "time"
        if pa.types.is_timestamp(data_type):
            # SQL Server has datetimeoffset for tz-aware values.
            return "datetimeoffset" if data_type.tz is not None else "datetime2"
        if pa.types.is_binary(data_type) or pa.types.is_large_binary(data_type):
            return "varbinary(max)"
        if pa.types.is_fixed_size_binary(data_type):
            return (
                f"varbinary({int(data_type.byte_width)})"
                if int(data_type.byte_width) <= 8000
                else "varbinary(max)"
            )
        if pa.types.is_string(data_type) or pa.types.is_large_string(data_type):
            return "nvarchar(max)"

        # Anything else (including null) is not reliably representable.
        return None

    if dialect == Dialect.POSTGRES:
        if pa.types.is_boolean(data_type):
            return "boolean"
        if pa.types.is_int8(data_type) or pa.types.is_int16(data_type):
            return "smallint"
        if pa.types.is_int32(data_type):
            return "integer"
        if pa.types.is_int64(data_type):
            return "bigint"
        if pa.types.is_unsigned_integer(data_type):
            # Postgres has no unsigned ints; use a wider signed or numeric.
            if pa.types.is_uint8(data_type) or pa.types.is_uint16(data_type):
                return "integer"
            if pa.types.is_uint32(data_type):
                return "bigint"
            if pa.types.is_uint64(data_type):
                return "numeric(20, 0)"
        if pa.types.is_float16(data_type) or pa.types.is_float32(data_type):
            return "real"
        if pa.types.is_float64(data_type):
            return "double precision"
        if pa.types.is_decimal(data_type):
            precision = int(data_type.precision)
            scale = int(data_type.scale)
            return f"numeric({precision}, {scale})"
        if pa.types.is_date(data_type):
            return "date"
        if pa.types.is_time(data_type):
            return "time"
        if pa.types.is_timestamp(data_type):
            return "timestamptz" if data_type.tz is not None else "timestamp"
        if pa.types.is_binary(data_type) or pa.types.is_large_binary(data_type):
            return "bytea"
        if pa.types.is_fixed_size_binary(data_type):
            return "bytea"
        if pa.types.is_string(data_type) or pa.types.is_large_string(data_type):
            return "text"

        return None

    if dialect == Dialect.MYSQL:
        if pa.types.is_boolean(data_type):
            return "TINYINT(1)"
        if pa.types.is_int8(data_type) or pa.types.is_int16(data_type):
            return "SMALLINT"
        if pa.types.is_int32(data_type):
            return "INT"
        if pa.types.is_int64(data_type):
            return "BIGINT"
        if pa.types.is_unsigned_integer(data_type):
            # MySQL supports UNSIGNED, but we keep mappings consistent with the existing
            # pandas-based DDL generator (signed types).
            if pa.types.is_uint8(data_type) or pa.types.is_uint16(data_type):
                return "INT"
            if pa.types.is_uint32(data_type):
                return "BIGINT"
            if pa.types.is_uint64(data_type):
                return "DECIMAL(20, 0)"
        if pa.types.is_float16(data_type) or pa.types.is_float32(data_type):
            return "FLOAT"
        if pa.types.is_float64(data_type):
            return "DOUBLE"
        if pa.types.is_decimal(data_type):
            precision = int(data_type.precision)
            scale = int(data_type.scale)
            return f"DECIMAL({precision}, {scale})"
        if pa.types.is_date(data_type):
            return "DATE"
        if pa.types.is_time(data_type):
            return "TIME"
        if pa.types.is_timestamp(data_type):
            return "DATETIME"
        if pa.types.is_binary(data_type) or pa.types.is_large_binary(data_type):
            return "LONGBLOB"
        if pa.types.is_fixed_size_binary(data_type):
            width = int(data_type.byte_width)
            return f"VARBINARY({width})" if width <= 65535 else "LONGBLOB"
        if pa.types.is_string(data_type) or pa.types.is_large_string(data_type):
            return "TEXT"

        return None

    if dialect == Dialect.DUCKDB:
        if pa.types.is_boolean(data_type):
            return "BOOLEAN"
        if pa.types.is_signed_integer(data_type):
            return "BIGINT"
        if pa.types.is_unsigned_integer(data_type):
            return "UBIGINT"
        if pa.types.is_floating(data_type):
            return "DOUBLE"
        if pa.types.is_decimal(data_type):
            precision = int(data_type.precision)
            scale = int(data_type.scale)
            return f"DECIMAL({precision}, {scale})"
        if pa.types.is_date(data_type):
            return "DATE"
        if pa.types.is_time(data_type):
            return "TIME"
        if pa.types.is_timestamp(data_type):
            return "TIMESTAMPTZ" if data_type.tz is not None else "TIMESTAMP"
        if pa.types.is_binary(data_type) or pa.types.is_large_binary(data_type):
            return "BLOB"
        if pa.types.is_fixed_size_binary(data_type):
            return "BLOB"
        if pa.types.is_string(data_type) or pa.types.is_large_string(data_type):
            return "VARCHAR"

        return None

    raise NotImplementedError(f"Dialect not supported: {dialect}")


def generate_create_table_from_parquet(
    parquet_path: str,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
    table: str = "table",
    drop_existing: bool = True,
    dialect: Dialect = Dialect.SQLSERVER,
    verbose: bool = False,
) -> str:
    """Generate a CREATE TABLE statement from a Parquet file schema.

    This reads the Parquet schema only (via PyArrow) and does not materialize data.

    Columns whose Parquet types have no clean mapping for the chosen dialect are
    dropped, and a warning is logged under logger name 'datablade'.
    """

    if (
        parquet_path is None
        or not isinstance(parquet_path, str)
        or not parquet_path.strip()
    ):
        raise ValueError("parquet_path must be a non-empty string")
    if not isinstance(table, str) or not table.strip():
        raise ValueError("table must be a non-empty string")
    if catalog is not None and (not isinstance(catalog, str) or not catalog.strip()):
        raise ValueError("catalog, if provided, must be a non-empty string")
    if schema is not None and (not isinstance(schema, str) or not schema.strip()):
        raise ValueError("schema, if provided, must be a non-empty string")

    _, pq = _require_pyarrow()

    arrow_schema = pq.ParquetFile(parquet_path).schema_arrow

    qualified_name = _qualify_name(catalog, schema, table, dialect)
    lines: List[str] = []

    for field in arrow_schema:
        sql_type = _sql_type_from_arrow(field.type, dialect)
        if sql_type is None:
            logger.warning(
                "Dropping Parquet column %r (type=%s) for dialect=%s: unsupported type",
                field.name,
                str(field.type),
                dialect.value,
            )
            continue

        null_str = "NULL" if field.nullable else "NOT NULL"
        lines.append(
            f"    {quote_identifier(str(field.name), dialect)} {sql_type} {null_str}"
        )

    if not lines:
        raise ValueError(
            "No supported columns found in Parquet schema for the selected dialect"
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
                drop_clause = (
                    f"IF OBJECT_ID('{qualified_name}') IS NOT NULL "
                    f"DROP TABLE {qualified_name};\n"
                )
        else:
            drop_clause = f"DROP TABLE IF EXISTS {qualified_name};\n"

    statement = f"{drop_clause}CREATE TABLE {qualified_name} (\n{body}\n);"
    print_verbose(
        f"Generated CREATE TABLE from Parquet schema for {qualified_name}", verbose
    )
    return statement
