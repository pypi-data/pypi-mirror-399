"""Unit tests for S3 storage connector."""

import sys
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from pycaroline.connectors.base import ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, StorageType


class TestS3Connector:
    """Tests for S3Connector class."""

    def test_init_with_explicit_credentials(self):
        """Test initialization with explicit credentials."""
        from pycaroline.connectors.s3 import S3Connector

        conn = S3Connector(
            bucket="test-bucket",
            aws_access_key_id="AKIATEST",
            aws_secret_access_key="secret123",
            aws_region="us-west-2",
        )

        assert conn.bucket == "test-bucket"
        assert conn.aws_access_key_id == "AKIATEST"
        assert conn.aws_secret_access_key == "secret123"
        assert conn.aws_region == "us-west-2"

    def test_init_with_env_vars(self, monkeypatch):
        """Test initialization with environment variables."""
        from pycaroline.connectors.s3 import S3Connector

        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAENV")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "envsecret")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")

        conn = S3Connector(bucket="test-bucket")

        assert conn.aws_access_key_id == "AKIAENV"
        assert conn.aws_secret_access_key == "envsecret"
        assert conn.aws_region == "eu-west-1"

    def test_init_default_region(self):
        """Test default region when not specified."""
        from pycaroline.connectors.s3 import S3Connector

        conn = S3Connector(bucket="test-bucket")
        assert conn.aws_region == "us-east-1"

    def test_connect_success(self):
        """Test successful connection."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()

            assert conn.has_open_connection()
            mock_boto3.client.assert_called_once()
            mock_client.head_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_connect_failure(self):
        """Test connection failure."""
        from botocore.exceptions import ClientError

        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "403", "Message": "Forbidden"}}, "HeadBucket"
        )
        mock_boto3.client.return_value = mock_client

        with patch.dict(sys.modules, {"boto3": mock_boto3}):
            conn = S3Connector(bucket="test-bucket")

            with pytest.raises(ConnectionError) as exc_info:
                conn.connect()

            assert "test-bucket" in str(exc_info.value)

    def test_disconnect(self):
        """Test disconnection."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()
            assert conn.has_open_connection()

            conn.disconnect()
            assert not conn.has_open_connection()

    def test_query_not_connected(self):
        """Test query when not connected."""
        from pycaroline.connectors.s3 import S3Connector

        conn = S3Connector(bucket="test-bucket")

        with pytest.raises(QueryError) as exc_info:
            conn.query("data/test.parquet")

        assert "Not connected" in str(exc_info.value)

    @patch("polars.read_parquet")
    def test_query_parquet(self, mock_read_parquet):
        """Test reading parquet file."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_df = pl.DataFrame({"id": [1, 2, 3]})
        mock_read_parquet.return_value = mock_df

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()
            result = conn.query("data/test.parquet")

            mock_read_parquet.assert_called_once_with(
                "s3://test-bucket/data/test.parquet"
            )
            assert result.equals(mock_df)

    @patch("polars.read_csv")
    def test_query_csv(self, mock_read_csv):
        """Test reading CSV file."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_df = pl.DataFrame({"id": [1, 2, 3]})
        mock_read_csv.return_value = mock_df

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()
            result = conn.query("data/test.csv")

            mock_read_csv.assert_called_once_with("s3://test-bucket/data/test.csv")
            assert result.equals(mock_df)

    @patch("polars.read_json")
    def test_query_json(self, mock_read_json):
        """Test reading JSON file."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_df = pl.DataFrame({"id": [1, 2, 3]})
        mock_read_json.return_value = mock_df

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()
            result = conn.query("data/test.json")

            mock_read_json.assert_called_once_with("s3://test-bucket/data/test.json")
            assert result.equals(mock_df)

    def test_query_unsupported_format(self):
        """Test reading unsupported file format."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()

            with pytest.raises(QueryError) as exc_info:
                conn.query("data/test.txt")

            assert "Unsupported file format" in str(exc_info.value)

    @patch("polars.read_parquet")
    def test_get_table_with_limit(self, mock_read_parquet):
        """Test get_table with row limit."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_df = pl.DataFrame({"id": [1, 2, 3, 4, 5]})
        mock_read_parquet.return_value = mock_df

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            conn = S3Connector(bucket="test-bucket")
            conn.connect()
            result = conn.get_table("data/test.parquet", limit=2)

            assert len(result) == 2

    def test_factory_registration(self):
        """Test S3 connector is registered with factory."""
        # Import to trigger registration
        from pycaroline.connectors.s3 import S3Connector  # noqa: F401

        assert ConnectorFactory.is_registered(StorageType.S3)

    def test_context_manager(self):
        """Test context manager protocol."""
        from pycaroline.connectors.s3 import S3Connector

        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        with patch.dict(
            sys.modules, {"boto3": mock_boto3, "botocore.exceptions": MagicMock()}
        ):
            with S3Connector(bucket="test-bucket") as conn:
                assert conn.has_open_connection()

            assert not conn.has_open_connection()
