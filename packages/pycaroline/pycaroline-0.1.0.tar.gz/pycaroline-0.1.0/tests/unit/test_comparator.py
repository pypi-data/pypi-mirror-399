"""Unit tests for DataComparator."""

import polars as pl

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult


class TestDataComparator:
    """Tests for DataComparator class."""

    def test_compare_identical_dataframes(self):
        """Test comparing two identical DataFrames."""
        df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(df, df.clone())

        assert result.source_row_count == 3
        assert result.target_row_count == 3
        assert result.matching_rows == 3
        assert result.mismatched_rows == 0
        assert len(result.rows_only_in_source) == 0
        assert len(result.rows_only_in_target) == 0

    def test_compare_with_missing_rows_in_target(self):
        """Test comparing when target is missing rows."""
        source = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.source_row_count == 3
        assert result.target_row_count == 2
        assert len(result.rows_only_in_source) == 1
        assert result.rows_only_in_source["id"][0] == 3

    def test_compare_with_extra_rows_in_target(self):
        """Test comparing when target has extra rows."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.source_row_count == 2
        assert result.target_row_count == 3
        assert len(result.rows_only_in_target) == 1
        assert result.rows_only_in_target["id"][0] == 3

    def test_compare_with_value_differences(self):
        """Test comparing DataFrames with value differences."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "X"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.source_row_count == 2
        assert result.target_row_count == 2
        assert result.mismatched_rows > 0 or result.matching_rows < 2

    def test_compare_with_ignore_case(self):
        """Test case-insensitive comparison."""
        source = pl.DataFrame({"id": [1], "value": ["ABC"]})
        target = pl.DataFrame({"id": [1], "value": ["abc"]})
        config = ComparisonConfig(join_columns=["id"], ignore_case=True)
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 1

    def test_compare_with_ignore_spaces(self):
        """Test whitespace-insensitive comparison."""
        source = pl.DataFrame({"id": [1], "value": ["  hello  "]})
        target = pl.DataFrame({"id": [1], "value": ["hello"]})
        config = ComparisonConfig(join_columns=["id"], ignore_spaces=True)
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 1

    def test_compare_with_numeric_tolerance(self):
        """Test numeric comparison with tolerance."""
        source = pl.DataFrame({"id": [1], "value": [1.0000]})
        target = pl.DataFrame({"id": [1], "value": [1.0001]})
        config = ComparisonConfig(join_columns=["id"], abs_tol=0.001)
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 1

    def test_compare_empty_dataframes(self):
        """Test comparing empty DataFrames."""
        source = pl.DataFrame(
            {"id": pl.Series([], dtype=pl.Int64), "value": pl.Series([], dtype=pl.Utf8)}
        )
        target = pl.DataFrame(
            {"id": pl.Series([], dtype=pl.Int64), "value": pl.Series([], dtype=pl.Utf8)}
        )
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.source_row_count == 0
        assert result.target_row_count == 0
        assert result.matching_rows == 0

    def test_compare_returns_comparison_result(self):
        """Test that compare returns a ComparisonResult instance."""
        df = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(df, df.clone())

        assert isinstance(result, ComparisonResult)
        assert isinstance(result.rows_only_in_source, pl.DataFrame)
        assert isinstance(result.rows_only_in_target, pl.DataFrame)
        assert isinstance(result.column_stats, pl.DataFrame)
        assert isinstance(result.report_text, str)

    def test_compare_with_multiple_join_columns(self):
        """Test comparison with multiple join columns."""
        source = pl.DataFrame(
            {"id1": [1, 1, 2], "id2": ["a", "b", "a"], "value": [10, 20, 30]}
        )
        target = pl.DataFrame(
            {"id1": [1, 1, 2], "id2": ["a", "b", "a"], "value": [10, 20, 30]}
        )
        config = ComparisonConfig(join_columns=["id1", "id2"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert result.matching_rows == 3

    def test_compare_with_custom_names(self):
        """Test comparison with custom source/target names."""
        df = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(
            df, df.clone(), source_name="production", target_name="staging"
        )

        assert "production" in result.report_text or "staging" in result.report_text

    def test_build_column_stats(self):
        """Test column statistics generation."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        result = comparator.compare(source, target)

        assert "column" in result.column_stats.columns
        assert "in_source" in result.column_stats.columns
        assert "in_target" in result.column_stats.columns
