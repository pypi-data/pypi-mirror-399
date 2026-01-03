"""Data models for comparison configuration and results."""

from dataclasses import dataclass

import polars as pl


@dataclass
class ComparisonConfig:
    """Configuration for data comparison.

    Attributes:
        join_columns: List of column names to use as join keys for matching rows.
        abs_tol: Absolute tolerance for numeric comparison (default: 0.0001).
        rel_tol: Relative tolerance for numeric comparison (default: 0.0).
        ignore_case: If True, string comparisons are case-insensitive (default: False).
        ignore_spaces: If True, leading/trailing whitespace is stripped from strings (default: True).
    """

    join_columns: list[str]
    abs_tol: float = 0.0001
    rel_tol: float = 0.0
    ignore_case: bool = False
    ignore_spaces: bool = True


@dataclass
class ComparisonResult:
    """Results from a data comparison.

    Attributes:
        source_row_count: Total number of rows in the source DataFrame.
        target_row_count: Total number of rows in the target DataFrame.
        matching_rows: Number of rows that match between source and target.
        mismatched_rows: Number of rows with matching keys but differing values.
        rows_only_in_source: DataFrame containing rows present only in source.
        rows_only_in_target: DataFrame containing rows present only in target.
        mismatched_columns: DataFrame containing rows with value mismatches.
        column_stats: DataFrame with column-level match statistics.
        report_text: Human-readable text report from datacompy.
    """

    source_row_count: int
    target_row_count: int
    matching_rows: int
    mismatched_rows: int
    rows_only_in_source: pl.DataFrame
    rows_only_in_target: pl.DataFrame
    mismatched_columns: pl.DataFrame
    column_stats: pl.DataFrame
    report_text: str
