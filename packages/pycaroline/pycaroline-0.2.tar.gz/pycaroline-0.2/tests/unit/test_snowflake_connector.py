"""Unit tests for SnowflakeConnector with mocked dependencies."""

from unittest.mock import MagicMock, patch

import polars as pl
import pytest


class TestSnowflakeConnectorConnect:
    """Tests for SnowflakeConnector.connect method."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_connect_with_password(self, mock_sf):
        """Test connecting with password authentication."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()

        assert connector._connection == mock_conn
        mock_sf.connector.connect.assert_called_once()

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_connect_with_sso(self, mock_sf):
        """Test connecting with SSO authentication."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", authenticator="externalbrowser"
        )
        connector.connect()

        call_kwargs = mock_sf.connector.connect.call_args[1]
        assert call_kwargs["authenticator"] == "externalbrowser"

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_connect_with_oauth(self, mock_sf):
        """Test connecting with OAuth authentication."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account",
            user="test_user",
            authenticator="oauth",
            token="test_token",
        )
        connector.connect()

        call_kwargs = mock_sf.connector.connect.call_args[1]
        assert call_kwargs["authenticator"] == "oauth"
        assert call_kwargs["token"] == "test_token"

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_connect_with_warehouse_and_database(self, mock_sf):
        """Test connecting with warehouse and database specified."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account",
            user="test_user",
            password="test_pass",
            warehouse="test_wh",
            database="test_db",
            schema="test_schema",
            role="test_role",
        )
        connector.connect()

        call_kwargs = mock_sf.connector.connect.call_args[1]
        assert call_kwargs["warehouse"] == "test_wh"
        assert call_kwargs["database"] == "test_db"
        assert call_kwargs["schema"] == "test_schema"
        assert call_kwargs["role"] == "test_role"


class TestSnowflakeConnectorDisconnect:
    """Tests for SnowflakeConnector.disconnect method."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_disconnect_closes_connection(self, mock_sf):
        """Test disconnect closes the connection."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()
        connector.disconnect()

        mock_conn.close.assert_called_once()
        assert connector._connection is None

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_disconnect_when_not_connected(self):
        """Test disconnect is safe when not connected."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.disconnect()  # Should not raise


class TestSnowflakeConnectorQuery:
    """Tests for SnowflakeConnector.query method."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_query_returns_dataframe(self, mock_sf):
        """Test query returns a polars DataFrame."""
        import pandas as pd

        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Snowflake returns pandas internally, connector converts to polars
        mock_cursor.fetch_pandas_all.return_value = pd.DataFrame({"col": [1, 2]})
        mock_conn.cursor.return_value = mock_cursor
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()
        result = connector.query("SELECT * FROM test")

        assert isinstance(result, pl.DataFrame)
        mock_cursor.execute.assert_called_with("SELECT * FROM test")

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    @patch("pycaroline.connectors.snowflake.DatabaseError", Exception)
    @patch("pycaroline.connectors.snowflake.ProgrammingError", Exception)
    def test_query_raises_on_error(self, mock_sf):
        """Test query raises QueryError on database error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()

        with pytest.raises(QueryError):
            connector.query("SELECT * FROM nonexistent")


class TestSnowflakeConnectorExecute:
    """Tests for SnowflakeConnector.execute method."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    def test_execute_runs_statement(self, mock_sf):
        """Test execute runs SQL statement."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute_string.return_value = [mock_cursor]
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()
        connector.execute("CREATE TABLE test (id INT)")

        mock_conn.execute_string.assert_called_with("CREATE TABLE test (id INT)")


class TestSnowflakeConnectorConfigFile:
    """Tests for SnowflakeConnector with config file."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake._load_toml_config")
    def test_load_config_from_file(self, mock_load_toml):
        """Test loading configuration from TOML file."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_load_toml.return_value = {
            "default": {
                "account": "file_account",
                "user": "file_user",
                "password": "file_pass",
            }
        }

        with patch("os.path.exists", return_value=True):
            connector = SnowflakeConnector(config_path="~/.snowflake/config.toml")

        assert connector._account == "file_account"
        assert connector._user == "file_user"

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake._load_toml_config")
    def test_direct_params_override_config_file(self, mock_load_toml):
        """Test direct parameters override config file values."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_load_toml.return_value = {
            "default": {"account": "file_account", "user": "file_user"}
        }

        with patch("os.path.exists", return_value=True):
            connector = SnowflakeConnector(
                account="direct_account", config_path="~/.snowflake/config.toml"
            )

        assert connector._account == "direct_account"


class TestSnowflakeConnectorPrivateKey:
    """Tests for private key authentication."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    @patch("os.path.exists", return_value=False)
    def test_private_key_file_not_found(self, mock_exists, mock_sf):
        """Test error when private key file doesn't exist."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(
            account="test_account",
            user="test_user",
            private_key_path="/nonexistent/key.pem",
        )

        with pytest.raises(ConnectionError, match="not found"):
            connector.connect()


class TestSnowflakeConnectorExecuteError:
    """Tests for execute method error handling."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    @patch("pycaroline.connectors.snowflake.DatabaseError", Exception)
    @patch("pycaroline.connectors.snowflake.ProgrammingError", Exception)
    def test_execute_raises_on_error(self, mock_sf):
        """Test execute raises QueryError on database error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_conn = MagicMock()
        mock_conn.execute_string.side_effect = Exception("Execute failed")
        mock_sf.connector.connect.return_value = mock_conn

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )
        connector.connect()

        with pytest.raises(QueryError):
            connector.execute("INVALID SQL")


class TestSnowflakeConnectorConnectionError:
    """Tests for connection error handling."""

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    @patch("pycaroline.connectors.snowflake.snowflake")
    @patch("pycaroline.connectors.snowflake.DatabaseError", Exception)
    @patch("pycaroline.connectors.snowflake.ProgrammingError", Exception)
    def test_connect_raises_on_database_error(self, mock_sf):
        """Test connect raises ConnectionError on database error."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.snowflake import SnowflakeConnector

        mock_sf.connector.connect.side_effect = Exception("Connection failed")

        connector = SnowflakeConnector(
            account="test_account", user="test_user", password="test_pass"
        )

        with pytest.raises(ConnectionError):
            connector.connect()
