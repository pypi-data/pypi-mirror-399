"""Optional facade class for datablade.

The canonical API is module-level functions (e.g., datablade.dataframes.read_file_iter).
This module provides a small convenience wrapper for users who prefer an object-style
entrypoint with shared defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Optional, Union

import pandas as pd

from .dataframes import (
    clean_dataframe_columns,
    read_file_iter,
    read_file_smart,
    read_file_to_parquets,
    stream_to_parquets,
    try_cast_string_columns_to_numeric,
)
from .sql import Dialect, generate_create_table, generate_create_table_from_parquet

PathLike = Union[str, Path]


@dataclass(frozen=True)
class Blade:
    """Convenience facade for common datablade workflows.

    Stores default options that are threaded through to the underlying functions.
    """

    memory_fraction: float = 0.5
    verbose: bool = False
    convert_types: bool = True

    def read(self, file_path: PathLike, **read_kwargs: Any) -> pd.DataFrame:
        return read_file_smart(
            file_path=file_path,
            memory_fraction=self.memory_fraction,
            verbose=self.verbose,
            **read_kwargs,
        )

    def iter(
        self,
        file_path: PathLike,
        *,
        chunksize: Optional[int] = None,
        **read_kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        return read_file_iter(
            file_path=file_path,
            chunksize=chunksize,
            memory_fraction=self.memory_fraction,
            verbose=self.verbose,
            **read_kwargs,
        )

    def partition_to_parquets(
        self,
        file_path: PathLike,
        output_dir: PathLike,
        *,
        output_prefix: str = "part",
        rows_per_file: Optional[int] = None,
        convert_types: Optional[bool] = None,
        **read_kwargs: Any,
    ):
        return read_file_to_parquets(
            file_path=file_path,
            output_dir=output_dir,
            output_prefix=output_prefix,
            rows_per_file=rows_per_file,
            memory_fraction=self.memory_fraction,
            convert_types=(
                self.convert_types if convert_types is None else convert_types
            ),
            verbose=self.verbose,
            **read_kwargs,
        )

    def stream_to_parquets(
        self,
        file_path: PathLike,
        output_dir: PathLike,
        *,
        output_prefix: str = "part",
        rows_per_file: Optional[int] = None,
        convert_types: Optional[bool] = None,
        **read_kwargs: Any,
    ):
        return stream_to_parquets(
            file_path=file_path,
            output_dir=output_dir,
            output_prefix=output_prefix,
            rows_per_file=rows_per_file,
            memory_fraction=self.memory_fraction,
            convert_types=(
                self.convert_types if convert_types is None else convert_types
            ),
            verbose=self.verbose,
            **read_kwargs,
        )

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_dataframe_columns(df, verbose=self.verbose)

    def cast_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        return try_cast_string_columns_to_numeric(df, verbose=self.verbose)

    def create_table_sql(
        self,
        df: pd.DataFrame,
        *,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        table: str = "table",
        drop_existing: bool = True,
        dialect: Dialect = Dialect.SQLSERVER,
    ) -> str:
        return generate_create_table(
            df=df,
            catalog=catalog,
            schema=schema,
            table=table,
            drop_existing=drop_existing,
            dialect=dialect,
            verbose=self.verbose,
        )

    def create_table_sql_from_parquet(
        self,
        parquet_path: str,
        *,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        table: str = "table",
        drop_existing: bool = True,
        dialect: Dialect = Dialect.SQLSERVER,
    ) -> str:
        return generate_create_table_from_parquet(
            parquet_path=parquet_path,
            catalog=catalog,
            schema=schema,
            table=table,
            drop_existing=drop_existing,
            dialect=dialect,
            verbose=self.verbose,
        )
