"""Database connectors for data-recon.

This module provides database connectors for various cloud data warehouses.
"""

from pycaroline.connectors.base import (
    BaseConnector,
    ConnectionError,
    QueryError,
)
from pycaroline.connectors.factory import (
    ConnectorFactory,
    DatabaseType,
)

# Import connectors to register them with the factory
# These imports are conditional based on available dependencies
try:
    from pycaroline.connectors.snowflake import SnowflakeConnector
except ImportError:
    SnowflakeConnector = None  # type: ignore

try:
    from pycaroline.connectors.bigquery import BigQueryConnector
except ImportError:
    BigQueryConnector = None  # type: ignore

try:
    from pycaroline.connectors.redshift import RedshiftConnector
except ImportError:
    RedshiftConnector = None  # type: ignore

__all__ = [
    "BaseConnector",
    "ConnectionError",
    "QueryError",
    "ConnectorFactory",
    "DatabaseType",
    "SnowflakeConnector",
    "BigQueryConnector",
    "RedshiftConnector",
]
