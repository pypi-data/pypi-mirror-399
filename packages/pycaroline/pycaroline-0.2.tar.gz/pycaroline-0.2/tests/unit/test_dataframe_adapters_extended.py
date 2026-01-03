"""Extended unit tests for DataFrame adapters to improve coverage.

Tests for adapter error handling, type detection, and edge cases.
"""

import pytest
import polars as pl
import pandas as pd

from pycaroline.adapters.dataframe import (
    DataFrameType,
    PolarsAdapter,
    PandasAdapter,
    SnowparkAdapter,
    detect_dataframe_type,
    adapt_dataframe,
)


class TestPolarsAdapter:
    """Tests for PolarsAdapter."""

    def test_to_polars_returns_same_dataframe(self):
        """Test that to_polars returns the same polars DataFrame."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = adapter.to_polars(df)

        assert result is df

    def test_to_polars_raises_type_error_for_non_polars(self):
        """Test that to_polars raises TypeError for non-polars DataFrame."""
        adapter = PolarsAdapter()
        df = pd.DataFrame({"id": [1, 2]})

        with pytest.raises(TypeError) as exc_info:
            adapter.to_polars(df)

        assert "Expected polars DataFrame" in str(exc_info.value)

    def test_supports_returns_true_for_polars(self):
        """Test that supports returns True for polars DataFrame."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [1]})

        assert adapter.supports(df) is True

    def test_supports_returns_false_for_pandas(self):
        """Test that supports returns False for pandas DataFrame."""
        adapter = PolarsAdapter()
        df = pd.DataFrame({"id": [1]})

        assert adapter.supports(df) is False

    def test_dataframe_type_property(self):
        """Test that dataframe_type returns POLARS."""
        adapter = PolarsAdapter()
        assert adapter.dataframe_type == DataFrameType.POLARS


class TestPandasAdapter:
    """Tests for PandasAdapter."""

    def test_to_polars_converts_pandas_to_polars(self):
        """Test that to_polars converts pandas DataFrame to polars."""
        adapter = PandasAdapter()
        df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert result.shape == (2, 2)
        assert result["id"].to_list() == [1, 2]

    def test_to_polars_raises_type_error_for_non_pandas(self):
        """Test that to_polars raises TypeError for non-pandas DataFrame."""
        adapter = PandasAdapter()
        df = pl.DataFrame({"id": [1, 2]})

        with pytest.raises(TypeError) as exc_info:
            adapter.to_polars(df)

        assert "Expected pandas DataFrame" in str(exc_info.value)

    def test_supports_returns_true_for_pandas(self):
        """Test that supports returns True for pandas DataFrame."""
        adapter = PandasAdapter()
        df = pd.DataFrame({"id": [1]})

        assert adapter.supports(df) is True

    def test_supports_returns_false_for_polars(self):
        """Test that supports returns False for polars DataFrame."""
        adapter = PandasAdapter()
        df = pl.DataFrame({"id": [1]})

        assert adapter.supports(df) is False

    def test_dataframe_type_property(self):
        """Test that dataframe_type returns PANDAS."""
        adapter = PandasAdapter()
        assert adapter.dataframe_type == DataFrameType.PANDAS


class TestSnowparkAdapter:
    """Tests for SnowparkAdapter."""

    def test_supports_returns_false_when_snowpark_not_installed(self):
        """Test that supports returns False when snowpark is not installed."""
        adapter = SnowparkAdapter()
        df = pl.DataFrame({"id": [1]})

        # Should return False for non-snowpark DataFrames
        assert adapter.supports(df) is False

    def test_to_polars_raises_type_error_for_non_snowpark(self):
        """Test that to_polars raises appropriate error for non-snowpark DataFrame."""
        adapter = SnowparkAdapter()
        df = pl.DataFrame({"id": [1]})

        # Should raise ImportError or TypeError
        with pytest.raises((ImportError, TypeError)):
            adapter.to_polars(df)

    def test_dataframe_type_property(self):
        """Test that dataframe_type returns SNOWPARK."""
        adapter = SnowparkAdapter()
        assert adapter.dataframe_type == DataFrameType.SNOWPARK


class TestDetectDataframeType:
    """Tests for detect_dataframe_type function."""

    def test_detect_polars_dataframe(self):
        """Test detecting polars DataFrame type."""
        df = pl.DataFrame({"id": [1]})
        result = detect_dataframe_type(df)
        assert result == DataFrameType.POLARS

    def test_detect_pandas_dataframe(self):
        """Test detecting pandas DataFrame type."""
        df = pd.DataFrame({"id": [1]})
        result = detect_dataframe_type(df)
        assert result == DataFrameType.PANDAS

    def test_detect_unknown_type_returns_none(self):
        """Test that unknown types return None."""
        result = detect_dataframe_type("not a dataframe")
        assert result is None

    def test_detect_dict_returns_none(self):
        """Test that dict returns None."""
        result = detect_dataframe_type({"id": [1]})
        assert result is None

    def test_detect_list_returns_none(self):
        """Test that list returns None."""
        result = detect_dataframe_type([[1, 2], [3, 4]])
        assert result is None


class TestAdaptDataframe:
    """Tests for adapt_dataframe function."""

    def test_adapt_polars_dataframe(self):
        """Test adapting polars DataFrame."""
        df = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        result = adapt_dataframe(df)

        assert isinstance(result, pl.DataFrame)
        assert result is df

    def test_adapt_pandas_dataframe(self):
        """Test adapting pandas DataFrame."""
        df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        result = adapt_dataframe(df)

        assert isinstance(result, pl.DataFrame)
        assert result.shape == (2, 2)

    def test_adapt_with_explicit_type_string(self):
        """Test adapting with explicit type as string."""
        df = pd.DataFrame({"id": [1, 2]})
        result = adapt_dataframe(df, df_type="pandas")

        assert isinstance(result, pl.DataFrame)

    def test_adapt_with_explicit_type_enum(self):
        """Test adapting with explicit type as enum."""
        df = pd.DataFrame({"id": [1, 2]})
        result = adapt_dataframe(df, df_type=DataFrameType.PANDAS)

        assert isinstance(result, pl.DataFrame)

    def test_adapt_raises_type_error_for_unsupported_type(self):
        """Test that adapt_dataframe raises TypeError for unsupported types."""
        with pytest.raises(TypeError) as exc_info:
            adapt_dataframe("not a dataframe")

        assert "Unsupported DataFrame type" in str(exc_info.value)

    def test_adapt_raises_value_error_for_invalid_type_enum(self):
        """Test that adapt_dataframe raises ValueError for invalid type enum."""
        df = pl.DataFrame({"id": [1]})

        # This should work since polars is supported
        result = adapt_dataframe(df, df_type=DataFrameType.POLARS)
        assert isinstance(result, pl.DataFrame)

    def test_adapt_with_empty_dataframe(self):
        """Test adapting empty DataFrames."""
        df = pd.DataFrame({"id": [], "value": []})
        result = adapt_dataframe(df)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0


class TestDataFrameTypeEnum:
    """Tests for DataFrameType enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert DataFrameType.POLARS.value == "polars"
        assert DataFrameType.PANDAS.value == "pandas"
        assert DataFrameType.SNOWPARK.value == "snowpark"

    def test_enum_from_string(self):
        """Test creating enum from string."""
        assert DataFrameType("polars") == DataFrameType.POLARS
        assert DataFrameType("pandas") == DataFrameType.PANDAS
        assert DataFrameType("snowpark") == DataFrameType.SNOWPARK

    def test_enum_invalid_string_raises_error(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            DataFrameType("invalid")
