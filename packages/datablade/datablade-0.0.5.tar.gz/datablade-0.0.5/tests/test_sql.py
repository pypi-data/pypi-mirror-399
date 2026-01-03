"""Tests for datablade.sql module."""

import logging
from unittest.mock import Mock, patch

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from datablade.sql import (
    Dialect,
    bulk_load,
    bulk_load_duckdb,
    bulk_load_mysql,
    bulk_load_postgres,
    bulk_load_sqlserver,
    generate_create_table,
    generate_create_table_from_parquet,
    quote_identifier,
    write_dataframe_and_load,
)


def _write_parquet(tmp_path, *, schema: pa.Schema, data: dict) -> str:
    table = pa.table(data, schema=schema)
    parquet_path = tmp_path / "data.parquet"
    pq.write_table(table, parquet_path)
    return str(parquet_path)


class TestDialect:
    """Tests for Dialect enum."""

    def test_dialect_values(self):
        """Test that Dialect enum has expected values."""
        assert Dialect.SQLSERVER == "sqlserver"
        assert Dialect.POSTGRES == "postgres"
        assert Dialect.MYSQL == "mysql"
        assert Dialect.DUCKDB == "duckdb"


class TestQuoteIdentifier:
    """Tests for quote_identifier function."""

    def test_quote_sqlserver(self):
        """Test SQL Server identifier quoting."""
        result = quote_identifier("table_name", Dialect.SQLSERVER)
        assert result == "[table_name]"

    def test_quote_postgres(self):
        """Test PostgreSQL identifier quoting."""
        result = quote_identifier("table_name", Dialect.POSTGRES)
        assert result == '"table_name"'

    def test_quote_mysql(self):
        """Test MySQL identifier quoting."""
        result = quote_identifier("table_name", Dialect.MYSQL)
        assert result == "`table_name`"

    def test_quote_duckdb(self):
        """Test DuckDB identifier quoting."""
        result = quote_identifier("table_name", Dialect.DUCKDB)
        assert result == '"table_name"'

    def test_escape_existing_quotes_postgres(self):
        """Test that existing quotes are escaped in PostgreSQL."""
        result = quote_identifier('table"name', Dialect.POSTGRES)
        assert result == '"table""name"'

    def test_escape_existing_quotes_mysql(self):
        """Test that existing backticks are escaped in MySQL."""
        result = quote_identifier("table`name", Dialect.MYSQL)
        assert result == "`table``name`"

    def test_remove_brackets_sqlserver(self):
        """Test that existing brackets are removed for SQL Server."""
        result = quote_identifier("[table_name]", Dialect.SQLSERVER)
        assert result == "[table_name]"

    def test_none_name_raises_error(self):
        """Test that None name raises ValueError."""
        with pytest.raises(ValueError, match="name must be provided"):
            quote_identifier(None, Dialect.SQLSERVER)

    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            quote_identifier("   ", Dialect.SQLSERVER)

    def test_non_string_name_raises_error(self):
        """Test that non-string name raises TypeError."""
        with pytest.raises(TypeError, match="name must be a string"):
            quote_identifier(123, Dialect.SQLSERVER)

    def test_unsupported_dialect_raises_error(self):
        with pytest.raises(NotImplementedError, match="Dialect not supported"):
            quote_identifier("x", "nope")  # type: ignore[arg-type]


class TestGenerateCreateTable:
    """Tests for generate_create_table function."""

    def test_generate_sqlserver_create_table(self):
        """Test SQL Server CREATE TABLE generation."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
            }
        )

        sql = generate_create_table(
            df, catalog="testdb", schema="dbo", table="users", dialect=Dialect.SQLSERVER
        )

        assert "CREATE TABLE" in sql
        assert "users" in sql
        assert "id" in sql
        assert "name" in sql
        assert "age" in sql

    def test_generate_postgres_create_table(self):
        """Test PostgreSQL CREATE TABLE generation."""
        df = pd.DataFrame({"id": [1, 2, 3], "value": [10.5, 20.3, 30.1]})

        sql = generate_create_table(
            df, schema="public", table="data", dialect=Dialect.POSTGRES
        )

        assert "CREATE TABLE" in sql
        assert '"public"."data"' in sql

    def test_generate_mysql_create_table(self):
        """Test MySQL CREATE TABLE generation."""
        df = pd.DataFrame({"id": [1, 2, 3], "active": [True, False, True]})

        sql = generate_create_table(df, table="flags", dialect=Dialect.MYSQL)

        assert "CREATE TABLE" in sql
        assert "`flags`" in sql

    def test_generate_duckdb_create_table(self):
        """Test DuckDB CREATE TABLE generation."""
        df = pd.DataFrame({"id": [1, 2, 3], "text": ["a", "b", "c"]})

        sql = generate_create_table(df, table="items", dialect=Dialect.DUCKDB)

        assert "CREATE TABLE" in sql
        assert '"items"' in sql

    def test_drop_table_included_by_default(self):
        """Test that DROP TABLE is included by default."""
        df = pd.DataFrame({"id": [1, 2, 3]})

        sql = generate_create_table(df, table="test", dialect=Dialect.POSTGRES)

        assert "DROP TABLE" in sql

    def test_drop_table_omitted_when_disabled(self):
        """Test that DROP TABLE can be omitted."""
        df = pd.DataFrame({"id": [1, 2, 3]})

        sql = generate_create_table(
            df, table="test", drop_existing=False, dialect=Dialect.POSTGRES
        )

        assert "DROP TABLE" not in sql

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            generate_create_table(None, table="test")

    def test_non_dataframe_raises_error(self):
        """Test that non-DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            generate_create_table("not a dataframe", table="test")

    def test_empty_table_raises_error(self):
        """Test that empty table name raises ValueError."""
        df = pd.DataFrame({"id": [1, 2, 3]})
        with pytest.raises(ValueError, match="table must be a non-empty string"):
            generate_create_table(df, table="")

    def test_bytes_column_sqlserver_maps_to_varbinary(self):
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "varbinary(max)" in sql.lower()

    def test_bytes_column_postgres_maps_to_bytea(self):
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert "bytea" in sql.lower()

    def test_bytes_column_mysql_maps_to_blob(self):
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.MYSQL)
        assert "blob" in sql.lower()

    def test_bytes_column_duckdb_maps_to_blob(self):
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.DUCKDB)
        assert "blob" in sql.lower()

    def test_all_null_nullable_int_does_not_crash(self):
        df = pd.DataFrame({"n": pd.Series([pd.NA, pd.NA], dtype="Int64")})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "create table" in sql.lower()

    def test_long_strings_sqlserver_use_nvarchar_max(self):
        df = pd.DataFrame({"s": ["a" * 5000]})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "nvarchar(max)" in sql.lower()

    def test_duckdb_unsigned_int_maps_to_ubigint(self):
        df = pd.DataFrame({"n": pd.Series([1, 2, 3], dtype="UInt64")})
        sql = generate_create_table(df, table="t", dialect=Dialect.DUCKDB)
        assert "ubigint" in sql.lower()

    def test_sqlserver_integer_ranges_map_to_expected_types(self):
        df = pd.DataFrame(
            {
                "tiny": [0, 255],
                "small": [-32768, 32767],
                "regular": [-2147483648, 2147483647],
                "big": [-2147483649, 2147483648],
            }
        )
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        lowered = sql.lower()
        assert "[tiny] tinyint" in lowered
        assert "[small] smallint" in lowered
        assert "[regular] int" in lowered
        assert "[big] bigint" in lowered

    def test_sqlserver_category_calls_bytes_probe_and_maps_to_nvarchar_len(self):
        # Categorical dtype isn't object; this exercises the `_is_bytes_like_series`
        # non-object early return.
        df = pd.DataFrame({"cat": pd.Series(pd.Categorical(["a", "bb"]))})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "nvarchar(2)" in sql.lower()

    def test_sqlserver_short_strings_use_nvarchar_len(self):
        df = pd.DataFrame({"s": ["abc"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "nvarchar(3)" in sql.lower()

    def test_postgres_very_long_strings_use_text(self):
        df = pd.DataFrame({"s": ["a" * 70000]})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert " text" in sql.lower()

    def test_object_column_not_all_bytes_treated_as_string(self):
        # Ensures the bytes-like sampler returns False when mixed types appear.
        df = pd.DataFrame({"mixed": [b"\x00", "x"]})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert "bytea" not in sql.lower()

    def test_sqlserver_drop_without_catalog_uses_object_id(self):
        df = pd.DataFrame({"id": [1]})
        sql = generate_create_table(
            df,
            table="t",
            schema=None,
            catalog=None,
            dialect=Dialect.SQLSERVER,
            drop_existing=True,
        )
        assert "if object_id" in sql.lower()

    def test_invalid_catalog_schema_raise_value_error(self):
        df = pd.DataFrame({"id": [1]})
        with pytest.raises(ValueError, match="catalog, if provided"):
            generate_create_table(df, table="t", catalog="  ")
        with pytest.raises(ValueError, match="schema, if provided"):
            generate_create_table(df, table="t", schema="  ")

    def test_unsupported_dialect_raises_not_implemented(self):
        from datablade.sql.ddl import _infer_sql_type

        with pytest.raises(NotImplementedError, match="Dialect not supported"):
            _infer_sql_type(pd.Series([1, 2, 3]), "nope")  # type: ignore[arg-type]

    def test_sqlserver_all_null_object_column_uses_nvarchar_1(self):
        # Exercises bytes-probe empty path and string-length empty path.
        df = pd.DataFrame({"s": pd.Series([None, None], dtype="object")})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "nvarchar(1)" in sql.lower()

    def test_sqlserver_string_dtype_uses_nvarchar_max_fallback(self):
        # Pandas StringDtype is not object dtype; this exercises the final
        # nvarchar(max) fallback path.
        df = pd.DataFrame({"s": pd.Series(["a"], dtype="string")})
        sql = generate_create_table(df, table="t", dialect=Dialect.SQLSERVER)
        assert "nvarchar(max)" in sql.lower()

    def test_postgres_nullable_int_all_null_maps_to_bigint(self):
        df = pd.DataFrame({"n": pd.Series([pd.NA, pd.NA], dtype="Int64")})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert "bigint" in sql.lower()

    def test_postgres_int32_range_maps_to_integer(self):
        df = pd.DataFrame({"n": [0, 50000]})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert " integer" in sql.lower()

    def test_postgres_outside_int32_range_maps_to_bigint(self):
        df = pd.DataFrame({"n": [-2147483649, 0]})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert " bigint" in sql.lower()

    def test_postgres_all_null_object_column_sets_default_length(self):
        df = pd.DataFrame({"s": pd.Series([None], dtype="object")})
        sql = generate_create_table(df, table="t", dialect=Dialect.POSTGRES)
        assert "varchar(1)" in sql.lower()

    def test_mysql_nullable_int_all_null_maps_to_bigint(self):
        df = pd.DataFrame({"n": pd.Series([pd.NA, pd.NA], dtype="Int64")})
        sql = generate_create_table(df, table="t", dialect=Dialect.MYSQL)
        assert "bigint" in sql.lower()

    def test_mysql_int32_range_maps_to_int(self):
        df = pd.DataFrame({"n": [0, 50000]})
        sql = generate_create_table(df, table="t", dialect=Dialect.MYSQL)
        assert " int" in sql.lower()

    def test_mysql_outside_int32_range_maps_to_bigint(self):
        df = pd.DataFrame({"n": [-2147483649, 0]})
        sql = generate_create_table(df, table="t", dialect=Dialect.MYSQL)
        assert " bigint" in sql.lower()

    def test_mysql_all_null_object_column_sets_default_length(self):
        df = pd.DataFrame({"s": pd.Series([None], dtype="object")})
        sql = generate_create_table(df, table="t", dialect=Dialect.MYSQL)
        assert "varchar(1)" in sql.lower()

    def test_duckdb_float_bool_datetime_mappings(self):
        df = pd.DataFrame(
            {
                "f": [1.1, 2.2],
                "b": [True, False],
                "t": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            }
        )
        sql = generate_create_table(df, table="t", dialect=Dialect.DUCKDB)
        lowered = sql.lower()
        assert " double" in lowered
        assert " boolean" in lowered
        assert " timestamp" in lowered


class TestGenerateCreateTableFromParquet:
    def test_generates_postgres_ddl_from_parquet_schema(self, tmp_path):
        table = pa.table(
            {
                "id": pa.array([1], type=pa.int64()),
                "name": pa.array(["a"], type=pa.string()),
                "created_at": pa.array([0], type=pa.timestamp("us", tz="UTC")),
                "payload": pa.array([b"\x00"], type=pa.binary()),
            }
        )
        parquet_path = tmp_path / "t.parquet"
        pq.write_table(table, parquet_path)

        ddl = generate_create_table_from_parquet(
            str(parquet_path),
            schema="public",
            table="events",
            dialect=Dialect.POSTGRES,
        )

        assert "CREATE TABLE" in ddl
        assert '"public"."events"' in ddl
        assert '"id" bigint' in ddl
        assert '"name" text' in ddl
        assert '"created_at" timestamptz' in ddl
        assert '"payload" bytea' in ddl

    def test_drops_unsupported_complex_types_with_warning(self, tmp_path, caplog):
        # Struct/list types are valid Parquet/Arrow but have no clean mapping across
        # supported SQL dialects.
        schema = pa.schema(
            [
                pa.field("ok", pa.int32(), nullable=False),
                pa.field("nested", pa.struct([pa.field("x", pa.int32())])),
                pa.field("arr", pa.list_(pa.int32())),
            ]
        )
        table = pa.Table.from_arrays(
            [
                pa.array([1], type=pa.int32()),
                pa.array(
                    [{"x": 1}],
                    type=pa.struct([pa.field("x", pa.int32())]),
                ),
                pa.array([[1]], type=pa.list_(pa.int32())),
            ],
            schema=schema,
        )
        parquet_path = tmp_path / "complex.parquet"
        pq.write_table(table, parquet_path)

        with caplog.at_level(logging.WARNING, logger="datablade"):
            ddl = generate_create_table_from_parquet(
                str(parquet_path), table="t", dialect=Dialect.SQLSERVER
            )

        assert "[ok]" in ddl
        assert "[nested]" not in ddl
        assert "[arr]" not in ddl
        assert any(
            "Dropping Parquet column" in rec.message and "nested" in rec.message
            for rec in caplog.records
        )
        assert any(
            "Dropping Parquet column" in rec.message and "arr" in rec.message
            for rec in caplog.records
        )

    def test_validates_inputs(self, tmp_path):
        schema = pa.schema([pa.field("id", pa.int64())])
        parquet_path = _write_parquet(tmp_path, schema=schema, data={"id": [1]})

        with pytest.raises(ValueError, match="parquet_path must be a non-empty string"):
            generate_create_table_from_parquet(None)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="parquet_path must be a non-empty string"):
            generate_create_table_from_parquet("   ")
        with pytest.raises(ValueError, match="table must be a non-empty string"):
            generate_create_table_from_parquet(parquet_path, table=" ")
        with pytest.raises(ValueError, match="catalog, if provided"):
            generate_create_table_from_parquet(parquet_path, table="t", catalog=" ")
        with pytest.raises(ValueError, match="schema, if provided"):
            generate_create_table_from_parquet(parquet_path, table="t", schema=" ")

    def test_raises_when_all_columns_dropped(self, tmp_path):
        schema = pa.schema(
            [pa.field("nested", pa.struct([pa.field("x", pa.int32())]), nullable=True)]
        )
        parquet_path = _write_parquet(
            tmp_path,
            schema=schema,
            data={"nested": [{"x": 1}]},
        )

        with pytest.raises(ValueError, match="No supported columns"):
            generate_create_table_from_parquet(
                parquet_path,
                table="t",
                dialect=Dialect.POSTGRES,
            )

    def test_sqlserver_drop_with_catalog_includes_use(self, tmp_path):
        schema = pa.schema([pa.field("id", pa.int64(), nullable=False)])
        parquet_path = _write_parquet(tmp_path, schema=schema, data={"id": [1]})
        ddl = generate_create_table_from_parquet(
            parquet_path,
            catalog="db",
            schema=None,
            table="t",
            dialect=Dialect.SQLSERVER,
            drop_existing=True,
            verbose=True,
        )
        assert "use [db];" in ddl.lower()

    def test_non_sqlserver_drop_uses_drop_table_if_exists(self, tmp_path):
        schema = pa.schema([pa.field("id", pa.int64(), nullable=True)])
        parquet_path = _write_parquet(tmp_path, schema=schema, data={"id": [1]})
        ddl = generate_create_table_from_parquet(
            parquet_path,
            schema="public",
            table="t",
            dialect=Dialect.POSTGRES,
            drop_existing=True,
        )
        assert "drop table if exists" in ddl.lower()

    def test_drop_existing_false_omits_drop_clause(self, tmp_path):
        schema = pa.schema([pa.field("id", pa.int64(), nullable=True)])
        parquet_path = _write_parquet(tmp_path, schema=schema, data={"id": [1]})
        ddl = generate_create_table_from_parquet(
            parquet_path,
            table="t",
            dialect=Dialect.DUCKDB,
            drop_existing=False,
        )
        assert "drop table" not in ddl.lower()


class TestArrowToSqlTypeMapping:
    def test_sql_type_from_arrow_covers_all_mappings(self):
        from datablade.sql.ddl_pyarrow import _sql_type_from_arrow

        # One representative per return path.
        cases = [
            # Dictionary recursion
            (Dialect.POSTGRES, pa.dictionary(pa.int8(), pa.string()), "text"),
            # Complex types (pre-dialect)
            (Dialect.SQLSERVER, pa.struct([pa.field("x", pa.int32())]), None),
            (Dialect.SQLSERVER, pa.list_(pa.int32()), None),
            (Dialect.SQLSERVER, pa.large_list(pa.int32()), None),
            (Dialect.SQLSERVER, pa.list_(pa.int32(), 2), None),
            (Dialect.SQLSERVER, pa.map_(pa.string(), pa.int32()), None),
            (
                Dialect.SQLSERVER,
                pa.union([pa.field("a", pa.int32())], mode="sparse"),
                None,
            ),
            # SQLSERVER
            (Dialect.SQLSERVER, pa.bool_(), "bit"),
            (Dialect.SQLSERVER, pa.int8(), "smallint"),
            (Dialect.SQLSERVER, pa.int16(), "smallint"),
            (Dialect.SQLSERVER, pa.int32(), "int"),
            (Dialect.SQLSERVER, pa.int64(), "bigint"),
            (Dialect.SQLSERVER, pa.uint8(), "int"),
            (Dialect.SQLSERVER, pa.uint16(), "int"),
            (Dialect.SQLSERVER, pa.uint32(), "bigint"),
            (Dialect.SQLSERVER, pa.uint64(), "decimal(20, 0)"),
            (Dialect.SQLSERVER, pa.float16(), "real"),
            (Dialect.SQLSERVER, pa.float32(), "real"),
            (Dialect.SQLSERVER, pa.float64(), "float"),
            (Dialect.SQLSERVER, pa.decimal256(50, 2), "decimal(38, 2)"),
            (Dialect.SQLSERVER, pa.date32(), "date"),
            (Dialect.SQLSERVER, pa.time64("us"), "time"),
            (Dialect.SQLSERVER, pa.timestamp("us"), "datetime2"),
            (Dialect.SQLSERVER, pa.timestamp("us", tz="UTC"), "datetimeoffset"),
            (Dialect.SQLSERVER, pa.binary(), "varbinary(max)"),
            (Dialect.SQLSERVER, pa.large_binary(), "varbinary(max)"),
            (Dialect.SQLSERVER, pa.binary(10), "varbinary(10)"),
            (Dialect.SQLSERVER, pa.binary(9000), "varbinary(max)"),
            (Dialect.SQLSERVER, pa.string(), "nvarchar(max)"),
            (Dialect.SQLSERVER, pa.large_string(), "nvarchar(max)"),
            (Dialect.SQLSERVER, pa.null(), None),
            # POSTGRES
            (Dialect.POSTGRES, pa.bool_(), "boolean"),
            (Dialect.POSTGRES, pa.int8(), "smallint"),
            (Dialect.POSTGRES, pa.int16(), "smallint"),
            (Dialect.POSTGRES, pa.int32(), "integer"),
            (Dialect.POSTGRES, pa.int64(), "bigint"),
            (Dialect.POSTGRES, pa.uint8(), "integer"),
            (Dialect.POSTGRES, pa.uint16(), "integer"),
            (Dialect.POSTGRES, pa.uint32(), "bigint"),
            (Dialect.POSTGRES, pa.uint64(), "numeric(20, 0)"),
            (Dialect.POSTGRES, pa.float16(), "real"),
            (Dialect.POSTGRES, pa.float32(), "real"),
            (Dialect.POSTGRES, pa.float64(), "double precision"),
            (Dialect.POSTGRES, pa.decimal128(10, 3), "numeric(10, 3)"),
            (Dialect.POSTGRES, pa.date32(), "date"),
            (Dialect.POSTGRES, pa.time64("us"), "time"),
            (Dialect.POSTGRES, pa.timestamp("us"), "timestamp"),
            (Dialect.POSTGRES, pa.timestamp("us", tz="UTC"), "timestamptz"),
            (Dialect.POSTGRES, pa.binary(), "bytea"),
            (Dialect.POSTGRES, pa.large_binary(), "bytea"),
            (Dialect.POSTGRES, pa.binary(10), "bytea"),
            (Dialect.POSTGRES, pa.string(), "text"),
            (Dialect.POSTGRES, pa.large_string(), "text"),
            (Dialect.POSTGRES, pa.null(), None),
            # MYSQL
            (Dialect.MYSQL, pa.bool_(), "TINYINT(1)"),
            (Dialect.MYSQL, pa.int8(), "SMALLINT"),
            (Dialect.MYSQL, pa.int16(), "SMALLINT"),
            (Dialect.MYSQL, pa.int32(), "INT"),
            (Dialect.MYSQL, pa.int64(), "BIGINT"),
            (Dialect.MYSQL, pa.uint8(), "INT"),
            (Dialect.MYSQL, pa.uint16(), "INT"),
            (Dialect.MYSQL, pa.uint32(), "BIGINT"),
            (Dialect.MYSQL, pa.uint64(), "DECIMAL(20, 0)"),
            (Dialect.MYSQL, pa.float16(), "FLOAT"),
            (Dialect.MYSQL, pa.float32(), "FLOAT"),
            (Dialect.MYSQL, pa.float64(), "DOUBLE"),
            (Dialect.MYSQL, pa.decimal128(12, 4), "DECIMAL(12, 4)"),
            (Dialect.MYSQL, pa.date32(), "DATE"),
            (Dialect.MYSQL, pa.time64("us"), "TIME"),
            (Dialect.MYSQL, pa.timestamp("us"), "DATETIME"),
            (Dialect.MYSQL, pa.binary(), "LONGBLOB"),
            (Dialect.MYSQL, pa.large_binary(), "LONGBLOB"),
            (Dialect.MYSQL, pa.binary(10), "VARBINARY(10)"),
            (Dialect.MYSQL, pa.binary(70000), "LONGBLOB"),
            (Dialect.MYSQL, pa.string(), "TEXT"),
            (Dialect.MYSQL, pa.large_string(), "TEXT"),
            (Dialect.MYSQL, pa.null(), None),
            # DUCKDB
            (Dialect.DUCKDB, pa.bool_(), "BOOLEAN"),
            (Dialect.DUCKDB, pa.int32(), "BIGINT"),
            (Dialect.DUCKDB, pa.uint32(), "UBIGINT"),
            (Dialect.DUCKDB, pa.float32(), "DOUBLE"),
            (Dialect.DUCKDB, pa.decimal128(9, 1), "DECIMAL(9, 1)"),
            (Dialect.DUCKDB, pa.date32(), "DATE"),
            (Dialect.DUCKDB, pa.time64("us"), "TIME"),
            (Dialect.DUCKDB, pa.timestamp("us"), "TIMESTAMP"),
            (Dialect.DUCKDB, pa.timestamp("us", tz="UTC"), "TIMESTAMPTZ"),
            (Dialect.DUCKDB, pa.binary(), "BLOB"),
            (Dialect.DUCKDB, pa.large_binary(), "BLOB"),
            (Dialect.DUCKDB, pa.binary(10), "BLOB"),
            (Dialect.DUCKDB, pa.string(), "VARCHAR"),
            (Dialect.DUCKDB, pa.large_string(), "VARCHAR"),
            (Dialect.DUCKDB, pa.null(), None),
        ]

        for dialect, arrow_type, expected in cases:
            assert _sql_type_from_arrow(arrow_type, dialect) == expected

        with pytest.raises(NotImplementedError, match="Dialect not supported"):
            _sql_type_from_arrow(pa.int32(), "nope")  # type: ignore[arg-type]


class TestBulkLoadPostgres:
    """Tests for bulk_load_postgres function."""

    def test_generates_copy_command(self, temp_dir, sample_df, sample_csv_file):
        """Test that COPY command is generated."""
        result = bulk_load_postgres(
            sample_csv_file, table_name="users", database="testdb", schema="public"
        )

        assert "\\COPY" in result
        assert "users" in result
        assert "public" in result

    def test_includes_delimiter(self, sample_csv_file):
        """Test that delimiter is included in command."""
        result = bulk_load_postgres(
            sample_csv_file, table_name="test", database="db", delimiter="|"
        )

        assert "DELIMITER" in result
        assert "|" in result

    def test_file_not_found_raises_error(self):
        """Test that non-existent file raises ValueError."""
        with pytest.raises(ValueError, match="File does not exist"):
            bulk_load_postgres(
                "/nonexistent/file.csv", table_name="test", database="db"
            )


class TestBulkLoadMysql:
    """Tests for bulk_load_mysql function."""

    def test_generates_load_data_command(self, sample_csv_file):
        """Test that LOAD DATA command is generated."""
        result = bulk_load_mysql(sample_csv_file, table_name="users", database="testdb")

        assert "LOAD DATA" in result
        assert "users" in result
        assert "testdb" in result

    def test_includes_field_options(self, sample_csv_file):
        """Test that field options are included."""
        result = bulk_load_mysql(
            sample_csv_file,
            table_name="test",
            database="db",
            delimiter="|",
            enclosed_by="'",
        )

        assert "FIELDS TERMINATED BY" in result
        assert "ENCLOSED BY" in result
        assert "'" in result


class TestBulkLoadDuckdb:
    """Tests for bulk_load_duckdb function."""

    def test_generates_copy_command_csv(self, sample_csv_file):
        """Test COPY command generation for CSV."""
        result = bulk_load_duckdb(sample_csv_file, table_name="test", database="memory")

        assert "COPY" in result
        assert "FORMAT CSV" in result

    def test_generates_copy_command_parquet(self, sample_parquet_file):
        result = bulk_load_duckdb(
            sample_parquet_file, table_name="test", database="memory"
        )
        assert "FORMAT PARQUET" in result

    def test_generates_copy_command_other_suffix(self, tmp_path):
        p = tmp_path / "data.txt"
        p.write_text("x")
        result = bulk_load_duckdb(str(p), table_name="test", database="memory")
        assert "COPY" in result
        assert "FORMAT" not in result


class TestBulkLoadSqlServer:
    """Tests for bulk_load_sqlserver function."""

    @patch("datablade.sql.bulk_load.subprocess.run")
    @patch("datablade.sql.bulk_load.log_debug")
    def test_uses_arg_list_and_redacts_password(
        self, mock_log_debug, mock_run, sample_csv_file
    ):
        mock_run.return_value = Mock(returncode=0, stdout=b"", stderr=b"")
        password = "SuperSecretPassword!"

        bulk_load_sqlserver(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            server="localhost",
            username="user",
            password=password,
            verbose=True,
        )

        assert mock_run.call_count == 1
        args, kwargs = mock_run.call_args
        assert isinstance(args[0], list)
        assert kwargs.get("shell") is False
        assert kwargs.get("check") is True

        # Ensure debug logging doesn't leak the password
        logged = "\n".join(str(c.args[0]) for c in mock_log_debug.call_args_list)
        assert password not in logged
        assert "***REDACTED***" in logged

    @patch("datablade.sql.bulk_load.subprocess.run")
    def test_bulk_load_sqlserver_logs_stdout(self, mock_run, sample_csv_file):
        mock_run.return_value = Mock(returncode=0, stdout=b"OK\n", stderr=b"")
        bulk_load_sqlserver(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            server="localhost",
            username="user",
            password="p",
            verbose=True,
        )
        assert mock_run.call_count == 1

    @patch("datablade.sql.bulk_load.subprocess.run")
    def test_bulk_load_sqlserver_raises_on_called_process_error(
        self, mock_run, sample_csv_file
    ):
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1,
            cmd=["bcp"],
            stderr=b"BAD\n",
        )

        with pytest.raises(subprocess.CalledProcessError):
            bulk_load_sqlserver(
                file_path=sample_csv_file,
                table_name="t",
                database="db",
                server="localhost",
                username="user",
                password="p",
                verbose=True,
            )

    def test_validate_bulk_load_params_sqlserver_requires_credentials(self, tmp_path):
        from datablade.sql.bulk_load import _validate_bulk_load_params

        p = tmp_path / "data.csv"
        p.write_text("x")
        with pytest.raises(ValueError, match="server is required"):
            _validate_bulk_load_params(
                str(p),
                table_name="t",
                database="db",
                server=None,
                username="u",
                password="p",
                dialect=Dialect.SQLSERVER,
            )


class TestBulkLoadValidation:
    def test_validate_bulk_load_params_requires_file_path(self):
        from datablade.sql.bulk_load import _validate_bulk_load_params

        with pytest.raises(ValueError, match="file_path must be provided"):
            _validate_bulk_load_params(
                None,  # type: ignore[arg-type]
                table_name="t",
                database="db",
                dialect=Dialect.POSTGRES,
            )

    def test_validate_bulk_load_params_requires_table_and_database(self, tmp_path):
        from datablade.sql.bulk_load import _validate_bulk_load_params

        p = tmp_path / "data.csv"
        p.write_text("x")
        with pytest.raises(ValueError, match="table_name must be a non-empty string"):
            _validate_bulk_load_params(
                str(p),
                table_name=" ",
                database="db",
                dialect=Dialect.POSTGRES,
            )
        with pytest.raises(ValueError, match="database must be a non-empty string"):
            _validate_bulk_load_params(
                str(p),
                table_name="t",
                database=" ",
                dialect=Dialect.POSTGRES,
            )
        with pytest.raises(ValueError, match="username is required"):
            _validate_bulk_load_params(
                str(p),
                table_name="t",
                database="db",
                server="s",
                username=None,
                password="p",
                dialect=Dialect.SQLSERVER,
            )
        with pytest.raises(ValueError, match="password is required"):
            _validate_bulk_load_params(
                str(p),
                table_name="t",
                database="db",
                server="s",
                username="u",
                password=None,
                dialect=Dialect.SQLSERVER,
            )

    @patch("datablade.sql.bulk_load._validate_bulk_load_params")
    def test_validate_requires_server_username_password(
        self, mock_validate, sample_csv_file
    ):
        """Exercise _validate_bulk_load_params via bulk_load_sqlserver inputs."""
        # For this test we don't want to hit filesystem, so just assert validation is called.
        mock_validate.return_value = sample_csv_file
        with pytest.raises(TypeError):
            # missing required params should be caught by python signature/type, not our validation
            bulk_load_sqlserver(file_path=sample_csv_file, table_name="t", database="db")  # type: ignore


class TestBulkLoadRouter:
    """Tests for bulk_load() routing logic."""

    def test_bulk_load_routes_postgres(self, sample_csv_file, mocker):
        mocked = mocker.patch(
            "datablade.sql.bulk_load.bulk_load_postgres", return_value="CMD"
        )
        result = bulk_load(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            dialect=Dialect.POSTGRES,
        )
        assert result == "CMD"
        assert mocked.call_count == 1

    def test_bulk_load_routes_mysql(self, sample_csv_file, mocker):
        mocked = mocker.patch(
            "datablade.sql.bulk_load.bulk_load_mysql", return_value="CMD"
        )
        result = bulk_load(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            dialect=Dialect.MYSQL,
        )
        assert result == "CMD"
        assert mocked.call_count == 1

    def test_bulk_load_routes_duckdb(self, sample_csv_file, mocker):
        mocked = mocker.patch(
            "datablade.sql.bulk_load.bulk_load_duckdb", return_value="CMD"
        )
        result = bulk_load(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            dialect=Dialect.DUCKDB,
        )
        assert result == "CMD"
        assert mocked.call_count == 1

    def test_bulk_load_routes_sqlserver_returns_none(self, sample_csv_file, mocker):
        mocked = mocker.patch("datablade.sql.bulk_load.bulk_load_sqlserver")
        result = bulk_load(
            file_path=sample_csv_file,
            table_name="t",
            database="db",
            dialect=Dialect.SQLSERVER,
            server="localhost",
            username="u",
            password="p",
        )
        assert result is None
        assert mocked.call_count == 1

    def test_bulk_load_unsupported_dialect_raises(self, sample_csv_file):
        with pytest.raises(NotImplementedError, match="Dialect not supported"):
            bulk_load(
                file_path=sample_csv_file,
                table_name="t",
                database="db",
                dialect="nope",  # type: ignore[arg-type]
            )


class TestWriteDataframeAndLoad:
    """Tests for write_dataframe_and_load() file writing branches."""

    def test_writes_parquet_then_calls_bulk_load(self, sample_df, temp_dir, mocker):
        out = temp_dir / "data.parquet"
        bulk = mocker.patch("datablade.sql.bulk_load.bulk_load", return_value="OK")
        to_parquet = mocker.patch.object(pd.DataFrame, "to_parquet")

        result = write_dataframe_and_load(
            df=sample_df,
            file_path=out,
            table_name="t",
            database="db",
            dialect=Dialect.DUCKDB,
            verbose=True,
        )
        assert result == "OK"
        assert to_parquet.call_count == 1
        assert bulk.call_count == 1

    def test_writes_csv_then_calls_bulk_load(self, sample_df, temp_dir, mocker):
        out = temp_dir / "data.csv"
        bulk = mocker.patch("datablade.sql.bulk_load.bulk_load", return_value="OK")
        to_csv = mocker.patch.object(pd.DataFrame, "to_csv")

        result = write_dataframe_and_load(
            df=sample_df,
            file_path=out,
            table_name="t",
            database="db",
            dialect=Dialect.POSTGRES,
            delimiter="|",
            verbose=True,
        )
        assert result == "OK"
        assert to_csv.call_count == 1
        assert bulk.call_count == 1

    def test_writes_other_suffix_uses_csv_writer(self, sample_df, temp_dir, mocker):
        out = temp_dir / "data.txt"
        bulk = mocker.patch("datablade.sql.bulk_load.bulk_load", return_value="OK")
        to_csv = mocker.patch.object(pd.DataFrame, "to_csv")

        result = write_dataframe_and_load(
            df=sample_df,
            file_path=out,
            table_name="t",
            database="db",
            dialect=Dialect.MYSQL,
            delimiter=",",
            verbose=True,
        )
        assert result == "OK"
        assert to_csv.call_count == 1
        assert bulk.call_count == 1

    def test_non_dataframe_raises_type_error(self, temp_dir):
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            write_dataframe_and_load(
                df=None,  # type: ignore[arg-type]
                file_path=temp_dir / "x.csv",
                table_name="t",
                database="db",
            )

    def test_generates_copy_command_parquet(self, sample_parquet_file):
        """Test COPY command generation for Parquet."""
        result = bulk_load_duckdb(
            sample_parquet_file, table_name="test", database="memory"
        )

        assert "COPY" in result
        assert "FORMAT PARQUET" in result
