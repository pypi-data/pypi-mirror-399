"""Integration tests for datablade package."""

import pandas as pd
import pytest

import datablade
from datablade import (
    configure_logging,
    dataframes,
    io,
    read_file_smart,
    sql,
    utils,
)


class TestPackageImports:
    """Test that all modules can be imported correctly."""

    def test_import_main_modules(self):
        """Test importing main modules."""
        assert dataframes is not None
        assert io is not None
        assert utils is not None
        assert sql is not None

    def test_import_convenience_functions(self):
        """Test that convenience re-exports work."""
        assert callable(configure_logging)
        assert callable(read_file_smart)
        assert hasattr(datablade, "Blade")


class TestBladeFacade:
    def test_blade_iter_and_stream_to_parquets(self, sample_csv_file, temp_dir):
        import pandas as pd

        from datablade import Blade

        blade = Blade(memory_fraction=0.5, verbose=False, convert_types=False)

        chunks = list(blade.iter(sample_csv_file, chunksize=2))
        assert len(chunks) > 1

        out_dir = temp_dir / "blade_parts"
        files = blade.stream_to_parquets(sample_csv_file, out_dir, rows_per_file=2)
        assert len(files) > 1
        combined = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        original = pd.read_csv(sample_csv_file)
        assert len(combined) == len(original)

    def test_blade_create_table_sql(self, sample_df):
        from datablade import Blade
        from datablade.sql import Dialect

        blade = Blade(verbose=False)
        ddl = blade.create_table_sql(
            sample_df, table="my_table", dialect=Dialect.POSTGRES
        )
        assert "CREATE TABLE" in ddl
        assert "my_table" in ddl


class TestEndToEndWorkflow:
    """Test realistic end-to-end workflows."""

    def test_dataframe_processing_workflow(self, sample_df):
        """Test complete DataFrame processing workflow."""
        from datablade.dataframes import (
            clean_dataframe_columns,
            pandas_to_parquet_table,
            try_cast_string_columns_to_numeric,
        )

        # Step 1: Clean columns
        df = clean_dataframe_columns(sample_df)
        assert df is not None

        # Step 2: Convert types
        df = try_cast_string_columns_to_numeric(df)
        assert df is not None

        # Step 3: Convert to Parquet table
        table = pandas_to_parquet_table(df)
        assert table is not None

    def test_sql_generation_workflow(self, sample_df):
        """Test SQL generation workflow."""
        from datablade.sql import Dialect, generate_create_table

        # Generate CREATE TABLE for different dialects
        for dialect in [Dialect.SQLSERVER, Dialect.POSTGRES, Dialect.MYSQL]:
            sql = generate_create_table(sample_df, table="test_table", dialect=dialect)
            assert "CREATE TABLE" in sql
            assert "test_table" in sql

    def test_file_reading_workflow(self, sample_csv_file, temp_dir):
        """Test file reading and processing workflow."""
        from datablade.dataframes import (
            clean_dataframe_columns,
            read_file_smart,
            read_file_to_parquets,
        )

        # Step 1: Read file
        df = read_file_smart(sample_csv_file)
        assert len(df) > 0

        # Step 2: Clean data
        df = clean_dataframe_columns(df)

        # Step 3: Write to partitioned parquets
        output_dir = temp_dir / "parquets"
        files = read_file_to_parquets(sample_csv_file, output_dir, rows_per_file=2)
        assert len(files) > 0

        # Step 4: Verify we can read back
        combined = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        assert len(combined) == len(df)


class TestBackwardCompatibility:
    """Test backward compatibility with legacy imports."""

    def test_core_imports_still_work(self):
        """Test that legacy core imports still work."""
        from datablade.core.frames import clean_dataframe_columns
        from datablade.core.lists import flatten
        from datablade.core.strings import sql_quotename

        assert callable(clean_dataframe_columns)
        assert callable(sql_quotename)
        assert callable(flatten)

    def test_new_imports_work(self):
        """Test that new modular imports work."""
        from datablade.dataframes import clean_dataframe_columns
        from datablade.utils import flatten, sql_quotename

        assert callable(clean_dataframe_columns)
        assert callable(sql_quotename)
        assert callable(flatten)


class TestErrorHandling:
    """Test error handling across modules."""

    def test_invalid_inputs_raise_appropriate_errors(self):
        """Test that invalid inputs raise appropriate errors."""
        from datablade.dataframes import clean_dataframe_columns
        from datablade.sql import Dialect, quote_identifier
        from datablade.utils import sql_quotename

        # DataFrame functions
        with pytest.raises(ValueError):
            clean_dataframe_columns(None)

        # String functions
        with pytest.raises(ValueError):
            sql_quotename(None)

        # SQL functions
        with pytest.raises(ValueError):
            quote_identifier(None, Dialect.POSTGRES)

    def test_type_errors_for_wrong_types(self):
        """Test that wrong types raise TypeErrors."""
        from datablade.dataframes import clean_dataframe_columns
        from datablade.utils import sql_quotename

        with pytest.raises(TypeError):
            clean_dataframe_columns("not a dataframe")

        with pytest.raises(TypeError):
            sql_quotename(123)


class TestLoggingIntegration:
    """Test logging integration across modules."""

    def test_configure_logging_affects_all_modules(self, caplog):
        """Test that configuring logging affects all modules."""
        import logging

        from datablade import configure_logging
        from datablade.dataframes import clean_dataframe_columns

        # Configure logging to DEBUG level
        configure_logging(level=logging.DEBUG)

        # Create a simple DataFrame
        df = pd.DataFrame({"A": [1, 2, 3]})

        # This should generate log messages
        with caplog.at_level(logging.DEBUG, logger="datablade"):
            result = clean_dataframe_columns(df, verbose=True)

        assert result is not None
        # Check that some logging occurred
        assert len(caplog.records) > 0


class TestPackageMetadata:
    """Test package metadata and version info."""

    def test_version_exists(self):
        """Test that package version is defined."""
        import datablade

        assert hasattr(datablade, "__version__")
        assert isinstance(datablade.__version__, str)

    def test_all_exports(self):
        """Test that __all__ is defined and contains expected exports."""
        import datablade

        assert hasattr(datablade, "__all__")
        assert "dataframes" in datablade.__all__
        assert "io" in datablade.__all__
        assert "utils" in datablade.__all__
        assert "sql" in datablade.__all__
