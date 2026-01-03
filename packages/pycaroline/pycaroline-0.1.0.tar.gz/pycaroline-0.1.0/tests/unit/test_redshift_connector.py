"""Unit tests for RedshiftConnector with mocked dependencies."""

from unittest.mock import MagicMock, patch

import polars as pl
import pytest


class TestRedshiftConnectorConnect:
    """Tests for RedshiftConnector.connect method."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", False)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_connect_with_redshift_connector(self, mock_rc):
        """Test connecting with redshift_connector library."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="test_user", password="test_pass"
        )
        connector.connect()

        assert connector._connection == mock_conn
        mock_rc.connect.assert_called_once()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", False)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.psycopg2")
    def test_connect_with_psycopg2(self, mock_pg):
        """Test connecting with psycopg2 library."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="test_user", password="test_pass"
        )
        connector.connect()

        assert connector._connection == mock_conn

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_connect_with_iam(self, mock_rc):
        """Test connecting with IAM authentication."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host",
            database="test_db",
            iam=True,
            cluster_identifier="my-cluster",
            region="us-east-1",
        )
        connector.connect()

        call_kwargs = mock_rc.connect.call_args[1]
        assert call_kwargs["iam"] is True
        assert call_kwargs["cluster_identifier"] == "my-cluster"

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_connect_iam_requires_cluster_identifier(self, mock_rc):
        """Test IAM auth requires cluster_identifier."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(host="test-host", database="test_db", iam=True)

        with pytest.raises(ConnectionError, match="cluster_identifier"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_connect_requires_user_without_iam(self, mock_rc):
        """Test non-IAM auth requires user."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(
            host="test-host", database="test_db", password="pass"
        )

        with pytest.raises(ConnectionError, match="user"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_connect_requires_password_without_iam(self, mock_rc):
        """Test non-IAM auth requires password."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(host="test-host", database="test_db", user="user")

        with pytest.raises(ConnectionError, match="password"):
            connector.connect()


class TestRedshiftConnectorDisconnect:
    """Tests for RedshiftConnector.disconnect method."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_disconnect_closes_connection(self, mock_rc):
        """Test disconnect closes the connection."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()
        connector.disconnect()

        mock_conn.close.assert_called_once()
        assert connector._connection is None


class TestRedshiftConnectorQuery:
    """Tests for RedshiftConnector.query method."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_query_returns_dataframe(self, mock_rc):
        """Test query returns a polars DataFrame."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("col",)]
        mock_cursor.fetchall.return_value = [(1,), (2,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()
        result = connector.query("SELECT * FROM test")

        assert isinstance(result, pl.DataFrame)
        mock_cursor.execute.assert_called_with("SELECT * FROM test")


class TestRedshiftConnectorExecute:
    """Tests for RedshiftConnector.execute method."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_execute_commits_transaction(self, mock_rc):
        """Test execute commits the transaction."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()
        connector.execute("CREATE TABLE test (id INT)")

        mock_cursor.execute.assert_called_with("CREATE TABLE test (id INT)")
        mock_conn.commit.assert_called_once()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_execute_rollback_on_error(self, mock_rc):
        """Test execute rolls back on error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()

        with pytest.raises(QueryError):
            connector.execute("INVALID SQL")

        mock_conn.rollback.assert_called_once()


class TestRedshiftConnectorGetTable:
    """Tests for RedshiftConnector.get_table method."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_get_table_with_schema(self, mock_rc):
        """Test get_table with schema specified."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("col",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()
        connector.get_table("users", schema="public")

        call_args = mock_cursor.execute.call_args[0][0]
        assert "public.users" in call_args

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_get_table_with_default_schema(self, mock_rc):
        """Test get_table uses default schema."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("col",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host",
            database="test_db",
            user="user",
            password="pass",
            schema="default_schema",
        )
        connector.connect()
        connector.get_table("users")

        call_args = mock_cursor.execute.call_args[0][0]
        assert "default_schema.users" in call_args

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_get_table_with_limit(self, mock_rc):
        """Test get_table with row limit."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("col",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()
        connector.get_table("users", limit=50)

        call_args = mock_cursor.execute.call_args[0][0]
        assert "LIMIT 50" in call_args


class TestRedshiftConnectorPsycopg2:
    """Tests for psycopg2 fallback."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", False)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.psycopg2")
    def test_connect_requires_user_with_psycopg2(self, mock_pg):
        """Test psycopg2 connection requires user."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(
            host="test-host", database="test_db", password="pass"
        )

        with pytest.raises(ConnectionError, match="user"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", False)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.psycopg2")
    def test_connect_requires_password_with_psycopg2(self, mock_pg):
        """Test psycopg2 connection requires password."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(host="test-host", database="test_db", user="user")

        with pytest.raises(ConnectionError, match="password"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", False)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.psycopg2")
    def test_connect_with_ssl_mode(self, mock_pg):
        """Test psycopg2 connection with SSL mode."""
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host",
            database="test_db",
            user="user",
            password="pass",
            ssl=True,
            ssl_mode="verify-full",
        )
        connector.connect()

        call_kwargs = mock_pg.connect.call_args[1]
        assert call_kwargs["sslmode"] == "verify-full"


class TestRedshiftConnectorQueryErrors:
    """Tests for query error handling."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.redshift_connector")
    def test_query_raises_on_error(self, mock_rc):
        """Test query raises QueryError on database error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.redshift import RedshiftConnector

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_rc.connect.return_value = mock_conn

        connector = RedshiftConnector(
            host="test-host", database="test_db", user="user", password="pass"
        )
        connector.connect()

        with pytest.raises(QueryError):
            connector.query("SELECT * FROM nonexistent")
