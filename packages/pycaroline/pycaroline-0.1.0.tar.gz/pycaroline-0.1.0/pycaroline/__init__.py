"""PyCaroline: A data validation library for comparing tables across databases.

This library provides tools for validating data migrations between cloud data
warehouses (Snowflake, BigQuery, Redshift) using datacompy for comparison.
"""

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult
from pycaroline.config.loader import ConfigLoader, ConfigurationError
from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType
from pycaroline.reporting.generator import ReportGenerator
from pycaroline.validator import DataValidator, ValidationError

try:
    from pycaroline._version import __version__
except ImportError:
    __version__ = "0.0.0"  # Fallback for editable installs without build

__all__ = [
    # Main orchestrator
    "DataValidator",
    "ValidationError",
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
    "BaseConnector",
    "ConnectionError",
    "QueryError",
    # Reporting
    "ReportGenerator",
]
