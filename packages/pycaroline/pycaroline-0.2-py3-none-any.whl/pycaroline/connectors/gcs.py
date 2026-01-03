"""GCS storage connector for reading data from Google Cloud Storage.

This module provides a connector for reading Parquet, CSV, and JSON files
from Google Cloud Storage buckets.
"""

import os
from typing import Any

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, StorageType


@ConnectorFactory.register_storage(StorageType.GCS)
class GCSConnector(BaseConnector):
    """Connector for reading data from Google Cloud Storage.

    This connector supports reading Parquet, CSV, and JSON files from GCS buckets.
    Authentication can be configured via environment variables or explicit parameters.

    Environment Variables:
        GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON file
        GCP_PROJECT: Google Cloud project ID

    Example:
        with GCSConnector(bucket="my-bucket") as conn:
            df = conn.query("data/customers.parquet")

        # Or with explicit credentials
        conn = GCSConnector(
            bucket="my-bucket",
            credentials_path="/path/to/service-account.json",
            project="my-project"
        )
    """

    def __init__(
        self,
        bucket: str,
        credentials_path: str | None = None,
        project: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize GCS connector.

        Args:
            bucket: The GCS bucket name.
            credentials_path: Path to service account JSON. Falls back to
                GOOGLE_APPLICATION_CREDENTIALS env var.
            project: Google Cloud project ID. Falls back to GCP_PROJECT env var.
            **kwargs: Additional arguments (ignored).
        """
        self.bucket = bucket
        self.credentials_path = credentials_path or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.project = project or os.environ.get("GCP_PROJECT")
        self._client: Any = None

    def connect(self) -> None:
        """Initialize GCS client.

        Raises:
            ConnectionError: If GCS client cannot be initialized.
        """
        try:
            from google.cloud import storage
            from google.cloud.exceptions import GoogleCloudError

            self._client = storage.Client(project=self.project)
            # Verify connection by checking bucket access
            bucket = self._client.bucket(self.bucket)
            bucket.reload()
        except ImportError as e:
            raise ConnectionError(
                "google-cloud-storage is required for GCS connector. "
                "Install with: pip install pycaroline[gcs]"
            ) from e
        except GoogleCloudError as e:
            raise ConnectionError(
                f"Failed to connect to GCS bucket '{self.bucket}': {e}"
            ) from e

    def disconnect(self) -> None:
        """Close GCS client."""
        self._client = None

    def has_open_connection(self) -> bool:
        """Check if GCS client is initialized.

        Returns:
            True if client is initialized, False otherwise.
        """
        return self._client is not None

    def query(self, path: str) -> pl.DataFrame:
        """Read file from GCS and return as DataFrame.

        Args:
            path: The file path within the bucket (e.g., "data/customers.parquet").

        Returns:
            Polars DataFrame containing the file data.

        Raises:
            QueryError: If the file cannot be read or format is unsupported.
        """
        if not self.has_open_connection():
            raise QueryError("Not connected to GCS. Call connect() first.")

        gcs_path = f"gs://{self.bucket}/{path}"

        try:
            if path.endswith(".parquet"):
                return pl.read_parquet(gcs_path)
            elif path.endswith(".csv"):
                return pl.read_csv(gcs_path)
            elif path.endswith(".json"):
                return pl.read_json(gcs_path)
            else:
                raise QueryError(
                    f"Unsupported file format for path: {path}. "
                    "Supported formats: .parquet, .csv, .json"
                )
        except Exception as e:
            if isinstance(e, QueryError):
                raise
            raise QueryError(
                f"Failed to read file from GCS: gs://{self.bucket}/{path}\nError: {e}"
            ) from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Read file from GCS with optional row limit.

        For GCS connector, 'table' is the file path within the bucket.
        The 'schema' parameter is ignored for GCS.

        Args:
            table: The file path within the bucket.
            schema: Ignored for GCS connector.
            limit: Optional maximum number of rows to return.

        Returns:
            Polars DataFrame containing the file data.
        """
        df = self.query(table)
        if limit is not None and limit > 0:
            df = df.head(limit)
        return df
