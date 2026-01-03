"""Unit tests for ConnectorFactory.

Tests connector registration, creation, and error handling.
"""

import pytest

from pycaroline.connectors.base import BaseConnector
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType


class TestConnectorRegistration:
    """Tests for connector registration functionality."""

    def test_register_decorator_adds_connector_to_registry(self):
        """Test that the register decorator adds a connector class to the registry."""

        # Create a test connector class
        @ConnectorFactory.register(DatabaseType.SNOWFLAKE)
        class TestSnowflakeConnector(BaseConnector):
            def connect(self):
                pass

            def disconnect(self):
                pass

            def query(self, sql):
                pass

        # Verify it's registered
        assert ConnectorFactory.is_registered(DatabaseType.SNOWFLAKE)
        assert DatabaseType.SNOWFLAKE in ConnectorFactory.get_registered_types()

    def test_is_registered_returns_false_for_unregistered_type(self):
        """Test that is_registered returns False for types not in registry."""
        # Clear registry for this test
        original_registry = ConnectorFactory._registry.copy()

        # Create a fresh registry state
        ConnectorFactory._registry = {}

        try:
            assert not ConnectorFactory.is_registered(DatabaseType.BIGQUERY)
        finally:
            # Restore original registry
            ConnectorFactory._registry = original_registry

    def test_get_registered_types_returns_list_of_registered_types(self):
        """Test that get_registered_types returns all registered database types."""
        registered = ConnectorFactory.get_registered_types()
        assert isinstance(registered, list)
        # Should have at least the types we've registered
        for db_type in registered:
            assert isinstance(db_type, DatabaseType)


class TestConnectorCreation:
    """Tests for connector creation functionality."""

    def test_create_returns_connector_instance_for_registered_type(self):
        """Test that create returns an instance of the registered connector."""

        # Create a test connector that accepts kwargs
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

        # Register it temporarily
        original_registry = ConnectorFactory._registry.copy()
        ConnectorFactory._registry[DatabaseType.SNOWFLAKE] = TestConnector

        try:
            connector = ConnectorFactory.create(
                DatabaseType.SNOWFLAKE,
                account="test_account",
                user="test_user",
                password="test_password",
            )
            assert connector is not None
            assert isinstance(connector, BaseConnector)
            assert connector.kwargs["account"] == "test_account"
        finally:
            # Restore original registry
            ConnectorFactory._registry = original_registry

    def test_create_raises_value_error_for_unknown_type(self):
        """Test that create raises ValueError for unregistered database types."""
        # Clear registry temporarily
        original_registry = ConnectorFactory._registry.copy()
        ConnectorFactory._registry = {}

        try:
            with pytest.raises(ValueError) as exc_info:
                ConnectorFactory.create(DatabaseType.SNOWFLAKE)

            assert "Unknown database type" in str(exc_info.value)
            assert "snowflake" in str(exc_info.value)
        finally:
            # Restore original registry
            ConnectorFactory._registry = original_registry

    def test_create_passes_kwargs_to_connector_constructor(self):
        """Test that create passes keyword arguments to the connector constructor."""
        # Create a test connector that captures init args
        captured_kwargs = {}

        class TestConnector(BaseConnector):
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)
                self._connection = None

            def connect(self):
                pass

            def disconnect(self):
                pass

            def query(self, sql):
                pass

        # Register it
        original_registry = ConnectorFactory._registry.copy()
        ConnectorFactory._registry[DatabaseType.SNOWFLAKE] = TestConnector

        try:
            ConnectorFactory.create(
                DatabaseType.SNOWFLAKE,
                account="my_account",
                user="my_user",
                custom_param="custom_value",
            )

            assert captured_kwargs["account"] == "my_account"
            assert captured_kwargs["user"] == "my_user"
            assert captured_kwargs["custom_param"] == "custom_value"
        finally:
            # Restore original registry
            ConnectorFactory._registry = original_registry


class TestConnectorFactoryIntegration:
    """Integration tests for connector factory with actual connector classes."""

    def test_snowflake_connector_is_registered(self):
        """Test that SnowflakeConnector is registered with the factory."""
        # Import to trigger registration
        try:
            import pycaroline.connectors.snowflake  # noqa: F401

            assert ConnectorFactory.is_registered(DatabaseType.SNOWFLAKE)
        except ImportError:
            pytest.skip("snowflake-connector-python not installed")

    def test_bigquery_connector_is_registered(self):
        """Test that BigQueryConnector is registered with the factory."""
        try:
            import pycaroline.connectors.bigquery  # noqa: F401

            assert ConnectorFactory.is_registered(DatabaseType.BIGQUERY)
        except ImportError:
            pytest.skip("google-cloud-bigquery not installed")

    def test_redshift_connector_is_registered(self):
        """Test that RedshiftConnector is registered with the factory."""
        try:
            import pycaroline.connectors.redshift  # noqa: F401

            assert ConnectorFactory.is_registered(DatabaseType.REDSHIFT)
        except ImportError:
            pytest.skip("redshift-connector or psycopg2 not installed")

    def test_error_message_includes_available_types(self):
        """Test that error message for unknown type includes available types."""

        # Register a test connector
        class TestConnector(BaseConnector):
            def __init__(self, **kwargs):
                self._connection = None

            def connect(self):
                pass

            def disconnect(self):
                pass

            def query(self, sql):
                pass

        original_registry = ConnectorFactory._registry.copy()
        ConnectorFactory._registry = {DatabaseType.SNOWFLAKE: TestConnector}

        try:
            with pytest.raises(ValueError) as exc_info:
                ConnectorFactory.create(DatabaseType.BIGQUERY)

            error_msg = str(exc_info.value)
            assert "Available types" in error_msg
            assert "snowflake" in error_msg
        finally:
            ConnectorFactory._registry = original_registry
