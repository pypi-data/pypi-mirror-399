"""MySQL database connector.

This module provides a connector for MySQL databases using mysql-connector-python.
"""

import os
from typing import Any

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType


@ConnectorFactory.register(DatabaseType.MYSQL)
class MySQLConnector(BaseConnector):
    """Connector for MySQL databases.

    This connector uses mysql-connector-python for database connections.
    Authentication can be configured via environment variables or explicit parameters.

    Environment Variables:
        MYSQL_HOST: MySQL server hostname
        MYSQL_PORT: MySQL server port (default: 3306)
        MYSQL_USER: MySQL username
        MYSQL_PASSWORD: MySQL password
        MYSQL_DATABASE: Default database name

    Example:
        with MySQLConnector(
            host="localhost",
            user="myuser",
            password="mypassword",
            database="mydb"
        ) as conn:
            df = conn.query("SELECT * FROM customers")

        # Or with environment variables
        conn = MySQLConnector()  # Uses MYSQL_* env vars
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
        """Initialize MySQL connector.

        Args:
            host: MySQL server hostname. Falls back to MYSQL_HOST env var.
            port: MySQL server port. Falls back to MYSQL_PORT env var or 3306.
            user: MySQL username. Falls back to MYSQL_USER env var.
            password: MySQL password. Falls back to MYSQL_PASSWORD env var.
            database: Default database name. Falls back to MYSQL_DATABASE env var.
            **kwargs: Additional connection parameters passed to mysql.connector.
        """
        self.host = host or os.environ.get("MYSQL_HOST", "localhost")
        self.port = port or int(os.environ.get("MYSQL_PORT", "3306"))
        self.user = user or os.environ.get("MYSQL_USER")
        self.password = password or os.environ.get("MYSQL_PASSWORD")
        self.database = database or os.environ.get("MYSQL_DATABASE")
        self._extra_kwargs = kwargs
        self._connection: Any = None

    def connect(self) -> None:
        """Establish connection to MySQL database.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        try:
            import mysql.connector
            from mysql.connector import Error as MySQLError

            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                **self._extra_kwargs,
            )
        except ImportError as e:
            raise ConnectionError(
                "mysql-connector-python is required for MySQL connector. "
                "Install with: pip install pycaroline[mysql]"
            ) from e
        except MySQLError as e:
            raise ConnectionError(
                f"Failed to connect to MySQL at {self.host}:{self.port}: {e}"
            ) from e

    def disconnect(self) -> None:
        """Close MySQL connection."""
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
            return self._connection.is_connected()
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
            raise QueryError("Not connected to MySQL. Call connect() first.")

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
            raise QueryError(f"Failed to execute MySQL query: {e}") from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Get data from a table.

        Args:
            table: Table name.
            schema: Database/schema name (optional, uses connection default).
            limit: Maximum number of rows to return.

        Returns:
            Polars DataFrame containing table data.
        """
        # Build fully qualified table name
        if schema:
            full_table = f"`{schema}`.`{table}`"
        else:
            full_table = f"`{table}`"

        sql = f"SELECT * FROM {full_table}"
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"

        return self.query(sql)
