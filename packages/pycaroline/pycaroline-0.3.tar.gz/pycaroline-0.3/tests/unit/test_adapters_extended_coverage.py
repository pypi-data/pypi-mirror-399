"""Additional tests for DataFrame adapters to improve coverage.

Tests for edge cases and error handling.
"""

from unittest.mock import MagicMock

import pandas as pd
import polars as pl
import pytest

from pycaroline.adapters.dataframe import (
    DataFrameType,
    PandasAdapter,
    PolarsAdapter,
    SnowparkAdapter,
    adapt_dataframe,
    detect_dataframe_type,
)


class TestPandasAdapterImportError:
    """Tests for PandasAdapter when pandas is not available."""

    def test_to_polars_raises_type_error_for_wrong_type(self):
        """Test that to_polars raises TypeError for wrong type."""
        adapter = PandasAdapter()

        # Create a mock object that's not a pandas DataFrame
        mock_df = MagicMock()

        # This should raise TypeError since it's not a pandas DataFrame
        with pytest.raises(TypeError):
            adapter.to_polars(mock_df)

    def test_supports_returns_false_for_non_dataframe(self):
        """Test that supports returns False for non-DataFrame objects."""
        adapter = PandasAdapter()

        result = adapter.supports("not a dataframe")
        assert result is False

        result = adapter.supports(123)
        assert result is False

        result = adapter.supports(None)
        assert result is False


class TestSnowparkAdapterEdgeCases:
    """Tests for SnowparkAdapter edge cases."""

    def test_to_polars_with_non_snowpark_raises_error(self):
        """Test that to_polars raises error for non-Snowpark DataFrame."""
        adapter = SnowparkAdapter()

        # Try with a polars DataFrame
        df = pl.DataFrame({"id": [1, 2]})

        with pytest.raises((ImportError, TypeError)):
            adapter.to_polars(df)

    def test_supports_with_various_types(self):
        """Test supports method with various input types."""
        adapter = SnowparkAdapter()

        # Should return False for all non-Snowpark types
        assert adapter.supports(None) is False
        assert adapter.supports("string") is False
        assert adapter.supports(123) is False
        assert adapter.supports([1, 2, 3]) is False
        assert adapter.supports({"key": "value"}) is False


class TestAdaptDataframeEdgeCases:
    """Tests for adapt_dataframe edge cases."""

    def test_adapt_with_none_raises_error(self):
        """Test that adapting None raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            adapt_dataframe(None)

        assert "Unsupported DataFrame type" in str(exc_info.value)

    def test_adapt_with_dict_raises_error(self):
        """Test that adapting dict raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            adapt_dataframe({"id": [1, 2]})

        assert "Unsupported DataFrame type" in str(exc_info.value)

    def test_adapt_with_list_raises_error(self):
        """Test that adapting list raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            adapt_dataframe([[1, 2], [3, 4]])

        assert "Unsupported DataFrame type" in str(exc_info.value)

    def test_adapt_polars_with_explicit_type(self):
        """Test adapting polars DataFrame with explicit type."""
        df = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = adapt_dataframe(df, df_type=DataFrameType.POLARS)

        assert isinstance(result, pl.DataFrame)
        assert result is df

    def test_adapt_pandas_with_string_type(self):
        """Test adapting pandas DataFrame with string type."""
        df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = adapt_dataframe(df, df_type="pandas")

        assert isinstance(result, pl.DataFrame)

    def test_adapt_preserves_data_types(self):
        """Test that adapt preserves data types correctly."""
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "str_col": ["a", "b", "c"],
                "bool_col": [True, False, True],
            }
        )

        result = adapt_dataframe(df)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 3
        assert result["int_col"].to_list() == [1, 2, 3]
        assert result["str_col"].to_list() == ["a", "b", "c"]


class TestDetectDataframeTypeEdgeCases:
    """Tests for detect_dataframe_type edge cases."""

    def test_detect_with_none(self):
        """Test detecting type of None."""
        result = detect_dataframe_type(None)
        assert result is None

    def test_detect_with_numpy_array(self):
        """Test detecting type of numpy array."""
        import numpy as np

        arr = np.array([[1, 2], [3, 4]])
        result = detect_dataframe_type(arr)
        assert result is None

    def test_detect_with_series(self):
        """Test detecting type of pandas Series."""
        series = pd.Series([1, 2, 3])
        result = detect_dataframe_type(series)
        # Series is not a DataFrame, should return None
        assert result is None


class TestPolarsAdapterEdgeCases:
    """Tests for PolarsAdapter edge cases."""

    def test_to_polars_with_empty_dataframe(self):
        """Test to_polars with empty DataFrame."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [], "value": []})

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0

    def test_to_polars_with_single_column(self):
        """Test to_polars with single column DataFrame."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [1, 2, 3]})

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert result.columns == ["id"]

    def test_supports_with_polars_lazyframe(self):
        """Test supports with polars LazyFrame."""
        adapter = PolarsAdapter()
        lazy_df = pl.DataFrame({"id": [1, 2]}).lazy()

        # LazyFrame is not a DataFrame
        result = adapter.supports(lazy_df)
        assert result is False


class TestPandasAdapterEdgeCases:
    """Tests for PandasAdapter edge cases."""

    def test_to_polars_with_empty_dataframe(self):
        """Test to_polars with empty pandas DataFrame."""
        adapter = PandasAdapter()
        df = pd.DataFrame({"id": [], "value": []})

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0

    def test_to_polars_with_index(self):
        """Test to_polars with pandas DataFrame with custom index."""
        adapter = PandasAdapter()
        df = pd.DataFrame({"value": ["a", "b", "c"]}, index=["x", "y", "z"])

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert "value" in result.columns

    def test_to_polars_with_multiindex(self):
        """Test to_polars with pandas DataFrame with MultiIndex columns."""
        adapter = PandasAdapter()
        df = pd.DataFrame(
            {
                ("A", "x"): [1, 2],
                ("A", "y"): [3, 4],
            }
        )

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 2
