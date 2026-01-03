"""Extended unit tests for DataComparator to improve coverage.

Tests for pandas DataFrame input, error handling, and edge cases.
"""

import pandas as pd
import polars as pl
import pytest

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult


class TestDataComparatorWithPandas:
    """Tests for DataComparator with pandas DataFrames."""

    def test_compare_pandas_dataframes(self):
        """Test comparing pandas DataFrames."""
        source = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        target = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert isinstance(result, ComparisonResult)
        assert result.source_row_count == 3
        assert result.target_row_count == 3
        assert result.matching_rows == 3

    def test_compare_mixed_pandas_polars(self):
        """Test comparing pandas source with polars target."""
        source = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 2

    def test_compare_polars_source_pandas_target(self):
        """Test comparing polars source with pandas target."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 2


class TestDataComparatorColumnStats:
    """Tests for column statistics generation."""

    def test_column_stats_includes_all_columns(self):
        """Test that column stats includes all columns from both DataFrames."""
        source = pl.DataFrame({"id": [1], "col_a": ["x"], "col_b": [10]})
        target = pl.DataFrame({"id": [1], "col_a": ["x"], "col_c": [20]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        columns_in_stats = result.column_stats["column"].to_list()
        assert "id" in columns_in_stats
        assert "col_a" in columns_in_stats
        assert "col_b" in columns_in_stats
        assert "col_c" in columns_in_stats

    def test_column_stats_shows_source_only_columns(self):
        """Test that column stats correctly identifies source-only columns."""
        source = pl.DataFrame({"id": [1], "source_only": ["x"]})
        target = pl.DataFrame({"id": [1]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        stats = result.column_stats.filter(pl.col("column") == "source_only")
        assert stats["in_source"][0] is True
        assert stats["in_target"][0] is False

    def test_column_stats_shows_target_only_columns(self):
        """Test that column stats correctly identifies target-only columns."""
        source = pl.DataFrame({"id": [1]})
        target = pl.DataFrame({"id": [1], "target_only": ["y"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        stats = result.column_stats.filter(pl.col("column") == "target_only")
        assert stats["in_source"][0] is False
        assert stats["in_target"][0] is True

    def test_column_stats_includes_dtype_info(self):
        """Test that column stats includes data type information."""
        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert "source_dtype" in result.column_stats.columns
        assert "target_dtype" in result.column_stats.columns


class TestDataComparatorEdgeCases:
    """Tests for edge cases and error handling."""

    def test_compare_single_row_dataframes(self):
        """Test comparing DataFrames with single row."""
        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 1

    def test_compare_with_null_values(self):
        """Test comparing DataFrames with null values."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", None]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", None]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.source_row_count == 2
        assert result.target_row_count == 2

    def test_compare_with_numeric_columns(self):
        """Test comparing DataFrames with various numeric types."""
        source = pl.DataFrame({
            "id": [1, 2],
            "int_col": [10, 20],
            "float_col": [1.5, 2.5],
        })
        target = pl.DataFrame({
            "id": [1, 2],
            "int_col": [10, 20],
            "float_col": [1.5, 2.5],
        })
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 2

    def test_compare_with_boolean_columns(self):
        """Test comparing DataFrames with boolean columns."""
        source = pl.DataFrame({"id": [1, 2], "flag": [True, False]})
        target = pl.DataFrame({"id": [1, 2], "flag": [True, False]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 2

    def test_compare_with_date_columns(self):
        """Test comparing DataFrames with date columns."""
        from datetime import date

        source = pl.DataFrame({
            "id": [1, 2],
            "date_col": [date(2024, 1, 1), date(2024, 1, 2)],
        })
        target = pl.DataFrame({
            "id": [1, 2],
            "date_col": [date(2024, 1, 1), date(2024, 1, 2)],
        })
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 2

    def test_compare_large_dataframes(self):
        """Test comparing larger DataFrames."""
        n = 1000
        source = pl.DataFrame({
            "id": list(range(n)),
            "value": [f"val_{i}" for i in range(n)],
        })
        target = source.clone()
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == n

    def test_compare_with_relative_tolerance(self):
        """Test comparison with relative tolerance."""
        source = pl.DataFrame({"id": [1], "value": [100.0]})
        target = pl.DataFrame({"id": [1], "value": [101.0]})
        config = ComparisonConfig(join_columns=["id"], rel_tol=0.02)  # 2% tolerance
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 1

    def test_compare_preserves_original_dataframes(self):
        """Test that comparison doesn't modify original DataFrames."""
        source = pl.DataFrame({"id": [1], "value": ["  hello  "]})
        target = pl.DataFrame({"id": [1], "value": ["hello"]})
        original_source_value = source["value"][0]

        config = ComparisonConfig(join_columns=["id"], ignore_spaces=True)
        comparator = DataComparator(config)
        comparator.compare(source, target)

        # Original should be unchanged
        assert source["value"][0] == original_source_value


class TestDataComparatorReportText:
    """Tests for report text generation."""

    def test_report_text_is_string(self):
        """Test that report_text is a string."""
        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert isinstance(result.report_text, str)
        assert len(result.report_text) > 0

    def test_report_text_contains_comparison_info(self):
        """Test that report_text contains comparison information."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        # Report should contain some comparison information
        assert "match" in result.report_text.lower() or "row" in result.report_text.lower()
