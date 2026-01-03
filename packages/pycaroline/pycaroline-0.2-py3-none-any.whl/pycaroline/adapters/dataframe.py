"""DataFrame adapters for converting various DataFrame types to polars.

This module provides adapters for polars, pandas, and snowpark DataFrames,
enabling direct DataFrame input for validation without requiring database connectors.

Note: Spark DataFrame support is not included as PySpark requires Python < 3.12.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import polars as pl


class DataFrameType(Enum):
    """Supported DataFrame types."""

    POLARS = "polars"
    PANDAS = "pandas"
    SNOWPARK = "snowpark"


class DataFrameAdapter(ABC):
    """Abstract base class for DataFrame adapters.

    Adapters convert various DataFrame types to polars DataFrames
    for use with the comparison engine.
    """

    @abstractmethod
    def to_polars(self, df: Any) -> pl.DataFrame:
        """Convert DataFrame to polars DataFrame.

        Args:
            df: Source DataFrame of the adapter's supported type.

        Returns:
            Polars DataFrame containing the same data.

        Raises:
            TypeError: If the DataFrame is not of the expected type.
        """
        pass

    @abstractmethod
    def supports(self, df: Any) -> bool:
        """Check if this adapter supports the given DataFrame type.

        Args:
            df: DataFrame to check.

        Returns:
            True if this adapter can handle the DataFrame, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def dataframe_type(self) -> DataFrameType:
        """Get the DataFrame type this adapter handles."""
        pass


class PolarsAdapter(DataFrameAdapter):
    """Adapter for polars DataFrames (passthrough)."""

    def to_polars(self, df: Any) -> pl.DataFrame:
        """Return polars DataFrame as-is.

        Args:
            df: Polars DataFrame.

        Returns:
            The same polars DataFrame.

        Raises:
            TypeError: If df is not a polars DataFrame.
        """
        if not isinstance(df, pl.DataFrame):
            raise TypeError(f"Expected polars DataFrame, got {type(df).__name__}")
        return df

    def supports(self, df: Any) -> bool:
        """Check if df is a polars DataFrame."""
        return isinstance(df, pl.DataFrame)

    @property
    def dataframe_type(self) -> DataFrameType:
        return DataFrameType.POLARS


class PandasAdapter(DataFrameAdapter):
    """Adapter for pandas DataFrames."""

    def to_polars(self, df: Any) -> pl.DataFrame:
        """Convert pandas DataFrame to polars.

        Args:
            df: Pandas DataFrame.

        Returns:
            Polars DataFrame containing the same data.

        Raises:
            TypeError: If df is not a pandas DataFrame.
            ImportError: If pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                "pandas is required for PandasAdapter. "
                "Install with: pip install pandas"
            ) from e

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

        return pl.from_pandas(df)

    def supports(self, df: Any) -> bool:
        """Check if df is a pandas DataFrame."""
        try:
            import pandas as pd
            return isinstance(df, pd.DataFrame)
        except ImportError:
            return False

    @property
    def dataframe_type(self) -> DataFrameType:
        return DataFrameType.PANDAS


class SnowparkAdapter(DataFrameAdapter):
    """Adapter for Snowpark DataFrames.

    Note: Converting Snowpark DataFrames requires an active Snowflake
    connection as the data must be collected from Snowflake.
    """

    def to_polars(self, df: Any) -> pl.DataFrame:
        """Convert Snowpark DataFrame to polars.

        This collects the Snowpark DataFrame to pandas first,
        then converts to polars. Requires active Snowflake connection.

        Args:
            df: Snowpark DataFrame.

        Returns:
            Polars DataFrame containing the same data.

        Raises:
            TypeError: If df is not a Snowpark DataFrame.
            ImportError: If snowflake-snowpark-python is not installed.
        """
        try:
            from snowflake.snowpark import DataFrame as SnowparkDataFrame
        except ImportError as e:
            raise ImportError(
                "snowflake-snowpark-python is required for SnowparkAdapter. "
                "Install with: pip install snowflake-snowpark-python"
            ) from e

        if not isinstance(df, SnowparkDataFrame):
            raise TypeError(f"Expected Snowpark DataFrame, got {type(df).__name__}")

        # Collect to pandas, then convert to polars
        pandas_df = df.to_pandas()
        return pl.from_pandas(pandas_df)

    def supports(self, df: Any) -> bool:
        """Check if df is a Snowpark DataFrame."""
        try:
            from snowflake.snowpark import DataFrame as SnowparkDataFrame
            return isinstance(df, SnowparkDataFrame)
        except ImportError:
            return False

    @property
    def dataframe_type(self) -> DataFrameType:
        return DataFrameType.SNOWPARK


# Registry of available adapters
_ADAPTERS: list[DataFrameAdapter] = [
    PolarsAdapter(),
    PandasAdapter(),
    SnowparkAdapter(),
]


def detect_dataframe_type(df: Any) -> DataFrameType | None:
    """Detect the type of a DataFrame.

    Args:
        df: DataFrame to detect type for.

    Returns:
        DataFrameType enum value if recognized, None otherwise.
    """
    for adapter in _ADAPTERS:
        if adapter.supports(df):
            return adapter.dataframe_type
    return None


def adapt_dataframe(df: Any, df_type: DataFrameType | str | None = None) -> pl.DataFrame:
    """Convert any supported DataFrame type to polars.

    Args:
        df: DataFrame to convert (polars, pandas, or snowpark).
        df_type: Optional explicit type specification. If None, auto-detects.

    Returns:
        Polars DataFrame containing the same data.

    Raises:
        TypeError: If DataFrame type is not supported or cannot be detected.
        ValueError: If specified df_type doesn't match actual DataFrame type.
    """
    # Handle string type specification
    if isinstance(df_type, str):
        df_type = DataFrameType(df_type)

    # Auto-detect if not specified
    if df_type is None:
        df_type = detect_dataframe_type(df)
        if df_type is None:
            raise TypeError(
                f"Unsupported DataFrame type: {type(df).__name__}. "
                f"Supported types: polars, pandas, snowpark"
            )

    # Find matching adapter
    for adapter in _ADAPTERS:
        if adapter.dataframe_type == df_type:
            return adapter.to_polars(df)

    raise ValueError(f"No adapter found for DataFrame type: {df_type}")
