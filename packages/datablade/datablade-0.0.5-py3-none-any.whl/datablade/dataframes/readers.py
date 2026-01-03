"""
Memory-aware file reading utilities with Polars support.

This module provides intelligent file reading that:
- Estimates memory requirements before loading
- Automatically chunks large files
- Uses Polars for high-performance reading when available
- Writes large files to multiple Parquet partitions
"""

import pathlib
from typing import Iterator, List, Optional, Union

import pandas as pd
import pyarrow.parquet as pq

from ..utils.logging import log_debug, log_info, log_warning


def _normalize_text_delimiter_kwargs(suffix: str, read_kwargs: dict) -> dict:
    """Normalize delimiter/sep kwargs for delimited text formats.

    - For TSV, default to tab separator unless the caller supplied one.
    - For CSV/TXT, leave pandas defaults unless the caller supplied one.
    """
    if suffix not in (".csv", ".tsv", ".txt"):
        return read_kwargs

    if "sep" in read_kwargs or "delimiter" in read_kwargs:
        return read_kwargs

    if suffix == ".tsv":
        out = dict(read_kwargs)
        out["sep"] = "\t"
        return out

    return read_kwargs


def _polars_scan_csv_kwargs(suffix: str, read_kwargs: dict) -> dict:
    """Best-effort mapping of pandas-style kwargs to polars scan_csv kwargs."""
    # Polars uses `separator` (not `sep`). We only map delimiters because other
    # pandas kwargs are not generally compatible.
    if "sep" in read_kwargs:
        return {"separator": read_kwargs["sep"]}
    if "delimiter" in read_kwargs:
        return {"separator": read_kwargs["delimiter"]}
    if suffix == ".tsv":
        return {"separator": "\t"}
    return {}


def _infer_parquet_batch_rows(
    file_path: pathlib.Path,
    parquet_file: pq.ParquetFile,
    memory_fraction: float,
    verbose: bool,
) -> int:
    """Infer an approximate Parquet batch size (rows) to keep memory bounded."""
    try:
        available_memory = _get_available_memory()
        target_memory = int(available_memory * memory_fraction)
        file_size = file_path.stat().st_size
        num_rows = int(getattr(parquet_file.metadata, "num_rows", 0) or 0)
        if num_rows <= 0 or file_size <= 0 or target_memory <= 0:
            return 65_536

        # Parquet is compressed on disk; materialized batches are larger.
        # We use a conservative multiplier to avoid overshooting.
        bytes_per_row_on_disk = file_size / num_rows
        inflated_bytes_per_row = max(1.0, bytes_per_row_on_disk * 3.0)
        batch_rows = int(target_memory / inflated_bytes_per_row)

        # Keep within sane bounds.
        batch_rows = max(1_024, min(1_000_000, batch_rows))
        log_debug(f"Auto Parquet batch_rows={batch_rows}", verbose)
        return batch_rows
    except Exception:
        return 65_536


def _get_available_memory() -> int:
    """Get available system memory in bytes."""
    try:
        import psutil

        return psutil.virtual_memory().available
    except ImportError:
        log_warning("psutil not installed; assuming 4GB available memory", verbose=True)
        return 4 * 1024 * 1024 * 1024


def _estimate_file_memory(file_path: pathlib.Path, sample_rows: int = 1000) -> int:
    """
    Estimate memory required to load a file by sampling.

    Returns estimated bytes needed to load entire file.
    """
    file_size = file_path.stat().st_size
    suffix = file_path.suffix.lower()

    if suffix == ".parquet":
        return file_size * 3

    if suffix in (".csv", ".tsv", ".txt"):
        try:
            sample_kwargs = {}
            if suffix == ".tsv":
                sample_kwargs["sep"] = "\t"

            sample = pd.read_csv(file_path, nrows=sample_rows, **sample_kwargs)
            memory_per_row = sample.memory_usage(deep=True).sum() / len(sample)
            bytes_per_row = file_size / max(1, _count_lines_estimate(file_path))
            estimated_rows = file_size / bytes_per_row
            return int(memory_per_row * estimated_rows * 1.2)
        except Exception:
            return file_size * 3

    if suffix in (".xlsx", ".xls"):
        return file_size * 10

    return file_size * 3


def _count_lines_estimate(file_path: pathlib.Path, sample_size: int = 65536) -> int:
    """Estimate number of lines in a file by sampling."""
    file_size = file_path.stat().st_size
    with open(file_path, "rb") as f:
        sample = f.read(sample_size)
        lines_in_sample = sample.count(b"\n")

    if lines_in_sample == 0:
        return 1

    return int(file_size * lines_in_sample / len(sample))


def read_file_chunked(
    file_path: Union[str, pathlib.Path],
    chunksize: Optional[int] = None,
    memory_fraction: float = 0.5,
    verbose: bool = False,
    **read_kwargs,
) -> Iterator[pd.DataFrame]:
    """
    Read a file in chunks, automatically determining chunk size based on available memory.

    Args:
        file_path: Path to the file to read.
        chunksize: Optional explicit chunk size (rows). If None, auto-calculated.
        memory_fraction: Fraction of available memory to use (default: 0.5).
        verbose: If True, logs progress messages.
        **read_kwargs: Additional arguments passed to pandas read function.

    Yields:
        DataFrame chunks.

    Raises:
        ValueError: If file does not exist or format is unsupported.
    """
    path = pathlib.Path(file_path)
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    suffix = path.suffix.lower()

    if suffix == ".parquet":
        parquet_file = pq.ParquetFile(path)
        batch_rows = chunksize
        if batch_rows is None:
            batch_rows = _infer_parquet_batch_rows(
                file_path=path,
                parquet_file=parquet_file,
                memory_fraction=memory_fraction,
                verbose=verbose,
            )

        for batch in parquet_file.iter_batches(
            batch_size=int(batch_rows), use_threads=True
        ):
            yield batch.to_pandas()
            log_debug(f"Read batch of {len(batch)} rows from parquet.", verbose)
        return

    if suffix not in (".csv", ".tsv", ".txt"):
        raise ValueError(f"Unsupported file format for chunked reading: {suffix}")

    if chunksize is None:
        available_memory = _get_available_memory()
        target_memory = int(available_memory * memory_fraction)
        estimated_total = _estimate_file_memory(path)

        if estimated_total <= target_memory:
            log_info(
                f"File fits in memory ({estimated_total / 1e6:.1f}MB); reading all at once.",
                verbose,
            )
            normalized_kwargs = _normalize_text_delimiter_kwargs(suffix, read_kwargs)
            df = pd.read_csv(path, **normalized_kwargs)
            yield df
            return

        total_lines = _count_lines_estimate(path)
        memory_per_row = estimated_total / max(1, total_lines)
        chunksize = max(1000, int(target_memory / memory_per_row))
        log_info(
            f"File too large ({estimated_total / 1e6:.1f}MB); reading in chunks of {chunksize} rows.",
            verbose,
        )

    chunk_num = 0
    normalized_kwargs = _normalize_text_delimiter_kwargs(suffix, read_kwargs)
    for chunk in pd.read_csv(path, chunksize=chunksize, **normalized_kwargs):
        chunk_num += 1
        log_debug(f"Read chunk {chunk_num} with {len(chunk)} rows.", verbose)
        yield chunk


def read_file_iter(
    file_path: Union[str, pathlib.Path],
    chunksize: Optional[int] = None,
    memory_fraction: float = 0.5,
    verbose: bool = False,
    **read_kwargs,
) -> Iterator[pd.DataFrame]:
    """Stream a file as an iterator of DataFrame chunks.

    This is the "never materialize" API: unlike read_file_smart(), this function
    does not concatenate chunks into a single DataFrame.

    Supported streaming formats:
    - .csv / .tsv / .txt  (via pandas chunking)
    - .parquet            (via pyarrow iter_batches)
    - .json               (JSON Lines only: requires lines=True; uses pandas chunks)

    Non-streaming formats:
    - .xlsx / .xls are loaded fully and yielded as a single DataFrame (only if
      the file is estimated to fit within memory_fraction of available memory).

    Raises:
        ValueError: If the file is missing, unsupported, or too large for a
            non-streaming format.
    """
    path = pathlib.Path(file_path)
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    suffix = path.suffix.lower()

    if suffix in (".csv", ".tsv", ".txt", ".parquet"):
        yield from read_file_chunked(
            file_path=path,
            chunksize=chunksize,
            memory_fraction=memory_fraction,
            verbose=verbose,
            **read_kwargs,
        )
        return

    if suffix == ".json":
        # pandas can stream JSON only for JSON Lines (one JSON object per line).
        lines = bool(read_kwargs.get("lines", False))
        if not lines:
            available_memory = _get_available_memory()
            target_memory = int(available_memory * memory_fraction)
            estimated_total = _estimate_file_memory(path)
            if estimated_total > target_memory:
                raise ValueError(
                    "JSON streaming requires lines=True (JSON Lines) or the file must fit in memory. "
                    "Consider converting to JSON Lines or using read_file_to_parquets/read_file_chunked for delimited text."
                )
            yield pd.read_json(path, **read_kwargs)
            return

        # JSON Lines streaming.
        if chunksize is None:
            available_memory = _get_available_memory()
            target_memory = int(available_memory * memory_fraction)
            estimated_total = _estimate_file_memory(path)

            if estimated_total <= target_memory:
                yield pd.read_json(path, **read_kwargs)
                return

            total_lines = _count_lines_estimate(path)
            memory_per_line = estimated_total / max(1, total_lines)
            chunksize = max(1000, int(target_memory / max(1.0, memory_per_line)))
            log_info(
                f"JSON Lines too large ({estimated_total / 1e6:.1f}MB); streaming in chunks of {chunksize} rows.",
                verbose,
            )

        # pandas returns a TextFileReader-like iterator when chunksize is provided.
        json_iter = pd.read_json(path, chunksize=chunksize, **read_kwargs)
        for i, chunk in enumerate(json_iter, start=1):
            log_debug(f"Read json chunk {i} with {len(chunk)} rows.", verbose)
            yield chunk
        return

    if suffix in (".xlsx", ".xls"):
        available_memory = _get_available_memory()
        target_memory = int(available_memory * memory_fraction)
        estimated_total = _estimate_file_memory(path)
        if estimated_total > target_memory:
            raise ValueError(
                f"Excel file is estimated too large to load safely ({estimated_total / 1e6:.1f}MB). "
                "Excel streaming is not supported; consider exporting to CSV/Parquet first."
            )
        yield pd.read_excel(path, **read_kwargs)
        return

    raise ValueError(f"Unsupported file format for streaming: {suffix}")


def read_file_to_parquets(
    file_path: Union[str, pathlib.Path],
    output_dir: Union[str, pathlib.Path],
    output_prefix: str = "part",
    rows_per_file: Optional[int] = None,
    memory_fraction: float = 0.5,
    convert_types: bool = True,
    verbose: bool = False,
    **read_kwargs,
) -> List[pathlib.Path]:
    """
    Read a large file and write it to multiple Parquet files if it doesn't fit in memory.

    Args:
        file_path: Path to the input file.
        output_dir: Directory where Parquet files will be written.
        output_prefix: Prefix for output file names (default: "part").
        rows_per_file: Optional explicit rows per output file. If None, auto-calculated.
        memory_fraction: Fraction of available memory to use.
        convert_types: If True, attempts to convert string columns to numeric.
        verbose: If True, logs progress messages.
        **read_kwargs: Additional arguments passed to pandas read function.

    Returns:
        List of paths to the created Parquet files.

    Raises:
        ValueError: If file does not exist or format is unsupported.
    """
    # Import here to avoid circular imports
    from .frames import clean_dataframe_columns, try_cast_string_columns_to_numeric

    path = pathlib.Path(file_path)
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_files: List[pathlib.Path] = []
    part_num = 0

    for chunk in read_file_chunked(
        file_path=path,
        chunksize=rows_per_file,
        memory_fraction=memory_fraction,
        verbose=verbose,
        **read_kwargs,
    ):
        chunk = clean_dataframe_columns(chunk, verbose=verbose)
        if convert_types:
            chunk = try_cast_string_columns_to_numeric(chunk, verbose=verbose)

        output_file = output_path / f"{output_prefix}_{part_num:05d}.parquet"
        chunk.to_parquet(output_file, index=False)
        output_files.append(output_file)

        log_info(f"Wrote {len(chunk)} rows to {output_file}", verbose)
        part_num += 1

    log_info(f"Created {len(output_files)} Parquet files in {output_path}", verbose)
    return output_files


def stream_to_parquets(
    file_path: Union[str, pathlib.Path],
    output_dir: Union[str, pathlib.Path],
    output_prefix: str = "part",
    rows_per_file: Optional[int] = None,
    memory_fraction: float = 0.5,
    convert_types: bool = True,
    verbose: bool = False,
    **read_kwargs,
) -> List[pathlib.Path]:
    """Stream a file and write it to Parquet partitions without materializing.

    This helper is the "no concat" companion to read_file_to_parquets(). It uses
    read_file_iter() under the hood and writes each incoming chunk to a separate
    Parquet file.

    Args:
        file_path: Input file path.
        output_dir: Directory where Parquet partitions are written.
        output_prefix: Output filename prefix.
        rows_per_file: Desired rows per partition. For streaming formats this
            is passed as chunksize; if None, chunk sizes are chosen automatically
            based on memory_fraction.
        memory_fraction: Fraction of available memory to use when auto-sizing.
        convert_types: If True, attempts to convert numeric-looking strings.
        verbose: If True, logs progress.
        **read_kwargs: Passed to the underlying reader.

    Returns:
        List of Parquet file paths.

    Raises:
        ValueError: If the input is missing/unsupported.
    """
    from .frames import clean_dataframe_columns, try_cast_string_columns_to_numeric

    path = pathlib.Path(file_path)
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_files: List[pathlib.Path] = []
    part_num = 0

    for chunk in read_file_iter(
        file_path=path,
        chunksize=rows_per_file,
        memory_fraction=memory_fraction,
        verbose=verbose,
        **read_kwargs,
    ):
        chunk = clean_dataframe_columns(chunk, verbose=verbose)
        if convert_types:
            chunk = try_cast_string_columns_to_numeric(chunk, verbose=verbose)

        output_file = output_path / f"{output_prefix}_{part_num:05d}.parquet"
        chunk.to_parquet(output_file, index=False)
        output_files.append(output_file)

        log_info(f"Wrote {len(chunk)} rows to {output_file}", verbose)
        part_num += 1

    log_info(f"Created {len(output_files)} Parquet files in {output_path}", verbose)
    return output_files


def read_file_smart(
    file_path: Union[str, pathlib.Path],
    use_polars: bool = True,
    memory_fraction: float = 0.5,
    verbose: bool = False,
    **read_kwargs,
) -> pd.DataFrame:
    """
    Intelligently read a file, using Polars for large files if available.

    For files that fit in memory, reads directly. For large files, uses
    Polars lazy evaluation or pandas chunking as a fallback.

    Args:
        file_path: Path to the file to read.
        use_polars: If True and Polars is available, uses Polars for large files.
        memory_fraction: Fraction of available memory to use.
        verbose: If True, logs progress messages.
        **read_kwargs: Additional arguments passed to the read function.

    Returns:
        DataFrame with the file contents.

    Raises:
        ValueError: If file does not exist or format is unsupported.
    """
    path = pathlib.Path(file_path)
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    suffix = path.suffix.lower()
    available_memory = _get_available_memory()
    target_memory = int(available_memory * memory_fraction)
    estimated_memory = _estimate_file_memory(path)

    fits_in_memory = estimated_memory <= target_memory

    log_debug(
        f"File: {path.name}, Estimated: {estimated_memory / 1e6:.1f}MB, "
        f"Available: {target_memory / 1e6:.1f}MB, Fits: {fits_in_memory}",
        verbose,
    )

    # Try Polars for better performance on large files
    if use_polars and not fits_in_memory:
        try:
            import polars as pl

            log_info(
                f"Using Polars for large file ({estimated_memory / 1e6:.1f}MB)", verbose
            )

            if suffix == ".parquet":
                lf = pl.scan_parquet(path)
            elif suffix in (".csv", ".tsv", ".txt"):
                lf = pl.scan_csv(path, **_polars_scan_csv_kwargs(suffix, read_kwargs))
            else:
                raise ValueError(f"Unsupported format for Polars: {suffix}")

            df_polars = lf.collect(streaming=True)
            log_info(f"Polars read {len(df_polars)} rows.", verbose)
            return df_polars.to_pandas()

        except ImportError:
            log_warning(
                "Polars not installed; falling back to pandas chunked reading.", verbose
            )
        except Exception as e:
            log_warning(f"Polars failed: {e}; falling back to pandas.", verbose)

    # Direct read for small files
    if fits_in_memory:
        log_info(
            f"Reading file directly ({estimated_memory / 1e6:.1f}MB fits in memory).",
            verbose,
        )
        if suffix == ".parquet":
            return pd.read_parquet(path, **read_kwargs)
        elif suffix in (".csv", ".tsv", ".txt"):
            normalized_kwargs = _normalize_text_delimiter_kwargs(suffix, read_kwargs)
            return pd.read_csv(path, **normalized_kwargs)
        elif suffix in (".xlsx", ".xls"):
            return pd.read_excel(path, **read_kwargs)
        elif suffix == ".json":
            return pd.read_json(path, **read_kwargs)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    # Chunked reading for large files when Polars isn't available
    log_info(f"Reading large file in chunks ({estimated_memory / 1e6:.1f}MB).", verbose)
    normalized_kwargs = _normalize_text_delimiter_kwargs(suffix, read_kwargs)
    return pd.concat(
        read_file_chunked(
            file_path=path,
            memory_fraction=memory_fraction,
            verbose=verbose,
            **normalized_kwargs,
        ),
        ignore_index=True,
    )
