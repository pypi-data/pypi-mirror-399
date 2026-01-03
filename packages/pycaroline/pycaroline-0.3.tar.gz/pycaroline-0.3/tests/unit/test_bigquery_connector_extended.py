"""Extended unit tests for BigQueryConnector to improve coverage.

Tests for execute method, error handling, and edge cases.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestBigQueryConnectorExecute:
    """Tests for BigQueryConnector execute method."""

    def test_execute_runs_statement(self):
        """Test that execute runs SQL statement."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_query_job = MagicMock()
                mock_client.query.return_value = mock_query_job
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project")
                connector.connect()
                connector.execute("CREATE TABLE test.table (id INT64)")

                mock_client.query.assert_called_once()
                mock_query_job.result.assert_called_once()

    def test_execute_not_connected_raises_error(self):
        """Test that execute raises error when not connected."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            from pycaroline.connectors.base import QueryError
            from pycaroline.connectors.bigquery import BigQueryConnector

            connector = BigQueryConnector(project="test_project")

            with pytest.raises(QueryError) as exc_info:
                connector.execute("CREATE TABLE test (id INT64)")

            assert "Not connected" in str(exc_info.value)

    def test_execute_raises_on_api_error(self):
        """Test that execute raises QueryError on API error."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.base import QueryError
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_client.query.side_effect = Exception("API Error")
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project")
                connector.connect()

                with pytest.raises(QueryError) as exc_info:
                    connector.execute("INVALID SQL")

                assert "Statement failed" in str(exc_info.value)


class TestBigQueryConnectorGetTable:
    """Tests for BigQueryConnector get_table method."""

    def test_get_table_with_default_dataset(self):
        """Test get_table uses default dataset when set."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                import pandas as pd

                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_query_job = MagicMock()
                mock_query_job.to_dataframe.return_value = pd.DataFrame({"id": [1, 2]})
                mock_client.query.return_value = mock_query_job
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(
                    project="test_project", dataset="default_dataset"
                )
                connector.connect()
                connector.get_table("users")

                # Should use default dataset
                call_args = mock_client.query.call_args[0][0]
                assert "default_dataset" in call_args

    def test_get_table_with_schema_override(self):
        """Test get_table uses schema parameter over default dataset."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                import pandas as pd

                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_query_job = MagicMock()
                mock_query_job.to_dataframe.return_value = pd.DataFrame({"id": [1, 2]})
                mock_client.query.return_value = mock_query_job
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(
                    project="test_project", dataset="default_dataset"
                )
                connector.connect()
                connector.get_table("users", schema="override_dataset")

                call_args = mock_client.query.call_args[0][0]
                assert "override_dataset" in call_args

    def test_get_table_without_dataset(self):
        """Test get_table without any dataset."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                import pandas as pd

                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_query_job = MagicMock()
                mock_query_job.to_dataframe.return_value = pd.DataFrame({"id": [1, 2]})
                mock_client.query.return_value = mock_query_job
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project")
                connector.connect()
                connector.get_table("users")

                call_args = mock_client.query.call_args[0][0]
                assert "`users`" in call_args


class TestBigQueryConnectorConnect:
    """Tests for BigQueryConnector connect method."""

    def test_connect_with_credentials_file_not_found(self):
        """Test connect raises error when credentials file not found."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            from pycaroline.connectors.base import ConnectionError
            from pycaroline.connectors.bigquery import BigQueryConnector

            connector = BigQueryConnector(
                project="test_project",
                credentials_path="/nonexistent/path/creds.json",
            )

            with pytest.raises(ConnectionError) as exc_info:
                connector.connect()

            assert "Credentials file not found" in str(exc_info.value)

    def test_connect_with_location(self):
        """Test connect sets location when specified."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project", location="US")
                connector.connect()

                assert mock_client._location == "US"


class TestBigQueryConnectorDisconnect:
    """Tests for BigQueryConnector disconnect method."""

    def test_disconnect_when_not_connected(self):
        """Test disconnect is safe when not connected."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            from pycaroline.connectors.bigquery import BigQueryConnector

            connector = BigQueryConnector(project="test_project")

            # Should not raise
            connector.disconnect()
            assert connector._connection is None

    def test_disconnect_closes_client(self):
        """Test disconnect closes the client."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project")
                connector.connect()
                connector.disconnect()

                mock_client.close.assert_called_once()
                assert connector._connection is None


class TestBigQueryConnectorQuery:
    """Tests for BigQueryConnector query method."""

    def test_query_not_connected_raises_error(self):
        """Test query raises error when not connected."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            from pycaroline.connectors.base import QueryError
            from pycaroline.connectors.bigquery import BigQueryConnector

            connector = BigQueryConnector(project="test_project")

            with pytest.raises(QueryError) as exc_info:
                connector.query("SELECT * FROM test")

            assert "Not connected" in str(exc_info.value)

    def test_query_raises_on_generic_error(self):
        """Test query raises QueryError on generic exception."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.base import QueryError
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_client = MagicMock()
                mock_client.query.side_effect = Exception("Generic error")
                mock_bq.Client.return_value = mock_client

                connector = BigQueryConnector(project="test_project")
                connector.connect()

                with pytest.raises(QueryError) as exc_info:
                    connector.query("SELECT * FROM test")

                assert "Query failed" in str(exc_info.value)
