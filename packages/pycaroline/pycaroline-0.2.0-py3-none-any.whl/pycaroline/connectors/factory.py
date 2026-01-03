"""Connector factory for creating database and storage connectors.

This module provides a factory pattern for creating database and storage connectors
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
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class StorageType(Enum):
    """Supported cloud storage types."""

    S3 = "s3"
    GCS = "gcs"


class ConnectorFactory:
    """Factory for creating database and storage connectors.

    This factory supports plugin registration, allowing new connector types
    to be added dynamically using the `register` or `register_storage` decorators.

    Example:
        @ConnectorFactory.register(DatabaseType.SNOWFLAKE)
        class SnowflakeConnector(BaseConnector):
            ...

        @ConnectorFactory.register_storage(StorageType.S3)
        class S3Connector(BaseConnector):
            ...

        # Create a database connector instance
        connector = ConnectorFactory.create(
            DatabaseType.SNOWFLAKE,
            account="my_account",
            user="my_user",
            password="my_password"
        )

        # Create a storage connector instance
        connector = ConnectorFactory.create(
            StorageType.S3,
            bucket="my-bucket"
        )
    """

    _registry: dict[DatabaseType, type[BaseConnector]] = {}
    _storage_registry: dict[StorageType, type[BaseConnector]] = {}

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
    def register_storage(
        cls, storage_type: StorageType
    ) -> Callable[[type[BaseConnector]], type[BaseConnector]]:
        """Decorator to register a connector class for a storage type.

        Args:
            storage_type: The storage type to register the connector for.

        Returns:
            Decorator function that registers the connector class.

        Example:
            @ConnectorFactory.register_storage(StorageType.S3)
            class S3Connector(BaseConnector):
                ...
        """

        def decorator(connector_class: type[BaseConnector]) -> type[BaseConnector]:
            cls._storage_registry[storage_type] = connector_class
            return connector_class

        return decorator

    @classmethod
    def create(
        cls, source_type: DatabaseType | StorageType | str, **kwargs: Any
    ) -> BaseConnector:
        """Create a connector instance for the specified type.

        Args:
            source_type: The type of source to connect to (DatabaseType, StorageType, or string).
            **kwargs: Connection parameters passed to the connector constructor.

        Returns:
            An instance of the appropriate connector class.

        Raises:
            ValueError: If the source type is not registered.
        """
        # Handle string input
        if isinstance(source_type, str):
            # Try database types first
            for db_type in DatabaseType:
                if db_type.value == source_type:
                    source_type = db_type
                    break
            else:
                # Try storage types
                for storage_type in StorageType:
                    if storage_type.value == source_type:
                        source_type = storage_type
                        break
                else:
                    all_types = [t.value for t in DatabaseType] + [
                        t.value for t in StorageType
                    ]
                    raise ValueError(
                        f"Unknown source type: {source_type}. Available types: {all_types}"
                    )

        # Handle DatabaseType
        if isinstance(source_type, DatabaseType):
            if source_type not in cls._registry:
                available = [t.value for t in cls._registry.keys()]
                raise ValueError(
                    f"Unknown database type: {source_type.value}. "
                    f"Available types: {available}"
                )
            return cls._registry[source_type](**kwargs)

        # Handle StorageType
        if isinstance(source_type, StorageType):
            if source_type not in cls._storage_registry:
                available = [t.value for t in cls._storage_registry.keys()]
                raise ValueError(
                    f"Unknown storage type: {source_type.value}. "
                    f"Available types: {available}"
                )
            return cls._storage_registry[source_type](**kwargs)

        raise ValueError(f"Invalid source type: {source_type}")

    @classmethod
    def get_registered_types(cls) -> list[DatabaseType]:
        """Get list of registered database types.

        Returns:
            List of DatabaseType enums that have registered connectors.
        """
        return list(cls._registry.keys())

    @classmethod
    def get_registered_storage_types(cls) -> list[StorageType]:
        """Get list of registered storage types.

        Returns:
            List of StorageType enums that have registered connectors.
        """
        return list(cls._storage_registry.keys())

    @classmethod
    def is_registered(cls, source_type: DatabaseType | StorageType) -> bool:
        """Check if a source type has a registered connector.

        Args:
            source_type: The source type to check (DatabaseType or StorageType).

        Returns:
            True if the type is registered, False otherwise.
        """
        if isinstance(source_type, DatabaseType):
            return source_type in cls._registry
        if isinstance(source_type, StorageType):
            return source_type in cls._storage_registry
        return False
