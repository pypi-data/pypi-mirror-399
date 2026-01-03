"""Redshift database connector.

This module provides a connector for Amazon Redshift that extends BaseConnector.
"""

import os

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType

# Try redshift_connector first, fall back to psycopg2
REDSHIFT_CONNECTOR_AVAILABLE = False
PSYCOPG2_AVAILABLE = False

try:
    import redshift_connector

    REDSHIFT_CONNECTOR_AVAILABLE = True
except ImportError:
    pass

try:
    import psycopg2

    PSYCOPG2_AVAILABLE = True
except ImportError:
    pass


@ConnectorFactory.register(DatabaseType.REDSHIFT)
class RedshiftConnector(BaseConnector):
    """Redshift database connector.

    Supports authentication via:
    - Username/password authentication
    - IAM authentication (when using redshift_connector)

    Configuration can be provided via:
    - Direct parameters
    - Environment variables (REDSHIFT_HOST, REDSHIFT_USER, etc.)

    Example:
        # Using environment variables
        with RedshiftConnector() as conn:
            df = conn.query("SELECT * FROM my_table")

        # Using direct parameters
        connector = RedshiftConnector(
            host="my-cluster.region.redshift.amazonaws.com",
            port=5439,
            database="my_database",
            user="my_user",
            password="my_password"
        )

        # Using IAM authentication (redshift_connector only)
        connector = RedshiftConnector(
            host="my-cluster.region.redshift.amazonaws.com",
            database="my_database",
            iam=True,
            cluster_identifier="my-cluster",
            region="us-east-1"
        )
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        schema: str | None = None,
        iam: bool = False,
        cluster_identifier: str | None = None,
        region: str | None = None,
        ssl: bool = True,
        ssl_mode: str = "verify-ca",
    ):
        """Initialize the Redshift connector.

        Args:
            host: Redshift cluster endpoint hostname.
            port: Redshift cluster port (default: 5439).
            database: Database name to connect to.
            user: Username for authentication.
            password: Password for authentication.
            schema: Default schema for queries.
            iam: Use IAM authentication (requires redshift_connector).
            cluster_identifier: Cluster identifier for IAM auth.
            region: AWS region for IAM auth.
            ssl: Enable SSL connection (default: True).
            ssl_mode: SSL mode for psycopg2 ('verify-ca', 'verify-full', 'require').
        """
        if not REDSHIFT_CONNECTOR_AVAILABLE and not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "redshift-connector or psycopg2 is required for RedshiftConnector. "
                "Install with: pip install data-recon[redshift]"
            )

        self._connection = None
        self._use_redshift_connector = REDSHIFT_CONNECTOR_AVAILABLE

        # Priority: direct params > env vars
        self._host = host or os.environ.get("REDSHIFT_HOST")
        self._port = port or int(os.environ.get("REDSHIFT_PORT", "5439"))
        self._database = database or os.environ.get("REDSHIFT_DATABASE")
        self._user = user or os.environ.get("REDSHIFT_USER")
        self._password = password or os.environ.get("REDSHIFT_PASSWORD")
        self._schema = schema or os.environ.get("REDSHIFT_SCHEMA")
        self._iam = iam
        self._cluster_identifier = cluster_identifier or os.environ.get(
            "REDSHIFT_CLUSTER_IDENTIFIER"
        )
        self._region = region or os.environ.get("AWS_REGION")
        self._ssl = ssl
        self._ssl_mode = ssl_mode

    def connect(self) -> None:
        """Establish connection to Redshift.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        if not self._host:
            raise ConnectionError(
                "Redshift host is required. Set REDSHIFT_HOST environment "
                "variable or provide 'host' parameter."
            )
        if not self._database:
            raise ConnectionError(
                "Redshift database is required. Set REDSHIFT_DATABASE environment "
                "variable or provide 'database' parameter."
            )

        try:
            if self._use_redshift_connector:
                self._connect_with_redshift_connector()
            else:
                self._connect_with_psycopg2()
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Redshift host '{self._host}' "
                f"database '{self._database}': {e}"
            ) from e

    def _connect_with_redshift_connector(self) -> None:
        """Connect using redshift_connector library."""
        connection_params = {
            "host": self._host,
            "port": self._port,
            "database": self._database,
            "ssl": self._ssl,
        }

        if self._iam:
            # IAM authentication
            if not self._cluster_identifier:
                raise ConnectionError(
                    "cluster_identifier is required for IAM authentication"
                )
            connection_params["iam"] = True
            connection_params["cluster_identifier"] = self._cluster_identifier
            if self._region:
                connection_params["region"] = self._region
        else:
            # Username/password authentication
            if not self._user:
                raise ConnectionError(
                    "Redshift user is required. Set REDSHIFT_USER environment "
                    "variable or provide 'user' parameter."
                )
            if not self._password:
                raise ConnectionError(
                    "Redshift password is required. Set REDSHIFT_PASSWORD environment "
                    "variable or provide 'password' parameter."
                )
            connection_params["user"] = self._user
            connection_params["password"] = self._password

        self._connection = redshift_connector.connect(**connection_params)

    def _connect_with_psycopg2(self) -> None:
        """Connect using psycopg2 library."""
        if not self._user:
            raise ConnectionError(
                "Redshift user is required. Set REDSHIFT_USER environment "
                "variable or provide 'user' parameter."
            )
        if not self._password:
            raise ConnectionError(
                "Redshift password is required. Set REDSHIFT_PASSWORD environment "
                "variable or provide 'password' parameter."
            )

        connection_params = {
            "host": self._host,
            "port": self._port,
            "dbname": self._database,
            "user": self._user,
            "password": self._password,
        }

        if self._ssl:
            connection_params["sslmode"] = self._ssl_mode

        self._connection = psycopg2.connect(**connection_params)

    def disconnect(self) -> None:
        """Close the Redshift connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL query and return results as Polars DataFrame.

        Args:
            sql: The SQL query to execute.

        Returns:
            Polars DataFrame containing the query results.

        Raises:
            QueryError: If the query fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Query: {sql}")

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            return pl.DataFrame(rows, schema=columns, orient="row")
        except Exception as e:
            raise QueryError(f"Query failed: {sql}\nError: {e}") from e

    def execute(self, sql: str) -> None:
        """Execute SQL statement (DDL/DML).

        Args:
            sql: The SQL statement to execute.

        Raises:
            QueryError: If the statement fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Statement: {sql}")

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            self._connection.commit()
            cursor.close()
        except Exception as e:
            self._connection.rollback()
            raise QueryError(f"Statement failed: {sql}\nError: {e}") from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Retrieve data from a table.

        Args:
            table: The table name to query.
            schema: Optional schema name. If provided, queries {schema}.{table}.
                   Falls back to default schema if set.
            limit: Optional maximum number of rows to return.

        Returns:
            Polars DataFrame containing the table data.

        Raises:
            QueryError: If the query fails to execute.
        """
        # Use provided schema, fall back to default schema
        effective_schema = schema or self._schema
        if effective_schema:
            qualified_name = f"{effective_schema}.{table}"
        else:
            qualified_name = table

        sql = f"SELECT * FROM {qualified_name}"  # nosec B608
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"

        return self.query(sql)
