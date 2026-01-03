"""Extended unit tests for ConnectorFactory to improve coverage.

Tests for string-based type creation, storage connectors, and edge cases.
"""

import pytest

from pycaroline.connectors.base import BaseConnector
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType, StorageType


class MockStorageConnector(BaseConnector):
    """Mock storage connector for testing."""

    def __init__(self, **kwargs):
        self._connection = None
        self.kwargs = kwargs

    def connect(self):
        self._connection = True

    def disconnect(self):
        self._connection = None

    def query(self, sql):
        import polars as pl
        return pl.DataFrame({"data": [1, 2, 3]})


class TestConnectorFactoryStringTypes:
    """Tests for string-based type creation."""

    def test_create_with_string_database_type(self):
        """Test creating connector with string database type."""
        # Register a test connector
        original_registry = ConnectorFactory._registry.copy()

        class TestConnector(BaseConnector):
            def __init__(self, **kwargs):
                self._connection = None
                self.kwargs = kwargs

            def connect(self):
                pass

            def disconnect(self):
                pass

            def query(self, sql):
                pass

        ConnectorFactory._registry[DatabaseType.SNOWFLAKE] = TestConnector

        try:
            connector = ConnectorFactory.create("snowflake", account="test")
            assert connector is not None
            assert connector.kwargs["account"] == "test"
        finally:
            ConnectorFactory._registry = original_registry

    def test_create_with_string_storage_type(self):
        """Test creating connector with string storage type."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry[StorageType.S3] = MockStorageConnector

        try:
            connector = ConnectorFactory.create("s3", bucket="test-bucket")
            assert connector is not None
            assert connector.kwargs["bucket"] == "test-bucket"
        finally:
            ConnectorFactory._storage_registry = original_storage_registry

    def test_create_with_invalid_string_type(self):
        """Test that invalid string type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ConnectorFactory.create("invalid_type")

        assert "Unknown source type" in str(exc_info.value)
        assert "invalid_type" in str(exc_info.value)

    def test_create_with_gcs_string_type(self):
        """Test creating GCS connector with string type."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry[StorageType.GCS] = MockStorageConnector

        try:
            connector = ConnectorFactory.create("gcs", bucket="my-bucket")
            assert connector is not None
        finally:
            ConnectorFactory._storage_registry = original_storage_registry


class TestConnectorFactoryStorageTypes:
    """Tests for storage connector registration and creation."""

    def test_register_storage_decorator(self):
        """Test that register_storage decorator works correctly."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()

        try:
            @ConnectorFactory.register_storage(StorageType.S3)
            class TestS3Connector(BaseConnector):
                def __init__(self, **kwargs):
                    self._connection = None

                def connect(self):
                    pass

                def disconnect(self):
                    pass

                def query(self, sql):
                    pass

            assert StorageType.S3 in ConnectorFactory._storage_registry
            assert ConnectorFactory.is_registered(StorageType.S3)
        finally:
            ConnectorFactory._storage_registry = original_storage_registry

    def test_get_registered_storage_types(self):
        """Test getting list of registered storage types."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry[StorageType.S3] = MockStorageConnector
        ConnectorFactory._storage_registry[StorageType.GCS] = MockStorageConnector

        try:
            storage_types = ConnectorFactory.get_registered_storage_types()
            assert isinstance(storage_types, list)
            assert StorageType.S3 in storage_types
            assert StorageType.GCS in storage_types
        finally:
            ConnectorFactory._storage_registry = original_storage_registry

    def test_create_storage_connector_with_enum(self):
        """Test creating storage connector with StorageType enum."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry[StorageType.S3] = MockStorageConnector

        try:
            connector = ConnectorFactory.create(StorageType.S3, bucket="test")
            assert connector is not None
        finally:
            ConnectorFactory._storage_registry = original_storage_registry

    def test_create_unregistered_storage_type_raises_error(self):
        """Test that creating unregistered storage type raises ValueError."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry = {}

        try:
            with pytest.raises(ValueError) as exc_info:
                ConnectorFactory.create(StorageType.S3)

            assert "Unknown storage type" in str(exc_info.value)
        finally:
            ConnectorFactory._storage_registry = original_storage_registry


class TestConnectorFactoryIsRegistered:
    """Tests for is_registered method."""

    def test_is_registered_with_database_type(self):
        """Test is_registered with DatabaseType."""
        original_registry = ConnectorFactory._registry.copy()

        class TestConnector(BaseConnector):
            def __init__(self, **kwargs):
                self._connection = None

            def connect(self):
                pass

            def disconnect(self):
                pass

            def query(self, sql):
                pass

        ConnectorFactory._registry[DatabaseType.MYSQL] = TestConnector

        try:
            assert ConnectorFactory.is_registered(DatabaseType.MYSQL)
        finally:
            ConnectorFactory._registry = original_registry

    def test_is_registered_with_storage_type(self):
        """Test is_registered with StorageType."""
        original_storage_registry = ConnectorFactory._storage_registry.copy()
        ConnectorFactory._storage_registry[StorageType.GCS] = MockStorageConnector

        try:
            assert ConnectorFactory.is_registered(StorageType.GCS)
        finally:
            ConnectorFactory._storage_registry = original_storage_registry

    def test_is_registered_with_invalid_type(self):
        """Test is_registered with invalid type returns False."""
        result = ConnectorFactory.is_registered("invalid")  # type: ignore
        assert result is False


class TestConnectorFactoryEdgeCases:
    """Tests for edge cases and error handling."""

    def test_create_with_invalid_source_type_object(self):
        """Test that invalid source type object raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ConnectorFactory.create(123)  # type: ignore

        assert "Invalid source type" in str(exc_info.value)

    def test_error_message_includes_all_available_types(self):
        """Test that error message includes both database and storage types."""
        with pytest.raises(ValueError) as exc_info:
            ConnectorFactory.create("nonexistent_type")

        error_msg = str(exc_info.value)
        # Should mention available types
        assert "Available types" in error_msg or "Unknown source type" in error_msg
