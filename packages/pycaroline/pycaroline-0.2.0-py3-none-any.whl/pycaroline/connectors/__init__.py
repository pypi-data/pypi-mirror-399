"""Database and storage connectors for pycaroline.

This module provides connectors for various cloud data warehouses and storage services.
"""

from pycaroline.connectors.base import (
    BaseConnector,
    ConnectionError,
    QueryError,
)
from pycaroline.connectors.factory import (
    ConnectorFactory,
    DatabaseType,
    StorageType,
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

try:
    from pycaroline.connectors.s3 import S3Connector
except ImportError:
    S3Connector = None  # type: ignore

try:
    from pycaroline.connectors.gcs import GCSConnector
except ImportError:
    GCSConnector = None  # type: ignore

try:
    from pycaroline.connectors.mysql import MySQLConnector
except ImportError:
    MySQLConnector = None  # type: ignore

try:
    from pycaroline.connectors.postgresql import PostgreSQLConnector
except ImportError:
    PostgreSQLConnector = None  # type: ignore

__all__ = [
    "BaseConnector",
    "ConnectionError",
    "QueryError",
    "ConnectorFactory",
    "DatabaseType",
    "StorageType",
    "SnowflakeConnector",
    "BigQueryConnector",
    "RedshiftConnector",
    "S3Connector",
    "GCSConnector",
    "MySQLConnector",
    "PostgreSQLConnector",
]
