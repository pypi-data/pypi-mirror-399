"""PostgreSQL database connector.

This module provides a connector for PostgreSQL databases using psycopg2.
"""

import os
from typing import Any

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType


@ConnectorFactory.register(DatabaseType.POSTGRESQL)
class PostgreSQLConnector(BaseConnector):
    """Connector for PostgreSQL databases.

    This connector uses psycopg2 for database connections.
    Authentication can be configured via environment variables or explicit parameters.

    Environment Variables:
        PGHOST: PostgreSQL server hostname
        PGPORT: PostgreSQL server port (default: 5432)
        PGUSER: PostgreSQL username
        PGPASSWORD: PostgreSQL password
        PGDATABASE: Default database name

    Example:
        with PostgreSQLConnector(
            host="localhost",
            user="myuser",
            password="mypassword",
            database="mydb"
        ) as conn:
            df = conn.query("SELECT * FROM customers")

        # Or with environment variables
        conn = PostgreSQLConnector()  # Uses PG* env vars
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize PostgreSQL connector.

        Args:
            host: PostgreSQL server hostname. Falls back to PGHOST env var.
            port: PostgreSQL server port. Falls back to PGPORT env var or 5432.
            user: PostgreSQL username. Falls back to PGUSER env var.
            password: PostgreSQL password. Falls back to PGPASSWORD env var.
            database: Default database name. Falls back to PGDATABASE env var.
            **kwargs: Additional connection parameters passed to psycopg2.
        """
        self.host = host or os.environ.get("PGHOST", "localhost")
        self.port = port or int(os.environ.get("PGPORT", "5432"))
        self.user = user or os.environ.get("PGUSER")
        self.password = password or os.environ.get("PGPASSWORD")
        self.database = database or os.environ.get("PGDATABASE")
        self._extra_kwargs = kwargs
        self._connection: Any = None

    def connect(self) -> None:
        """Establish connection to PostgreSQL database.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        try:
            import psycopg2
            from psycopg2 import OperationalError

            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database,
                **self._extra_kwargs,
            )
        except ImportError as e:
            raise ConnectionError(
                "psycopg2 is required for PostgreSQL connector. "
                "Install with: pip install pycaroline[postgresql]"
            ) from e
        except OperationalError as e:
            raise ConnectionError(
                f"Failed to connect to PostgreSQL at {self.host}:{self.port}: {e}"
            ) from e

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None

    def has_open_connection(self) -> bool:
        """Check if connection is open.

        Returns:
            True if connected, False otherwise.
        """
        if self._connection is None:
            return False
        try:
            return not self._connection.closed
        except Exception:
            return False

    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL query and return results as DataFrame.

        Args:
            sql: SQL query to execute.

        Returns:
            Polars DataFrame containing query results.

        Raises:
            QueryError: If query execution fails.
        """
        if not self.has_open_connection():
            raise QueryError("Not connected to PostgreSQL. Call connect() first.")

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                return pl.DataFrame({col: [] for col in columns})

            return pl.DataFrame(rows, schema=columns, orient="row")
        except Exception as e:
            raise QueryError(f"Failed to execute PostgreSQL query: {e}") from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Get data from a table.

        Args:
            table: Table name.
            schema: Schema name (optional, defaults to 'public').
            limit: Maximum number of rows to return.

        Returns:
            Polars DataFrame containing table data.
        """
        # Build fully qualified table name
        schema = schema or "public"
        full_table = f'"{schema}"."{table}"'

        sql = f"SELECT * FROM {full_table}"
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"

        return self.query(sql)
