"""PyCaroline: A data validation library for comparing tables across databases.

This library provides tools for validating data migrations between cloud data
warehouses (Snowflake, BigQuery, Redshift), cloud storage (S3, GCS), and
databases (MySQL, PostgreSQL) using datacompy for comparison.

Supports direct DataFrame input with polars, pandas, and snowpark DataFrames.
Supports file-based data loading and comparison for various formats.
"""

from pycaroline.adapters.dataframe import (
    DataFrameAdapter,
    DataFrameType,
    adapt_dataframe,
    detect_dataframe_type,
)
from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult
from pycaroline.config.loader import ConfigLoader, ConfigurationError
from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType, StorageType
from pycaroline.loaders import FileFormat, FileLoadError, compare_files, load_file
from pycaroline.reporting.generator import ReportGenerator
from pycaroline.validator import DataValidator, ValidationError, compare_dataframes

try:
    from pycaroline._version import __version__
except ImportError:
    __version__ = "0.0.0"  # Fallback for editable installs without build

__all__ = [
    # Main orchestrator
    "DataValidator",
    "ValidationError",
    "compare_dataframes",
    # Configuration
    "ConfigLoader",
    "ConfigurationError",
    "ValidationConfig",
    "TableConfig",
    "ComparisonSettings",
    # Comparison
    "DataComparator",
    "ComparisonConfig",
    "ComparisonResult",
    # Connectors
    "ConnectorFactory",
    "DatabaseType",
    "StorageType",
    "BaseConnector",
    "ConnectionError",
    "QueryError",
    # DataFrame adapters
    "DataFrameAdapter",
    "DataFrameType",
    "adapt_dataframe",
    "detect_dataframe_type",
    # File loading
    "FileFormat",
    "FileLoadError",
    "load_file",
    "compare_files",
    # Reporting
    "ReportGenerator",
]
