"""Unit tests for database connectors."""

import os
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError


class MockConnector(BaseConnector):
    """Mock connector for testing base class functionality."""

    def __init__(self):
        self._connection = None

    def connect(self):
        self._connection = MagicMock()

    def disconnect(self):
        self._connection = None

    def query(self, sql):
        return pl.DataFrame({"col": [1, 2, 3]})


class TestBaseConnector:
    """Tests for BaseConnector abstract class."""

    def test_context_manager_connects_and_disconnects(self):
        """Test that context manager properly connects and disconnects."""
        connector = MockConnector()

        with connector as conn:
            assert conn._connection is not None

        assert connector._connection is None

    def test_has_open_connection_false_initially(self):
        """Test has_open_connection returns False before connect."""
        connector = MockConnector()

        assert connector.has_open_connection() is False

    def test_has_open_connection_true_after_connect(self):
        """Test has_open_connection returns True after connect."""
        connector = MockConnector()
        connector.connect()

        assert connector.has_open_connection() is True
        connector.disconnect()

    def test_get_table_builds_correct_sql(self):
        """Test get_table builds correct SQL query."""
        connector = MockConnector()
        connector.connect()

        with patch.object(
            connector, "query", return_value=pl.DataFrame()
        ) as mock_query:
            connector.get_table("users")
            mock_query.assert_called_with("SELECT * FROM users")

    def test_get_table_with_schema(self):
        """Test get_table with schema prefix."""
        connector = MockConnector()
        connector.connect()

        with patch.object(
            connector, "query", return_value=pl.DataFrame()
        ) as mock_query:
            connector.get_table("users", schema="public")
            mock_query.assert_called_with("SELECT * FROM public.users")

    def test_get_table_with_limit(self):
        """Test get_table with row limit."""
        connector = MockConnector()
        connector.connect()

        with patch.object(
            connector, "query", return_value=pl.DataFrame()
        ) as mock_query:
            connector.get_table("users", limit=100)
            mock_query.assert_called_with("SELECT * FROM users LIMIT 100")

    def test_get_table_with_schema_and_limit(self):
        """Test get_table with both schema and limit."""
        connector = MockConnector()
        connector.connect()

        with patch.object(
            connector, "query", return_value=pl.DataFrame()
        ) as mock_query:
            connector.get_table("users", schema="public", limit=50)
            mock_query.assert_called_with("SELECT * FROM public.users LIMIT 50")


class TestSnowflakeConnector:
    """Tests for SnowflakeConnector."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_init_from_env_vars(self):
        """Test initialization from environment variables."""
        with patch.dict(
            os.environ,
            {
                "SNOWFLAKE_ACCOUNT": "test_account",
                "SNOWFLAKE_USER": "test_user",
                "SNOWFLAKE_PASSWORD": "test_pass",
            },
        ):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            connector = SnowflakeConnector()

            assert connector._account == "test_account"
            assert connector._user == "test_user"
            assert connector._password == "test_pass"

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_init_from_direct_params(self):
        """Test initialization from direct parameters."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(
            account="direct_account", user="direct_user", password="direct_pass"
        )

        assert connector._account == "direct_account"
        assert connector._user == "direct_user"

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_connect_raises_without_account(self):
        """Test connect raises error without account."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(user="user", password="pass")

        with pytest.raises(ConnectionError, match="account"):
            connector.connect()

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_connect_raises_without_user(self):
        """Test connect raises error without user."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(account="account", password="pass")

        with pytest.raises(ConnectionError, match="user"):
            connector.connect()

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_connect_raises_without_auth(self):
        """Test connect raises error without authentication method."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(account="account", user="user")

        with pytest.raises(ConnectionError, match="authentication"):
            connector.connect()

    @patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True)
    def test_query_raises_when_not_connected(self):
        """Test query raises error when not connected."""
        from pycaroline.connectors.snowflake import SnowflakeConnector

        connector = SnowflakeConnector(account="a", user="u", password="p")

        with pytest.raises(QueryError, match="Not connected"):
            connector.query("SELECT 1")


class TestBigQueryConnector:
    """Tests for BigQueryConnector."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    def test_init_from_env_vars(self):
        """Test initialization from environment variables."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            from pycaroline.connectors.bigquery import BigQueryConnector

            connector = BigQueryConnector()

            assert connector._project == "test-project"

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    def test_init_from_direct_params(self):
        """Test initialization from direct parameters."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        connector = BigQueryConnector(project="my-project", dataset="my_dataset")

        assert connector._project == "my-project"
        assert connector._dataset == "my_dataset"

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    def test_query_raises_when_not_connected(self):
        """Test query raises error when not connected."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        connector = BigQueryConnector(project="test")

        with pytest.raises(QueryError, match="Not connected"):
            connector.query("SELECT 1")


class TestRedshiftConnector:
    """Tests for RedshiftConnector."""

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    @patch("pycaroline.connectors.redshift.PSYCOPG2_AVAILABLE", False)
    def test_init_from_env_vars(self):
        """Test initialization from environment variables."""
        with patch.dict(
            os.environ,
            {
                "REDSHIFT_HOST": "test-host",
                "REDSHIFT_DATABASE": "test_db",
                "REDSHIFT_USER": "test_user",
                "REDSHIFT_PASSWORD": "test_pass",
            },
        ):
            from pycaroline.connectors.redshift import RedshiftConnector

            connector = RedshiftConnector()

            assert connector._host == "test-host"
            assert connector._database == "test_db"

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    def test_connect_raises_without_host(self):
        """Test connect raises error without host."""
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(database="db", user="u", password="p")

        with pytest.raises(ConnectionError, match="host"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    def test_connect_raises_without_database(self):
        """Test connect raises error without database."""
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(host="host", user="u", password="p")

        with pytest.raises(ConnectionError, match="database"):
            connector.connect()

    @patch("pycaroline.connectors.redshift.REDSHIFT_CONNECTOR_AVAILABLE", True)
    def test_query_raises_when_not_connected(self):
        """Test query raises error when not connected."""
        from pycaroline.connectors.redshift import RedshiftConnector

        connector = RedshiftConnector(host="h", database="d", user="u", password="p")

        with pytest.raises(QueryError, match="Not connected"):
            connector.query("SELECT 1")


class TestConnectionError:
    """Tests for ConnectionError exception."""

    def test_connection_error_message(self):
        """Test ConnectionError stores message correctly."""
        error = ConnectionError("Test error message")
        assert str(error) == "Test error message"


class TestQueryError:
    """Tests for QueryError exception."""

    def test_query_error_message(self):
        """Test QueryError stores message correctly."""
        error = QueryError("Query failed")
        assert str(error) == "Query failed"
