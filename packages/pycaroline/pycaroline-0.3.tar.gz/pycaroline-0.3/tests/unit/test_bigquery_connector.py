"""Unit tests for BigQueryConnector with mocked dependencies."""

from unittest.mock import MagicMock, patch

import polars as pl
import pytest


class TestBigQueryConnectorConnect:
    """Tests for BigQueryConnector.connect method."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_connect_with_adc(self, mock_bq):
        """Test connecting with Application Default Credentials."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()

        assert connector._connection == mock_client
        mock_bq.Client.assert_called_once_with(project="test-project")

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    @patch("os.path.exists", return_value=True)
    def test_connect_with_service_account(self, mock_exists, mock_bq):
        """Test connecting with service account credentials."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_bq.Client.from_service_account_json.return_value = mock_client

        connector = BigQueryConnector(
            project="test-project", credentials_path="/path/to/creds.json"
        )
        connector.connect()

        assert connector._connection == mock_client
        mock_bq.Client.from_service_account_json.assert_called_once()

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    @patch("os.path.exists", return_value=False)
    def test_connect_raises_for_missing_credentials(self, mock_exists, mock_bq):
        """Test connect raises error for missing credentials file."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.bigquery import BigQueryConnector

        connector = BigQueryConnector(
            project="test-project", credentials_path="/nonexistent/creds.json"
        )

        with pytest.raises(ConnectionError, match="not found"):
            connector.connect()

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_connect_with_location(self, mock_bq):
        """Test connecting with location specified."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project", location="US")
        connector.connect()

        assert mock_client._location == "US"


class TestBigQueryConnectorDisconnect:
    """Tests for BigQueryConnector.disconnect method."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_disconnect_closes_client(self, mock_bq):
        """Test disconnect closes the client."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()
        connector.disconnect()

        mock_client.close.assert_called_once()
        assert connector._connection is None


class TestBigQueryConnectorQuery:
    """Tests for BigQueryConnector.query method."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_query_returns_dataframe(self, mock_bq):
        """Test query returns a polars DataFrame."""
        import pandas as pd

        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        # BigQuery returns pandas internally, connector converts to polars
        mock_job.to_dataframe.return_value = pd.DataFrame({"col": [1, 2]})
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()
        result = connector.query("SELECT * FROM test")

        assert isinstance(result, pl.DataFrame)
        mock_client.query.assert_called_with("SELECT * FROM test")


class TestBigQueryConnectorExecute:
    """Tests for BigQueryConnector.execute method."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_execute_waits_for_completion(self, mock_bq):
        """Test execute waits for query completion."""
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()
        connector.execute("CREATE TABLE test (id INT64)")

        mock_job.result.assert_called_once()


class TestBigQueryConnectorGetTable:
    """Tests for BigQueryConnector.get_table method."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_get_table_with_schema(self, mock_bq):
        """Test get_table with schema (dataset) specified."""
        import pandas as pd

        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.to_dataframe.return_value = pd.DataFrame({"col": [1]})
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()
        connector.get_table("users", schema="my_dataset")

        call_args = mock_client.query.call_args[0][0]
        assert "`my_dataset.users`" in call_args

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_get_table_with_default_dataset(self, mock_bq):
        """Test get_table uses default dataset."""
        import pandas as pd

        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.to_dataframe.return_value = pd.DataFrame({"col": [1]})
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project", dataset="default_ds")
        connector.connect()
        connector.get_table("users")

        call_args = mock_client.query.call_args[0][0]
        assert "`default_ds.users`" in call_args

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_get_table_with_limit(self, mock_bq):
        """Test get_table with row limit."""
        import pandas as pd

        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.to_dataframe.return_value = pd.DataFrame({"col": [1]})
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project", dataset="ds")
        connector.connect()
        connector.get_table("users", limit=100)

        call_args = mock_client.query.call_args[0][0]
        assert "LIMIT 100" in call_args


class TestBigQueryConnectorErrors:
    """Tests for error handling."""

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_query_raises_on_api_error(self, mock_bq):
        """Test query raises QueryError on API error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("API error")
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()

        with pytest.raises(QueryError):
            connector.query("SELECT * FROM nonexistent")

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_execute_raises_on_api_error(self, mock_bq):
        """Test execute raises QueryError on API error."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.result.side_effect = Exception("API error")
        mock_client.query.return_value = mock_job
        mock_bq.Client.return_value = mock_client

        connector = BigQueryConnector(project="test-project")
        connector.connect()

        with pytest.raises(QueryError):
            connector.execute("CREATE TABLE test")

    @patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True)
    @patch("pycaroline.connectors.bigquery.bigquery")
    def test_connect_raises_on_general_error(self, mock_bq):
        """Test connect raises ConnectionError on general error."""
        from pycaroline.connectors.base import ConnectionError
        from pycaroline.connectors.bigquery import BigQueryConnector

        mock_bq.Client.side_effect = Exception("Connection failed")

        connector = BigQueryConnector(project="test-project")

        with pytest.raises(ConnectionError):
            connector.connect()
