"""DataFrame adapters for pycaroline.

This module provides adapters for converting various DataFrame types
to polars DataFrames for comparison.
"""

from pycaroline.adapters.dataframe import (
    DataFrameAdapter,
    PandasAdapter,
    PolarsAdapter,
    SnowparkAdapter,
    adapt_dataframe,
    detect_dataframe_type,
)

__all__ = [
    "DataFrameAdapter",
    "PandasAdapter",
    "PolarsAdapter",
    "SnowparkAdapter",
    "adapt_dataframe",
    "detect_dataframe_type",
]
