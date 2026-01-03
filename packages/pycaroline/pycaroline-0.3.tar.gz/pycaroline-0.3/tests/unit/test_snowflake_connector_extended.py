"""Extended unit tests for SnowflakeConnector to improve coverage.

Tests for authentication methods, execute, and error handling.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from pycaroline.connectors.base import ConnectionError, QueryError


class TestSnowflakeConnectorAuth:
    """Tests for SnowflakeConnector authentication methods."""

    @pytest.fixture
    def mock_snowflake(self):
        """Mock snowflake.connector module."""
        with patch.dict(
            "sys.modules",
            {"snowflake": MagicMock(), "snowflake.connector": MagicMock()},
        ):
            yield

    def test_connect_with_sso_authenticator(self, mock_snowflake):
        """Test connection with SSO (externalbrowser) authenticator."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector

                connector = SnowflakeConnector(
                    account="test_account",
                    user="test_user",
                    authenticator="externalbrowser",
                )

                connector.connect()

                # Verify externalbrowser authenticator was used
                call_kwargs = mock_sf.connector.connect.call_args[1]
                assert call_kwargs["authenticator"] == "externalbrowser"

    def test_connect_with_oauth_token(self, mock_snowflake):
        """Test connection with OAuth token."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector

                connector = SnowflakeConnector(
                    account="test_account",
                    user="test_user",
                    authenticator="oauth",
                    token="test_oauth_token",
                )

                connector.connect()

                call_kwargs = mock_sf.connector.connect.call_args[1]
                assert call_kwargs["authenticator"] == "oauth"
                assert call_kwargs["token"] == "test_oauth_token"

    def test_connect_without_auth_raises_error(self, mock_snowflake):
        """Test that connection without any auth method raises error."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector(
                account="test_account",
                user="test_user",
                # No password, no private key, no token, no SSO
            )

            with pytest.raises(ConnectionError) as exc_info:
                connector.connect()

            assert "No valid authentication method" in str(exc_info.value)

    def test_connect_missing_account_raises_error(self, mock_snowflake):
        """Test that missing account raises ConnectionError."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            # Clear environment variables
            with patch.dict(os.environ, {}, clear=True):
                connector = SnowflakeConnector(user="test_user", password="test_pass")

                with pytest.raises(ConnectionError) as exc_info:
                    connector.connect()

                assert "account is required" in str(exc_info.value)

    def test_connect_missing_user_raises_error(self, mock_snowflake):
        """Test that missing user raises ConnectionError."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            with patch.dict(os.environ, {}, clear=True):
                connector = SnowflakeConnector(
                    account="test_account", password="test_pass"
                )

                with pytest.raises(ConnectionError) as exc_info:
                    connector.connect()

                assert "user is required" in str(exc_info.value)


class TestSnowflakeConnectorPrivateKey:
    """Tests for private key authentication."""

    def test_private_key_file_not_found(self):
        """Test that missing private key file raises ConnectionError."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector(
                account="test_account",
                user="test_user",
                private_key_path="/nonexistent/path/key.pem",
            )

            with pytest.raises(ConnectionError) as exc_info:
                connector.connect()

            assert "Private key file not found" in str(exc_info.value)


class TestSnowflakeConnectorExecute:
    """Tests for execute method."""

    def test_execute_runs_statement(self):
        """Test that execute runs SQL statement."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector

                mock_connection = MagicMock()
                mock_cursor = MagicMock()
                mock_connection.execute_string.return_value = [mock_cursor]
                mock_sf.connector.connect.return_value = mock_connection

                connector = SnowflakeConnector(
                    account="test",
                    user="test",
                    password="test",
                )
                connector.connect()
                connector.execute("CREATE TABLE test (id INT)")

                mock_connection.execute_string.assert_called_once()

    def test_execute_not_connected_raises_error(self):
        """Test that execute raises error when not connected."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector(
                account="test",
                user="test",
                password="test",
            )

            with pytest.raises(QueryError) as exc_info:
                connector.execute("CREATE TABLE test (id INT)")

            assert "Not connected" in str(exc_info.value)

    def test_execute_raises_on_error(self):
        """Test that execute raises QueryError on failure."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from snowflake.connector.errors import ProgrammingError

                from pycaroline.connectors.snowflake import SnowflakeConnector

                mock_connection = MagicMock()
                mock_connection.execute_string.side_effect = ProgrammingError(
                    "Syntax error"
                )
                mock_sf.connector.connect.return_value = mock_connection

                connector = SnowflakeConnector(
                    account="test",
                    user="test",
                    password="test",
                )
                connector.connect()

                with pytest.raises(QueryError) as exc_info:
                    connector.execute("INVALID SQL")

                assert "Statement failed" in str(exc_info.value)


class TestSnowflakeConnectorQuery:
    """Tests for query method."""

    def test_query_not_connected_raises_error(self):
        """Test that query raises error when not connected."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector(
                account="test",
                user="test",
                password="test",
            )

            with pytest.raises(QueryError) as exc_info:
                connector.query("SELECT * FROM test")

            assert "Not connected" in str(exc_info.value)


class TestSnowflakeConnectorConfigFile:
    """Tests for TOML config file loading."""

    def test_load_config_from_nonexistent_file(self):
        """Test that nonexistent config file is handled gracefully."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            # Should not raise, just use defaults
            connector = SnowflakeConnector(
                config_path="/nonexistent/config.toml",
                account="fallback_account",
                user="fallback_user",
                password="fallback_pass",
            )

            assert connector._account == "fallback_account"


class TestSnowflakeConnectorDisconnect:
    """Tests for disconnect method."""

    def test_disconnect_when_not_connected(self):
        """Test that disconnect is safe when not connected."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector(
                account="test",
                user="test",
                password="test",
            )

            # Should not raise
            connector.disconnect()
            assert connector._connection is None

    def test_disconnect_closes_connection(self):
        """Test that disconnect closes the connection."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector

                mock_connection = MagicMock()
                mock_sf.connector.connect.return_value = mock_connection

                connector = SnowflakeConnector(
                    account="test",
                    user="test",
                    password="test",
                )
                connector.connect()
                connector.disconnect()

                mock_connection.close.assert_called_once()
                assert connector._connection is None
