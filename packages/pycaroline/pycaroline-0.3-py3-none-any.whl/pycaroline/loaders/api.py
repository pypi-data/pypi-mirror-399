"""Public API functions for file loading.

This module provides high-level functions for loading files and comparing
file-based data using the FileLoader class.
"""

from pathlib import Path
from typing import Any

import polars as pl

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult
from pycaroline.loaders.file_loader import FileLoader


def load_file(
    path: str | Path,
    format: str | None = None,
    **options: Any,
) -> pl.DataFrame:
    """Load a file into a polars DataFrame.

    This function provides a convenient way to load data from various file
    formats into a polars DataFrame. It supports automatic format detection
    based on file extension, or explicit format specification.

    Args:
        path: Path to the file to load.
        format: Optional format override (parquet, csv, xlsx, xls, json,
            ndjson, avro, ipc, feather). If None, auto-detects from extension.
        **options: Format-specific options passed to the loader.

    Returns:
        Polars DataFrame containing the file data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the format is not supported.
        FileLoadError: If the file cannot be loaded.

    Examples:
        Load a CSV file with auto-detection:

        >>> df = load_file("data.csv")

        Load a CSV file with custom delimiter:

        >>> df = load_file("data.csv", delimiter=";")

        Load a Parquet file with column selection:

        >>> df = load_file("data.parquet", columns=["id", "name"])

        Load an Excel file from a specific sheet:

        >>> df = load_file("data.xlsx", sheet_name="Sheet2")

        Load a file with explicit format override:

        >>> df = load_file("data.txt", format="csv", delimiter="\\t")

    Format-Specific Options:
        CSV/TSV:
            - delimiter (str): Field delimiter (default: ",")
            - has_header (bool): Whether first row is header (default: True)
            - encoding (str): File encoding (default: "utf-8")
            - skip_rows (int): Number of rows to skip (default: 0)
            - n_rows (int): Maximum rows to read (default: None)
            - columns (list[str]): Specific columns to load (default: None)

        Excel (xlsx/xls):
            - sheet_name (str): Sheet name to load (default: None, loads first)
            - sheet_index (int): Sheet index to load (default: 0)
            - has_header (bool): Whether first row is header (default: True)
            - skip_rows (int): Number of rows to skip (default: 0)
            - columns (list[str]): Specific columns to load (default: None)

        Parquet/IPC/Feather:
            - columns (list[str]): Specific columns to load (default: None)
            - n_rows (int): Maximum rows to read (default: None)

        JSON/NDJSON:
            - n_rows (int): Maximum rows to read (default: None)

        Avro:
            - columns (list[str]): Specific columns to load (default: None)
    """
    return FileLoader.load(path, format=format, **options)


def compare_files(
    source_path: str | Path,
    target_path: str | Path,
    join_columns: list[str],
    source_format: str | None = None,
    target_format: str | None = None,
    source_options: dict[str, Any] | None = None,
    target_options: dict[str, Any] | None = None,
    abs_tol: float = 0.0001,
    rel_tol: float = 0.0,
    ignore_case: bool = False,
    ignore_spaces: bool = True,
) -> ComparisonResult:
    """Compare two files and return comparison results.

    This function loads two files and compares them using the DataComparator.
    It supports all file formats supported by load_file() and allows
    format-specific options for each file.

    Args:
        source_path: Path to the source file.
        target_path: Path to the target file.
        join_columns: Columns to use for joining/matching rows.
        source_format: Optional format override for source file.
        target_format: Optional format override for target file.
        source_options: Format-specific options for source file.
        target_options: Format-specific options for target file.
        abs_tol: Absolute tolerance for numeric comparisons (default: 0.0001).
        rel_tol: Relative tolerance for numeric comparisons (default: 0.0).
        ignore_case: Whether to ignore case in string comparisons (default: False).
        ignore_spaces: Whether to ignore leading/trailing spaces (default: True).

    Returns:
        ComparisonResult containing all comparison outputs including:
        - source_row_count: Total rows in source
        - target_row_count: Total rows in target
        - matching_rows: Number of matching rows
        - mismatched_rows: Number of rows with value differences
        - rows_only_in_source: DataFrame of rows only in source
        - rows_only_in_target: DataFrame of rows only in target
        - mismatched_columns: DataFrame of value mismatches
        - column_stats: DataFrame with column-level statistics
        - report_text: Human-readable comparison report

    Raises:
        FileNotFoundError: If either file does not exist.
        ValueError: If a format is not supported.
        FileLoadError: If a file cannot be loaded.

    Examples:
        Compare two CSV files:

        >>> result = compare_files(
        ...     "source.csv",
        ...     "target.csv",
        ...     join_columns=["id"]
        ... )
        >>> print(f"Matching rows: {result.matching_rows}")

        Compare files with different formats:

        >>> result = compare_files(
        ...     "source.parquet",
        ...     "target.csv",
        ...     join_columns=["id", "date"]
        ... )

        Compare with format-specific options:

        >>> result = compare_files(
        ...     "source.csv",
        ...     "target.xlsx",
        ...     join_columns=["id"],
        ...     source_options={"delimiter": ";"},
        ...     target_options={"sheet_name": "Data"}
        ... )

        Compare with tolerance for numeric differences:

        >>> result = compare_files(
        ...     "expected.parquet",
        ...     "actual.parquet",
        ...     join_columns=["id"],
        ...     abs_tol=0.01,
        ...     ignore_case=True
        ... )
    """
    # Load source file
    source_opts = source_options or {}
    source_df = load_file(source_path, format=source_format, **source_opts)

    # Load target file
    target_opts = target_options or {}
    target_df = load_file(target_path, format=target_format, **target_opts)

    # Create comparison config
    config = ComparisonConfig(
        join_columns=join_columns,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )

    # Run comparison
    comparator = DataComparator(config)
    return comparator.compare(
        source_df,
        target_df,
        source_name=str(source_path),
        target_name=str(target_path),
    )
