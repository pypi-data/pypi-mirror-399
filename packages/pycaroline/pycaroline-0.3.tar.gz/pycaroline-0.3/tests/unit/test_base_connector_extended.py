"""Extended unit tests for BaseConnector to improve coverage.

Tests for context manager, has_open_connection, and get_table methods.
"""

import polars as pl
import pytest

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError


class ConcreteConnector(BaseConnector):
    """Concrete implementation of BaseConnector for testing."""

    def __init__(self, should_fail_connect=False, should_fail_query=False):
        self._connection = None
        self.should_fail_connect = should_fail_connect
        self.should_fail_query = should_fail_query
        self.connect_called = False
        self.disconnect_called = False

    def connect(self):
        self.connect_called = True
        if self.should_fail_connect:
            raise ConnectionError("Connection failed")
        self._connection = "mock_connection"

    def disconnect(self):
        self.disconnect_called = True
        self._connection = None

    def query(self, sql):
        if self.should_fail_query:
            raise QueryError(f"Query failed: {sql}")
        return pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})


class TestBaseConnectorContextManager:
    """Tests for context manager protocol."""

    def test_context_manager_connects_on_enter(self):
        """Test that __enter__ calls connect."""
        connector = ConcreteConnector()

        with connector:
            assert connector.connect_called
            assert connector._connection is not None

    def test_context_manager_disconnects_on_exit(self):
        """Test that __exit__ calls disconnect."""
        connector = ConcreteConnector()

        with connector:
            pass

        assert connector.disconnect_called
        assert connector._connection is None

    def test_context_manager_disconnects_on_exception(self):
        """Test that __exit__ disconnects even when exception occurs."""
        connector = ConcreteConnector()

        with pytest.raises(ValueError):
            with connector:
                raise ValueError("Test error")

        assert connector.disconnect_called
        assert connector._connection is None

    def test_context_manager_returns_self(self):
        """Test that __enter__ returns the connector instance."""
        connector = ConcreteConnector()

        with connector as conn:
            assert conn is connector


class TestBaseConnectorHasOpenConnection:
    """Tests for has_open_connection method."""

    def test_has_open_connection_returns_false_initially(self):
        """Test that has_open_connection returns False before connect."""
        connector = ConcreteConnector()
        assert connector.has_open_connection() is False

    def test_has_open_connection_returns_true_after_connect(self):
        """Test that has_open_connection returns True after connect."""
        connector = ConcreteConnector()
        connector.connect()

        assert connector.has_open_connection() is True

    def test_has_open_connection_returns_false_after_disconnect(self):
        """Test that has_open_connection returns False after disconnect."""
        connector = ConcreteConnector()
        connector.connect()
        connector.disconnect()

        assert connector.has_open_connection() is False


class TestBaseConnectorGetTable:
    """Tests for get_table method."""

    def test_get_table_without_schema(self):
        """Test get_table without schema parameter."""
        connector = ConcreteConnector()
        connector.connect()

        # Mock the query method to capture the SQL
        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users")

        assert len(captured_sql) == 1
        assert "SELECT * FROM users" in captured_sql[0]

    def test_get_table_with_schema(self):
        """Test get_table with schema parameter."""
        connector = ConcreteConnector()
        connector.connect()

        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users", schema="public")

        assert len(captured_sql) == 1
        assert "SELECT * FROM public.users" in captured_sql[0]

    def test_get_table_with_limit(self):
        """Test get_table with limit parameter."""
        connector = ConcreteConnector()
        connector.connect()

        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users", limit=100)

        assert len(captured_sql) == 1
        assert "LIMIT 100" in captured_sql[0]

    def test_get_table_with_schema_and_limit(self):
        """Test get_table with both schema and limit."""
        connector = ConcreteConnector()
        connector.connect()

        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users", schema="prod", limit=50)

        assert len(captured_sql) == 1
        assert "SELECT * FROM prod.users" in captured_sql[0]
        assert "LIMIT 50" in captured_sql[0]

    def test_get_table_with_zero_limit(self):
        """Test get_table with zero limit (should not add LIMIT clause)."""
        connector = ConcreteConnector()
        connector.connect()

        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users", limit=0)

        assert len(captured_sql) == 1
        assert "LIMIT" not in captured_sql[0]

    def test_get_table_with_negative_limit(self):
        """Test get_table with negative limit (should not add LIMIT clause)."""
        connector = ConcreteConnector()
        connector.connect()

        captured_sql = []
        original_query = connector.query

        def mock_query(sql):
            captured_sql.append(sql)
            return original_query(sql)

        connector.query = mock_query
        connector.get_table("users", limit=-1)

        assert len(captured_sql) == 1
        assert "LIMIT" not in captured_sql[0]


class TestConnectionError:
    """Tests for ConnectionError exception."""

    def test_connection_error_message(self):
        """Test ConnectionError stores message correctly."""
        error = ConnectionError("Failed to connect")
        assert str(error) == "Failed to connect"

    def test_connection_error_inheritance(self):
        """Test ConnectionError inherits from Exception."""
        error = ConnectionError("Test")
        assert isinstance(error, Exception)


class TestQueryError:
    """Tests for QueryError exception."""

    def test_query_error_message(self):
        """Test QueryError stores message correctly."""
        error = QueryError("Query failed: SELECT * FROM table")
        assert "Query failed" in str(error)

    def test_query_error_inheritance(self):
        """Test QueryError inherits from Exception."""
        error = QueryError("Test")
        assert isinstance(error, Exception)
