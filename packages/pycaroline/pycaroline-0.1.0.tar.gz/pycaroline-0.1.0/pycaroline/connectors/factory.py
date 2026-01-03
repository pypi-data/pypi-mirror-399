"""Connector factory for creating database connectors.

This module provides a factory pattern for creating database connectors
with plugin registration support.
"""

from collections.abc import Callable
from enum import Enum
from typing import Any

from pycaroline.connectors.base import BaseConnector


class DatabaseType(Enum):
    """Supported database types."""

    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"


class ConnectorFactory:
    """Factory for creating database connectors.

    This factory supports plugin registration, allowing new connector types
    to be added dynamically using the `register` decorator.

    Example:
        @ConnectorFactory.register(DatabaseType.SNOWFLAKE)
        class SnowflakeConnector(BaseConnector):
            ...

        # Create a connector instance
        connector = ConnectorFactory.create(
            DatabaseType.SNOWFLAKE,
            account="my_account",
            user="my_user",
            password="my_password"
        )
    """

    _registry: dict[DatabaseType, type[BaseConnector]] = {}

    @classmethod
    def register(
        cls, db_type: DatabaseType
    ) -> Callable[[type[BaseConnector]], type[BaseConnector]]:
        """Decorator to register a connector class for a database type.

        Args:
            db_type: The database type to register the connector for.

        Returns:
            Decorator function that registers the connector class.

        Example:
            @ConnectorFactory.register(DatabaseType.SNOWFLAKE)
            class SnowflakeConnector(BaseConnector):
                ...
        """

        def decorator(connector_class: type[BaseConnector]) -> type[BaseConnector]:
            cls._registry[db_type] = connector_class
            return connector_class

        return decorator

    @classmethod
    def create(cls, db_type: DatabaseType, **kwargs: Any) -> BaseConnector:
        """Create a connector instance for the specified database type.

        Args:
            db_type: The type of database to connect to.
            **kwargs: Connection parameters passed to the connector constructor.

        Returns:
            An instance of the appropriate connector class.

        Raises:
            ValueError: If the database type is not registered.
        """
        if db_type not in cls._registry:
            available = [t.value for t in cls._registry.keys()]
            raise ValueError(
                f"Unknown database type: {db_type.value}. Available types: {available}"
            )
        return cls._registry[db_type](**kwargs)

    @classmethod
    def get_registered_types(cls) -> list[DatabaseType]:
        """Get list of registered database types.

        Returns:
            List of DatabaseType enums that have registered connectors.
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, db_type: DatabaseType) -> bool:
        """Check if a database type has a registered connector.

        Args:
            db_type: The database type to check.

        Returns:
            True if the type is registered, False otherwise.
        """
        return db_type in cls._registry
