"""S3 storage connector for reading data from AWS S3.

This module provides a connector for reading Parquet, CSV, and JSON files
from AWS S3 buckets.
"""

import os
from typing import Any

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, StorageType


@ConnectorFactory.register_storage(StorageType.S3)
class S3Connector(BaseConnector):
    """Connector for reading data from AWS S3.

    This connector supports reading Parquet, CSV, and JSON files from S3 buckets.
    Authentication can be configured via environment variables or explicit parameters.

    Environment Variables:
        AWS_ACCESS_KEY_ID: AWS access key ID
        AWS_SECRET_ACCESS_KEY: AWS secret access key
        AWS_DEFAULT_REGION: AWS region (default: us-east-1)

    Example:
        with S3Connector(bucket="my-bucket") as conn:
            df = conn.query("data/customers.parquet")

        # Or with explicit credentials
        conn = S3Connector(
            bucket="my-bucket",
            aws_access_key_id="AKIA...",
            aws_secret_access_key="...",
            aws_region="us-west-2"
        )
    """

    def __init__(
        self,
        bucket: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_region: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize S3 connector.

        Args:
            bucket: The S3 bucket name.
            aws_access_key_id: AWS access key ID. Falls back to AWS_ACCESS_KEY_ID env var.
            aws_secret_access_key: AWS secret access key. Falls back to AWS_SECRET_ACCESS_KEY env var.
            aws_region: AWS region. Falls back to AWS_DEFAULT_REGION env var or us-east-1.
            **kwargs: Additional arguments (ignored).
        """
        self.bucket = bucket
        self.aws_access_key_id = aws_access_key_id or os.environ.get(
            "AWS_ACCESS_KEY_ID"
        )
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.aws_region = aws_region or os.environ.get(
            "AWS_DEFAULT_REGION", "us-east-1"
        )
        self._client: Any = None

    def connect(self) -> None:
        """Initialize S3 client.

        Raises:
            ConnectionError: If S3 client cannot be initialized.
        """
        try:
            import boto3
            from botocore.exceptions import BotoCoreError, ClientError

            self._client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region,
            )
            # Verify connection by checking bucket access
            self._client.head_bucket(Bucket=self.bucket)
        except ImportError as e:
            raise ConnectionError(
                "boto3 is required for S3 connector. "
                "Install with: pip install pycaroline[s3]"
            ) from e
        except (BotoCoreError, ClientError) as e:
            raise ConnectionError(
                f"Failed to connect to S3 bucket '{self.bucket}': {e}"
            ) from e

    def disconnect(self) -> None:
        """Close S3 client."""
        self._client = None

    def has_open_connection(self) -> bool:
        """Check if S3 client is initialized.

        Returns:
            True if client is initialized, False otherwise.
        """
        return self._client is not None

    def query(self, path: str) -> pl.DataFrame:
        """Read file from S3 and return as DataFrame.

        Args:
            path: The file path within the bucket (e.g., "data/customers.parquet").

        Returns:
            Polars DataFrame containing the file data.

        Raises:
            QueryError: If the file cannot be read or format is unsupported.
        """
        if not self.has_open_connection():
            raise QueryError("Not connected to S3. Call connect() first.")

        s3_path = f"s3://{self.bucket}/{path}"

        try:
            if path.endswith(".parquet"):
                return pl.read_parquet(s3_path)
            elif path.endswith(".csv"):
                return pl.read_csv(s3_path)
            elif path.endswith(".json"):
                return pl.read_json(s3_path)
            else:
                raise QueryError(
                    f"Unsupported file format for path: {path}. "
                    "Supported formats: .parquet, .csv, .json"
                )
        except Exception as e:
            if isinstance(e, QueryError):
                raise
            raise QueryError(
                f"Failed to read file from S3: s3://{self.bucket}/{path}\nError: {e}"
            ) from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Read file from S3 with optional row limit.

        For S3 connector, 'table' is the file path within the bucket.
        The 'schema' parameter is ignored for S3.

        Args:
            table: The file path within the bucket.
            schema: Ignored for S3 connector.
            limit: Optional maximum number of rows to return.

        Returns:
            Polars DataFrame containing the file data.
        """
        df = self.query(table)
        if limit is not None and limit > 0:
            df = df.head(limit)
        return df
