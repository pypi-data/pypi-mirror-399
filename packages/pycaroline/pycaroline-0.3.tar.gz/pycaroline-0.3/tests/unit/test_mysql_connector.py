"""Unit tests for MySQL database connector."""

import sys
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from pycaroline.connectors.base import ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType


class TestMySQLConnector:
    """Tests for MySQLConnector class."""

    def test_init_with_explicit_params(self):
        """Test initialization with explicit parameters."""
        from pycaroline.connectors.mysql import MySQLConnector

        conn = MySQLConnector(
            host="myhost",
            port=3307,
            user="myuser",
            password="mypassword",
            database="mydb",
        )

        assert conn.host == "myhost"
        assert conn.port == 3307
        assert conn.user == "myuser"
        assert conn.password == "mypassword"
        assert conn.database == "mydb"

    def test_init_with_env_vars(self, monkeypatch):
        """Test initialization with environment variables."""
        from pycaroline.connectors.mysql import MySQLConnector

        monkeypatch.setenv("MYSQL_HOST", "envhost")
        monkeypatch.setenv("MYSQL_PORT", "3308")
        monkeypatch.setenv("MYSQL_USER", "envuser")
        monkeypatch.setenv("MYSQL_PASSWORD", "envpassword")
        monkeypatch.setenv("MYSQL_DATABASE", "envdb")

        conn = MySQLConnector()

        assert conn.host == "envhost"
        assert conn.port == 3308
        assert conn.user == "envuser"
        assert conn.password == "envpassword"
        assert conn.database == "envdb"

    def test_init_defaults(self):
        """Test default values."""
        from pycaroline.connectors.mysql import MySQLConnector

        conn = MySQLConnector()

        assert conn.host == "localhost"
        assert conn.port == 3306

    def test_connect_success(self):
        """Test successful connection."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_mysql_connector = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")
            conn.connect()

            assert conn.has_open_connection()
            mock_mysql_connector.connect.assert_called_once()

    def test_connect_failure(self):
        """Test connection failure."""
        from mysql.connector import Error as MySQLError

        from pycaroline.connectors.mysql import MySQLConnector

        mock_mysql_connector = MagicMock()
        mock_mysql_connector.connect.side_effect = MySQLError("Connection refused")

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = MySQLError

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")

            with pytest.raises(ConnectionError) as exc_info:
                conn.connect()

            assert "localhost" in str(exc_info.value)

    def test_disconnect(self):
        """Test disconnection."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_mysql_connector = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")
            conn.connect()
            assert conn.has_open_connection()

            mock_connection.is_connected.return_value = False
            conn.disconnect()
            assert not conn.has_open_connection()

    def test_query_not_connected(self):
        """Test query when not connected."""
        from pycaroline.connectors.mysql import MySQLConnector

        conn = MySQLConnector()

        with pytest.raises(QueryError) as exc_info:
            conn.query("SELECT 1")

        assert "Not connected" in str(exc_info.value)

    def test_query_success(self):
        """Test successful query execution."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]

        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor

        mock_mysql_connector = MagicMock()
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")
            conn.connect()
            result = conn.query("SELECT id, name FROM users")

            assert isinstance(result, pl.DataFrame)
            assert result["id"].to_list() == [1, 2]
            assert result["name"].to_list() == ["Alice", "Bob"]

    def test_query_empty_result(self):
        """Test query with empty result."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = []

        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor

        mock_mysql_connector = MagicMock()
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")
            conn.connect()
            result = conn.query("SELECT id, name FROM users WHERE 1=0")

            assert isinstance(result, pl.DataFrame)
            assert len(result) == 0
            assert "id" in result.columns
            assert "name" in result.columns

    def test_get_table(self):
        """Test get_table method."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_cursor = MagicMock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = [(1,), (2,)]

        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor

        mock_mysql_connector = MagicMock()
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            conn = MySQLConnector(host="localhost", user="user", password="pass")
            conn.connect()
            conn.get_table("users", schema="mydb", limit=10)

            mock_cursor.execute.assert_called_once()
            call_args = mock_cursor.execute.call_args[0][0]
            assert "`mydb`.`users`" in call_args
            assert "LIMIT 10" in call_args

    def test_factory_registration(self):
        """Test MySQL connector is registered with factory."""
        from pycaroline.connectors.mysql import MySQLConnector  # noqa: F401

        assert ConnectorFactory.is_registered(DatabaseType.MYSQL)

    def test_context_manager(self):
        """Test context manager protocol."""
        from pycaroline.connectors.mysql import MySQLConnector

        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True

        mock_mysql_connector = MagicMock()
        mock_mysql_connector.connect.return_value = mock_connection

        mock_mysql = MagicMock()
        mock_mysql.connector = mock_mysql_connector
        mock_mysql.connector.Error = Exception

        with patch.dict(
            sys.modules, {"mysql": mock_mysql, "mysql.connector": mock_mysql_connector}
        ):
            with MySQLConnector(host="localhost", user="user", password="pass") as conn:
                assert conn.has_open_connection()

            mock_connection.close.assert_called_once()
