"""Tests for datablade.dataframes.readers module."""

import sys
import types

import pandas as pd
import pytest

from datablade.dataframes.readers import (
    _count_lines_estimate,
    _estimate_file_memory,
    _get_available_memory,
    read_file_chunked,
    read_file_iter,
    read_file_smart,
    read_file_to_parquets,
    stream_to_parquets,
)


class TestGetAvailableMemory:
    """Tests for _get_available_memory function."""

    def test_returns_positive_integer(self):
        """Test that function returns a positive integer."""
        memory = _get_available_memory()
        assert isinstance(memory, int)
        assert memory > 0

    def test_fallback_when_psutil_unavailable(self, monkeypatch):
        """Test fallback behavior when psutil is not available."""

        # Mock import to simulate psutil not being installed
        def mock_import(name, *args, **kwargs):
            if name == "psutil":
                raise ImportError("No module named 'psutil'")
            return __import__(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)
        memory = _get_available_memory()
        assert memory == 4 * 1024 * 1024 * 1024  # 4GB fallback


class TestEstimateFileMemory:
    """Tests for _estimate_file_memory function."""

    def test_estimate_csv_file(self, sample_csv_file):
        """Test memory estimation for CSV files."""
        memory = _estimate_file_memory(sample_csv_file)
        assert isinstance(memory, int)
        assert memory > 0

    def test_estimate_parquet_file(self, sample_parquet_file):
        """Test memory estimation for Parquet files."""
        memory = _estimate_file_memory(sample_parquet_file)
        assert isinstance(memory, int)
        assert memory > 0
        # Parquet estimate should be roughly 3x file size
        file_size = sample_parquet_file.stat().st_size
        assert memory > file_size


class TestCountLinesEstimate:
    """Tests for _count_lines_estimate function."""

    def test_estimate_lines_in_csv(self, sample_csv_file):
        """Test line count estimation for CSV."""
        estimated_lines = _count_lines_estimate(sample_csv_file)
        assert isinstance(estimated_lines, int)
        assert estimated_lines > 0

        # Verify accuracy by reading actual lines
        with open(sample_csv_file) as f:
            actual_lines = sum(1 for _ in f)

        # Estimate should be reasonably close (within 50%)
        assert 0.5 * actual_lines <= estimated_lines <= 2 * actual_lines


class TestReadFileChunked:
    """Tests for read_file_chunked function."""

    def test_read_csv_in_chunks(self, sample_csv_file):
        """Test reading CSV file in chunks."""
        chunks = list(read_file_chunked(sample_csv_file, chunksize=2))

        assert len(chunks) > 1  # Should have multiple chunks
        assert all(isinstance(chunk, pd.DataFrame) for chunk in chunks)

        # Concatenate chunks and verify total rows
        combined = pd.concat(chunks, ignore_index=True)
        original = pd.read_csv(sample_csv_file)
        assert len(combined) == len(original)

    def test_read_small_file_as_single_chunk(self, sample_csv_file):
        """Test that small files are read as a single chunk."""
        chunks = list(read_file_chunked(sample_csv_file, chunksize=None))

        # Small file should be read in one chunk
        assert len(chunks) == 1
        assert isinstance(chunks[0], pd.DataFrame)

    def test_read_parquet_file(self, sample_parquet_file):
        """Test reading Parquet file in chunks."""
        chunks = list(read_file_chunked(sample_parquet_file))

        assert len(chunks) >= 1
        assert all(isinstance(chunk, pd.DataFrame) for chunk in chunks)

    def test_nonexistent_file_raises_error(self):
        """Test that non-existent file raises ValueError."""
        with pytest.raises(ValueError, match="File does not exist"):
            list(read_file_chunked("/nonexistent/file.csv"))

    def test_unsupported_format_raises_error(self, temp_dir):
        """Test that unsupported file format raises ValueError."""
        unsupported_file = temp_dir / "test.bin"
        unsupported_file.write_bytes(b"\x00\x01\x02")

        with pytest.raises(ValueError, match="Unsupported file format"):
            list(read_file_chunked(unsupported_file))

    def test_auto_chunking_when_estimated_too_large(self, sample_csv_file, monkeypatch):
        """Force the auto-chunking branch by faking low memory and high estimate."""
        from datablade.dataframes import readers

        monkeypatch.setattr(readers, "_get_available_memory", lambda: 10_000)
        monkeypatch.setattr(
            readers, "_estimate_file_memory", lambda *_args, **_kwargs: 1_000_000_000
        )
        monkeypatch.setattr(
            readers, "_count_lines_estimate", lambda *_args, **_kwargs: 10_000
        )

        chunks = list(read_file_chunked(sample_csv_file, chunksize=None))
        assert len(chunks) >= 1
        assert all(isinstance(c, pd.DataFrame) for c in chunks)


class TestReadFileIter:
    """Tests for the streaming read_file_iter API."""

    def test_stream_csv_in_chunks(self, sample_csv_file):
        chunks = list(read_file_iter(sample_csv_file, chunksize=2))
        assert len(chunks) > 1
        combined = pd.concat(chunks, ignore_index=True)
        original = pd.read_csv(sample_csv_file)
        assert len(combined) == len(original)

    def test_stream_parquet_in_batches(self, sample_parquet_file):
        chunks = list(read_file_iter(sample_parquet_file, chunksize=2))
        assert len(chunks) >= 1
        combined = pd.concat(chunks, ignore_index=True)
        original = pd.read_parquet(sample_parquet_file)
        assert len(combined) == len(original)

    def test_stream_json_lines(self, temp_dir):
        # Create a JSON Lines file
        jsonl = temp_dir / "data.json"
        jsonl.write_text('{"a": 1}\n{"a": 2}\n{"a": 3}\n', encoding="utf-8")

        chunks = list(read_file_iter(jsonl, chunksize=1, lines=True))
        assert len(chunks) == 3
        combined = pd.concat(chunks, ignore_index=True)
        assert combined["a"].tolist() == [1, 2, 3]

    def test_excel_too_large_raises(self, temp_dir, monkeypatch):
        # We don't need a valid Excel file; we only need the suffix and the size checks.
        xlsx = temp_dir / "big.xlsx"
        xlsx.write_bytes(b"not really an xlsx")

        from datablade.dataframes import readers

        monkeypatch.setattr(readers, "_get_available_memory", lambda: 10_000)
        monkeypatch.setattr(
            readers, "_estimate_file_memory", lambda *_args, **_kwargs: 1_000_000_000
        )

        with pytest.raises(ValueError, match="Excel streaming is not supported"):
            list(read_file_iter(xlsx))


class TestReadFileToParquets:
    """Tests for read_file_to_parquets function."""

    def test_write_to_multiple_parquets(self, sample_csv_file, temp_dir):
        """Test writing CSV to multiple Parquet files."""
        output_dir = temp_dir / "output"

        files = read_file_to_parquets(
            sample_csv_file, output_dir, rows_per_file=2, convert_types=False
        )

        assert len(files) > 0
        assert all(f.exists() for f in files)
        assert all(f.suffix == ".parquet" for f in files)

    def test_output_files_named_correctly(self, sample_csv_file, temp_dir):
        """Test that output files are named with correct prefix and numbering."""
        output_dir = temp_dir / "output"

        files = read_file_to_parquets(
            sample_csv_file, output_dir, output_prefix="data", rows_per_file=2
        )

        assert all("data_" in f.name for f in files)
        assert files[0].name == "data_00000.parquet"

    def test_creates_output_directory(self, sample_csv_file, temp_dir):
        """Test that output directory is created if it doesn't exist."""
        output_dir = temp_dir / "nonexistent" / "nested" / "dir"

        files = read_file_to_parquets(sample_csv_file, output_dir, rows_per_file=2)

        assert output_dir.exists()
        assert len(files) > 0

    def test_verify_data_integrity(self, sample_csv_file, temp_dir):
        """Test that data integrity is maintained."""
        output_dir = temp_dir / "output"
        original = pd.read_csv(sample_csv_file)

        files = read_file_to_parquets(
            sample_csv_file, output_dir, rows_per_file=2, convert_types=False
        )

        # Read all parquet files and concatenate
        combined = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

        assert len(combined) == len(original)
        assert set(combined.columns) == set(original.columns)

    def test_convert_types_true_converts_numeric_strings(self, temp_dir):
        df = pd.DataFrame({"id": ["1", "2"], "value": ["3.1", "4.2"]})
        csv_path = temp_dir / "strings.csv"
        df.to_csv(csv_path, index=False)

        out_dir = temp_dir / "out"
        files = read_file_to_parquets(
            csv_path, out_dir, rows_per_file=1, convert_types=True
        )
        combined = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        assert pd.api.types.is_numeric_dtype(combined["id"])
        assert pd.api.types.is_numeric_dtype(combined["value"])


class TestStreamToParquets:
    def test_stream_csv_to_multiple_parquets(self, sample_csv_file, temp_dir):
        out_dir = temp_dir / "streamed"
        files = stream_to_parquets(
            sample_csv_file,
            out_dir,
            output_prefix="data",
            rows_per_file=2,
            convert_types=False,
        )

        assert len(files) > 1
        assert all(f.exists() and f.suffix == ".parquet" for f in files)
        assert files[0].name == "data_00000.parquet"

        original = pd.read_csv(sample_csv_file)
        combined = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        assert len(combined) == len(original)


class TestReadFileSmart:
    """Tests for read_file_smart function."""

    def test_read_small_csv_file(self, sample_csv_file):
        """Test reading a small CSV file."""
        df = read_file_smart(sample_csv_file, use_polars=False)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_read_parquet_file(self, sample_parquet_file):
        """Test reading a Parquet file."""
        df = read_file_smart(sample_parquet_file, use_polars=False)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_nonexistent_file_raises_error(self):
        """Test that non-existent file raises ValueError."""
        with pytest.raises(ValueError, match="File does not exist"):
            read_file_smart("/nonexistent/file.csv")

    def test_unsupported_format_raises_error(self, temp_dir):
        """Test that unsupported file format raises ValueError."""
        unsupported_file = temp_dir / "test.bin"
        unsupported_file.write_bytes(b"\x00\x01\x02")

        with pytest.raises(ValueError, match="Unsupported file format"):
            read_file_smart(unsupported_file, use_polars=False)

    @pytest.mark.skipif(not hasattr(pd, "__version__"), reason="Requires pandas")
    def test_falls_back_when_polars_unavailable(self, sample_csv_file, monkeypatch):
        """Test fallback to pandas when Polars is unavailable."""
        # This test verifies the fallback logic works
        df = read_file_smart(sample_csv_file, use_polars=True)
        assert isinstance(df, pd.DataFrame)

    def test_memory_fraction_parameter(self, sample_csv_file):
        """Test that memory_fraction parameter is respected."""
        # Read with different memory fractions
        df1 = read_file_smart(sample_csv_file, memory_fraction=0.8)
        df2 = read_file_smart(sample_csv_file, memory_fraction=0.2)

        # Both should succeed and return same data
        assert len(df1) == len(df2)
        pd.testing.assert_frame_equal(df1, df2)

    def test_polars_path_used_for_large_file(self, sample_csv_file, monkeypatch):
        """Inject a fake polars module to exercise the polars codepath."""
        from datablade.dataframes import readers

        monkeypatch.setattr(readers, "_get_available_memory", lambda: 10_000)
        monkeypatch.setattr(
            readers, "_estimate_file_memory", lambda *_args, **_kwargs: 1_000_000_000
        )

        expected = pd.read_csv(sample_csv_file)

        class _FakeLazy:
            def collect(self, streaming=True):
                class _FakeDF:
                    def to_pandas(self_inner):
                        return expected

                return _FakeDF()

        fake_polars = types.SimpleNamespace(
            scan_csv=lambda _p: _FakeLazy(), scan_parquet=lambda _p: _FakeLazy()
        )
        monkeypatch.setitem(sys.modules, "polars", fake_polars)

        df = read_file_smart(sample_csv_file, use_polars=True)
        pd.testing.assert_frame_equal(df, expected)

    def test_polars_failure_falls_back_to_chunked_concat(
        self, sample_csv_file, monkeypatch
    ):
        """Polars import succeeds but scan/collect fails; should fall back to pandas chunking."""
        from datablade.dataframes import readers

        monkeypatch.setattr(readers, "_get_available_memory", lambda: 10_000)
        monkeypatch.setattr(
            readers, "_estimate_file_memory", lambda *_args, **_kwargs: 1_000_000_000
        )

        class _FakeLazy:
            def collect(self, streaming=True):
                raise RuntimeError("boom")

        fake_polars = types.SimpleNamespace(
            scan_csv=lambda _p: _FakeLazy(), scan_parquet=lambda _p: _FakeLazy()
        )
        monkeypatch.setitem(sys.modules, "polars", fake_polars)

        # Replace chunked reader to avoid real chunking logic
        d1 = pd.DataFrame({"a": [1]})
        d2 = pd.DataFrame({"a": [2]})
        monkeypatch.setattr(
            readers, "read_file_chunked", lambda **_kwargs: iter([d1, d2])
        )

        df = read_file_smart(sample_csv_file, use_polars=True)
        assert df["a"].tolist() == [1, 2]

    def test_read_json_branch(self, temp_dir):
        path = temp_dir / "data.json"
        pd.DataFrame([{"a": 1}, {"a": 2}]).to_json(path, orient="records")
        df = read_file_smart(path, use_polars=False)
        assert df["a"].tolist() == [1, 2]
