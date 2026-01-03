"""Unit tests for DataFrame adapters."""

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


class TestPolarsAdapter:
    """Tests for PolarsAdapter."""

    def test_to_polars_passthrough(self):
        """Test polars DataFrame is returned as-is."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})

        result = adapter.to_polars(df)

        assert result.equals(df)

    def test_to_polars_wrong_type(self):
        """Test error when non-polars DataFrame is passed."""
        adapter = PolarsAdapter()

        with pytest.raises(TypeError) as exc_info:
            adapter.to_polars({"id": [1, 2, 3]})

        assert "Expected polars DataFrame" in str(exc_info.value)

    def test_supports_polars(self):
        """Test supports returns True for polars DataFrame."""
        adapter = PolarsAdapter()
        df = pl.DataFrame({"id": [1, 2, 3]})

        assert adapter.supports(df) is True

    def test_supports_non_polars(self):
        """Test supports returns False for non-polars objects."""
        adapter = PolarsAdapter()

        assert adapter.supports({"id": [1, 2, 3]}) is False
        assert adapter.supports([1, 2, 3]) is False

    def test_dataframe_type(self):
        """Test dataframe_type property."""
        adapter = PolarsAdapter()
        assert adapter.dataframe_type == DataFrameType.POLARS


class TestPandasAdapter:
    """Tests for PandasAdapter."""

    def test_to_polars_conversion(self):
        """Test pandas DataFrame is converted to polars."""
        pytest.importorskip("pandas")
        import pandas as pd

        adapter = PandasAdapter()
        df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})

        result = adapter.to_polars(df)

        assert isinstance(result, pl.DataFrame)
        assert result["id"].to_list() == [1, 2, 3]
        assert result["value"].to_list() == ["a", "b", "c"]

    def test_to_polars_wrong_type(self):
        """Test error when non-pandas DataFrame is passed."""
        pytest.importorskip("pandas")
        adapter = PandasAdapter()

        with pytest.raises(TypeError) as exc_info:
            adapter.to_polars({"id": [1, 2, 3]})

        assert "Expected pandas DataFrame" in str(exc_info.value)

    def test_supports_pandas(self):
        """Test supports returns True for pandas DataFrame."""
        pytest.importorskip("pandas")
        import pandas as pd

        adapter = PandasAdapter()
        df = pd.DataFrame({"id": [1, 2, 3]})

        assert adapter.supports(df) is True

    def test_supports_non_pandas(self):
        """Test supports returns False for non-pandas objects."""
        adapter = PandasAdapter()

        assert adapter.supports({"id": [1, 2, 3]}) is False
        assert adapter.supports(pl.DataFrame({"id": [1, 2, 3]})) is False

    def test_dataframe_type(self):
        """Test dataframe_type property."""
        adapter = PandasAdapter()
        assert adapter.dataframe_type == DataFrameType.PANDAS


class TestSnowparkAdapter:
    """Tests for SnowparkAdapter."""

    def test_to_polars_wrong_type(self):
        """Test error when non-snowpark DataFrame is passed."""
        adapter = SnowparkAdapter()

        # The adapter will raise ImportError if snowpark is not installed,
        # or TypeError if the wrong type is passed
        with pytest.raises((TypeError, ImportError)):
            adapter.to_polars({"id": [1, 2, 3]})

    def test_dataframe_type(self):
        """Test dataframe_type property."""
        adapter = SnowparkAdapter()
        assert adapter.dataframe_type == DataFrameType.SNOWPARK


class TestDetectDataFrameType:
    """Tests for detect_dataframe_type function."""

    def test_detect_polars(self):
        """Test detection of polars DataFrame."""
        df = pl.DataFrame({"id": [1, 2, 3]})
        assert detect_dataframe_type(df) == DataFrameType.POLARS

    def test_detect_pandas(self):
        """Test detection of pandas DataFrame."""
        pytest.importorskip("pandas")
        import pandas as pd

        df = pd.DataFrame({"id": [1, 2, 3]})
        assert detect_dataframe_type(df) == DataFrameType.PANDAS

    def test_detect_unknown(self):
        """Test detection returns None for unknown types."""
        assert detect_dataframe_type({"id": [1, 2, 3]}) is None
        assert detect_dataframe_type([1, 2, 3]) is None


class TestAdaptDataFrame:
    """Tests for adapt_dataframe function."""

    def test_adapt_polars(self):
        """Test adapting polars DataFrame."""
        df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})

        result = adapt_dataframe(df)

        assert result.equals(df)

    def test_adapt_pandas(self):
        """Test adapting pandas DataFrame."""
        pytest.importorskip("pandas")
        import pandas as pd

        df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})

        result = adapt_dataframe(df)

        assert isinstance(result, pl.DataFrame)
        assert result["id"].to_list() == [1, 2, 3]

    def test_adapt_with_explicit_type(self):
        """Test adapting with explicit type specification."""
        df = pl.DataFrame({"id": [1, 2, 3]})

        result = adapt_dataframe(df, DataFrameType.POLARS)

        assert result.equals(df)

    def test_adapt_with_string_type(self):
        """Test adapting with string type specification."""
        df = pl.DataFrame({"id": [1, 2, 3]})

        result = adapt_dataframe(df, "polars")

        assert result.equals(df)

    def test_adapt_unsupported_type(self):
        """Test error for unsupported DataFrame type."""
        with pytest.raises(TypeError) as exc_info:
            adapt_dataframe({"id": [1, 2, 3]})

        assert "Unsupported DataFrame type" in str(exc_info.value)
