"""Tests for datablade.dataframes module."""

import pandas as pd
import pyarrow as pa
import pytest

from datablade.dataframes import (
    clean_dataframe_columns,
    generate_parquet_schema,
    generate_sql_server_create_table_string,
    pandas_to_parquet_table,
    try_cast_string_columns_to_numeric,
    write_to_file_and_sql,
)


class TestTryCastStringColumnsToNumeric:
    """Tests for try_cast_string_columns_to_numeric function."""

    def test_convert_all_numeric_strings(self, sample_df_with_strings):
        """Test converting columns with all numeric strings."""
        result = try_cast_string_columns_to_numeric(sample_df_with_strings)
        assert pd.api.types.is_numeric_dtype(result["id"])
        assert pd.api.types.is_numeric_dtype(result["value"])
        assert result["text"].dtype == "object"  # Should remain string

    def test_convert_partial_with_nans(self):
        """Test partial conversion with NaN values."""
        df = pd.DataFrame(
            {
                "mixed": ["1", "2", "three", "4"],
            }
        )
        result = try_cast_string_columns_to_numeric(df, convert_partial=True)
        assert pd.api.types.is_numeric_dtype(result["mixed"])
        assert pd.isna(result.loc[2, "mixed"])  # 'three' becomes NaN

    def test_no_partial_conversion_by_default(self):
        """Test that partial conversion is disabled by default."""
        df = pd.DataFrame(
            {
                "mixed": ["1", "2", "three", "4"],
            }
        )
        result = try_cast_string_columns_to_numeric(df, convert_partial=False)
        assert result["mixed"].dtype == "object"  # Should remain string

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            try_cast_string_columns_to_numeric(None)

    def test_non_dataframe_raises_error(self):
        """Test that non-DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            try_cast_string_columns_to_numeric("not a dataframe")

    def test_bytes_like_columns_not_coerced(self):
        """Test that bytes-like object columns are not coerced to numeric."""
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        result = try_cast_string_columns_to_numeric(df)
        assert result["payload"].dtype == "object"
        assert result["payload"].tolist() == [b"\x00\x01", b"\x02\x03"]


class TestCleanDataframeColumns:
    """Tests for clean_dataframe_columns function."""

    def test_flatten_multiindex_columns(self, sample_df_multiindex):
        """Test flattening MultiIndex columns."""
        result = clean_dataframe_columns(sample_df_multiindex)
        assert not isinstance(result.columns, pd.MultiIndex)
        assert "A_x" in result.columns
        assert "A_y" in result.columns

    def test_convert_column_names_to_strings(self):
        """Test converting non-string column names to strings."""
        df = pd.DataFrame([[1, 2, 3]], columns=[0, 1, 2])
        result = clean_dataframe_columns(df)
        assert all(isinstance(col, str) for col in result.columns)
        assert result.columns.tolist() == ["0", "1", "2"]

    def test_remove_duplicate_columns(self, sample_df_duplicates):
        """Test removing duplicate column names."""
        result = clean_dataframe_columns(sample_df_duplicates)
        assert len(result.columns) == 2
        assert result.columns.tolist() == ["A", "B"]

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            clean_dataframe_columns(None)

    def test_non_dataframe_raises_error(self):
        """Test that non-DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            clean_dataframe_columns("not a dataframe")


class TestGenerateParquetSchema:
    """Tests for generate_parquet_schema function."""

    def test_generates_pyarrow_schema(self, sample_df):
        """Test that a PyArrow schema is generated."""
        schema = generate_parquet_schema(sample_df)
        assert isinstance(schema, pa.Schema)
        assert len(schema) == len(sample_df.columns)

    def test_schema_includes_all_columns(self, sample_df):
        """Test that schema includes all DataFrame columns."""
        schema = generate_parquet_schema(sample_df)
        schema_names = [field.name for field in schema]
        assert set(schema_names) == set(sample_df.columns)

    def test_integer_type_optimization(self):
        """Test that integer types are optimized to smallest type."""
        df = pd.DataFrame({"small": [1, 2, 3, 4, 5]})
        schema = generate_parquet_schema(df)
        field = schema.field("small")
        assert field.type == pa.int8()  # Should use int8 for small values

    def test_nullable_fields(self, sample_df_with_nulls):
        """Test that nullable fields are correctly identified."""
        schema = generate_parquet_schema(sample_df_with_nulls)
        for field in schema:
            assert field.nullable  # All fields should be nullable

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            generate_parquet_schema(None)

    def test_bytes_object_column_maps_to_binary(self):
        """Test that bytes-like object columns are mapped to Arrow binary."""
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        schema = generate_parquet_schema(df)
        assert schema.field("payload").type == pa.binary()

    def test_tz_aware_datetime_maps_to_timestamp_with_tz(self):
        df = pd.DataFrame({"ts": pd.date_range("2024-01-01", periods=2, tz="UTC")})
        schema = generate_parquet_schema(df)
        assert schema.field("ts").type == pa.timestamp("ms", tz="UTC")

    def test_object_ints_infer_integer(self):
        df = pd.DataFrame({"n": pd.Series([1, 2, 3], dtype="object")})
        schema = generate_parquet_schema(df)
        assert pa.types.is_integer(schema.field("n").type)

    def test_object_floats_infer_float(self):
        df = pd.DataFrame({"x": pd.Series([1.1, 2.2, 3.3], dtype="object")})
        schema = generate_parquet_schema(df)
        assert schema.field("x").type == pa.float64()

    def test_object_bools_infer_bool(self):
        df = pd.DataFrame({"b": pd.Series([True, False, True], dtype="object")})
        schema = generate_parquet_schema(df)
        assert schema.field("b").type == pa.bool_()

    def test_object_mixed_falls_back_to_string(self):
        df = pd.DataFrame({"m": pd.Series(["a", 1, 2.2], dtype="object")})
        schema = generate_parquet_schema(df)
        assert schema.field("m").type == pa.string()

    def test_object_all_null_falls_back_to_string(self):
        df = pd.DataFrame({"m": pd.Series([None, None], dtype="object")})
        schema = generate_parquet_schema(df)
        assert schema.field("m").type == pa.string()


class TestPandasToParquetTable:
    """Tests for pandas_to_parquet_table function."""

    def test_converts_to_pyarrow_table(self, sample_df):
        """Test that DataFrame is converted to PyArrow table."""
        table = pandas_to_parquet_table(sample_df)
        assert isinstance(table, pa.Table)

    def test_table_has_same_rows(self, sample_df):
        """Test that table has same number of rows as DataFrame."""
        table = pandas_to_parquet_table(sample_df)
        assert len(table) == len(sample_df)

    def test_with_convert_enabled(self, sample_df_with_strings):
        """Test conversion with automatic type casting."""
        table = pandas_to_parquet_table(sample_df_with_strings, convert=True)
        # Check that numeric columns were converted
        df_result = table.to_pandas()
        assert pd.api.types.is_numeric_dtype(df_result["id"])

    def test_with_convert_disabled(self, sample_df_with_strings):
        """Test that conversion can be disabled."""
        table = pandas_to_parquet_table(sample_df_with_strings, convert=False)
        df_result = table.to_pandas()
        # String columns should remain as string/object
        assert df_result["id"].dtype == "object"

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            pandas_to_parquet_table(None)

    def test_bytes_object_column_round_trips(self):
        """Test that bytes-like columns remain binary in the Arrow table."""
        df = pd.DataFrame({"payload": [b"\x00\x01", b"\x02\x03"]})
        table = pandas_to_parquet_table(df, convert=True)
        assert table.schema.field("payload").type == pa.binary()

    def test_partial_conversion_enabled(self):
        df = pd.DataFrame({"mixed": ["1", "two", "3"]})
        table = pandas_to_parquet_table(df, convert=True, partial=True)
        out = table.to_pandas()
        assert pd.api.types.is_numeric_dtype(out["mixed"])
        assert pd.isna(out.loc[1, "mixed"])

    def test_preserve_index(self):
        df = pd.DataFrame({"a": [1, 2, 3]}, index=pd.Index([10, 11, 12], name="idx"))
        table = pandas_to_parquet_table(df, preserve_index=True, convert=False)
        out = table.to_pandas()
        # Preserve-index adds an index column, but the exact name can vary.
        index_cols = [
            c for c in out.columns if c.startswith("__index_level_") or c == "idx"
        ]
        assert index_cols, f"Expected an index column, got columns={list(out.columns)}"
        assert out[index_cols[0]].tolist() == [10, 11, 12]


class TestGenerateSqlServerCreateTableString:
    """Tests for generate_sql_server_create_table_string function."""

    def test_generates_sql_string(self, sample_df):
        """Test that SQL CREATE TABLE statement is generated."""
        sql = generate_sql_server_create_table_string(
            sample_df, catalog="testdb", schema="dbo", table="test_table"
        )
        assert isinstance(sql, str)
        assert "CREATE TABLE" in sql
        assert "test_table" in sql

    def test_includes_drop_statement_by_default(self, sample_df):
        """Test that DROP TABLE statement is included by default."""
        sql = generate_sql_server_create_table_string(
            sample_df, catalog="testdb", table="test_table", dropexisting=True
        )
        assert "DROP TABLE" in sql

    def test_no_drop_statement_when_disabled(self, sample_df):
        """Test that DROP TABLE can be omitted."""
        sql = generate_sql_server_create_table_string(
            sample_df, catalog="testdb", table="test_table", dropexisting=False
        )
        assert "DROP TABLE" not in sql

    def test_includes_all_columns(self, sample_df):
        """Test that all DataFrame columns are included."""
        sql = generate_sql_server_create_table_string(sample_df, table="test_table")
        for col in sample_df.columns:
            assert col in sql

    def test_none_df_raises_error(self):
        """Test that None DataFrame raises ValueError."""
        with pytest.raises(ValueError, match="df must be provided"):
            generate_sql_server_create_table_string(None)

    def test_empty_catalog_raises_error(self, sample_df):
        """Test that empty catalog raises ValueError."""
        with pytest.raises(ValueError, match="catalog must be a non-empty string"):
            generate_sql_server_create_table_string(sample_df, catalog="")

    def test_empty_schema_raises_error(self, sample_df):
        """Test that empty schema raises ValueError."""
        with pytest.raises(ValueError, match="schema must be a non-empty string"):
            generate_sql_server_create_table_string(sample_df, schema="")

    def test_empty_table_raises_error(self, sample_df):
        """Test that empty table name raises ValueError."""
        with pytest.raises(ValueError, match="table must be a non-empty string"):
            generate_sql_server_create_table_string(sample_df, table="")


class TestWriteToFileAndSql:
    """Tests for write_to_file_and_sql function."""

    def test_invalid_df_raises_error(self):
        """Test that invalid DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            write_to_file_and_sql(
                None, "test.csv", "table", "server", "db", "user", "pass"
            )

    def test_empty_file_path_raises_error(self, sample_df):
        """Test that empty file path raises ValueError."""
        with pytest.raises(ValueError, match="file_path must be a non-empty string"):
            write_to_file_and_sql(
                sample_df, "", "table", "server", "db", "user", "pass"
            )

    def test_empty_table_name_raises_error(self, sample_df):
        """Test that empty table name raises ValueError."""
        with pytest.raises(ValueError, match="table_name must be a non-empty string"):
            write_to_file_and_sql(
                sample_df, "test.csv", "", "server", "db", "user", "pass"
            )

    def test_empty_server_raises_error(self, sample_df):
        """Test that empty server raises ValueError."""
        with pytest.raises(ValueError, match="sql_server must be a non-empty string"):
            write_to_file_and_sql(
                sample_df, "test.csv", "table", "", "db", "user", "pass"
            )

    def test_empty_database_raises_error(self, sample_df):
        """Test that empty database raises ValueError."""
        with pytest.raises(ValueError, match="database must be a non-empty string"):
            write_to_file_and_sql(
                sample_df, "test.csv", "table", "server", "", "user", "pass"
            )

    def test_empty_username_raises_error(self, sample_df):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="username must be a non-empty string"):
            write_to_file_and_sql(
                sample_df, "test.csv", "table", "server", "db", "", "pass"
            )

    def test_empty_password_raises_error(self, sample_df):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="password must be provided"):
            write_to_file_and_sql(
                sample_df, "test.csv", "table", "server", "db", "user", ""
            )

    def test_uses_subprocess_arg_list_no_shell(self, sample_df, temp_dir, mocker):
        """Test that subprocess.run is invoked with args list and shell=False."""
        fake_process = mocker.Mock(returncode=0, stdout=b"", stderr=b"")
        run = mocker.patch(
            "datablade.dataframes.frames.subprocess.run", return_value=fake_process
        )
        mocker.patch("datablade.dataframes.frames.log_debug")

        out = temp_dir / "bcp_test.csv"
        write_to_file_and_sql(
            sample_df,
            str(out),
            "table",
            "server",
            "db",
            "user",
            "pass",
            verbose=True,
        )

        assert run.call_count == 1
        args, kwargs = run.call_args
        assert isinstance(args[0], list)
        assert kwargs.get("shell") is False
        assert kwargs.get("check") is True
