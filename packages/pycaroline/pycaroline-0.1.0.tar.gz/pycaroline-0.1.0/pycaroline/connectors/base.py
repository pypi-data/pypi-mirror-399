"""Base connector interface for database connections.

This module defines the abstract base class that all database connectors must implement.
"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any

import polars as pl


class BaseConnector(ABC):
    """Abstract base class for database connectors.

    All database connectors (Snowflake, BigQuery, Redshift) must inherit from this
    class and implement the abstract methods.

    The connector supports context manager protocol for automatic connection management:

        with SnowflakeConnector(...) as conn:
            df = conn.query("SELECT * FROM table")

    Attributes:
        _connection: The underlying database connection object (set by subclasses).
    """

    _connection: Any = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection.

        Should be safe to call even if not connected.
        """
        pass

    @abstractmethod
    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL query and return results as Polars DataFrame.

        Args:
            sql: The SQL query to execute.

        Returns:
            Polars DataFrame containing the query results.

        Raises:
            QueryError: If the query fails to execute.
        """
        pass

    def has_open_connection(self) -> bool:
        """Check if there is an active database connection.

        Returns:
            True if connected, False otherwise.
        """
        return self._connection is not None

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
            limit: Optional maximum number of rows to return.

        Returns:
            Polars DataFrame containing the table data.

        Raises:
            QueryError: If the query fails to execute.
        """
        qualified_name = f"{schema}.{table}" if schema else table
        sql = f"SELECT * FROM {qualified_name}"  # nosec B608
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"
        return self.query(sql)

    def __enter__(self) -> "BaseConnector":
        """Enter context manager - establish connection.

        Returns:
            Self with active connection.
        """
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: "TracebackType | None",
    ) -> None:
        """Exit context manager - close connection.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """
        self.disconnect()


class ConnectionError(Exception):
    """Raised when a database connection cannot be established."""

    pass


class QueryError(Exception):
    """Raised when a database query fails to execute."""

    pass
