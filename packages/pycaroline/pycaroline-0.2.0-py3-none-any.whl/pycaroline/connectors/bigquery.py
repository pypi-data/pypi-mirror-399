"""BigQuery database connector.

This module provides a connector for Google BigQuery that extends BaseConnector.
"""

import os

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType

try:
    from google.api_core.exceptions import GoogleAPIError
    from google.cloud import bigquery

    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False


@ConnectorFactory.register(DatabaseType.BIGQUERY)
class BigQueryConnector(BaseConnector):
    """BigQuery database connector.

    Supports authentication via:
    - Service account JSON file (credentials_path parameter or GOOGLE_APPLICATION_CREDENTIALS env var)
    - Application Default Credentials (ADC) when no credentials are specified

    Example:
        # Using environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/service-account.json"
        with BigQueryConnector(project="my-project") as conn:
            df = conn.query("SELECT * FROM `my-project.dataset.table`")

        # Using direct credentials path
        connector = BigQueryConnector(
            project="my-project",
            credentials_path="/path/to/service-account.json"
        )

        # Using Application Default Credentials
        connector = BigQueryConnector(project="my-project")
    """

    def __init__(
        self,
        project: str | None = None,
        credentials_path: str | None = None,
        location: str | None = None,
        dataset: str | None = None,
    ):
        """Initialize the BigQuery connector.

        Args:
            project: Google Cloud project ID. If not provided, uses GOOGLE_CLOUD_PROJECT
                    environment variable or the project from credentials.
            credentials_path: Path to service account JSON file. If not provided,
                            uses GOOGLE_APPLICATION_CREDENTIALS environment variable
                            or Application Default Credentials.
            location: Default location for queries (e.g., "US", "EU").
            dataset: Default dataset for unqualified table references.
        """
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "google-cloud-bigquery is required for BigQueryConnector. "
                "Install it with: pip install data-recon[bigquery]"
            )

        self._connection = None
        self._project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self._credentials_path = credentials_path or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self._location = location or os.environ.get("BIGQUERY_LOCATION")
        self._dataset = dataset or os.environ.get("BIGQUERY_DATASET")

    def connect(self) -> None:
        """Establish connection to BigQuery.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        try:
            if self._credentials_path:
                # Use service account credentials
                expanded_path = os.path.expanduser(self._credentials_path)
                if not os.path.exists(expanded_path):
                    raise ConnectionError(
                        f"Credentials file not found: {expanded_path}"
                    )
                self._connection = bigquery.Client.from_service_account_json(
                    expanded_path,
                    project=self._project,
                )
            else:
                # Use Application Default Credentials
                self._connection = bigquery.Client(project=self._project)

            # Set location if specified
            if self._location and self._connection is not None:
                self._connection._location = self._location  # type: ignore[attr-defined]

        except GoogleAPIError as e:
            raise ConnectionError(
                f"Failed to connect to BigQuery project '{self._project}': {e}"
            ) from e
        except Exception as e:
            raise ConnectionError(f"Failed to connect to BigQuery: {e}") from e

    def disconnect(self) -> None:
        """Close the BigQuery connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL query and return results as Polars DataFrame.

        Args:
            sql: The SQL query to execute.

        Returns:
            Polars DataFrame containing the query results.

        Raises:
            QueryError: If the query fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Query: {sql}")

        try:
            query_job = self._connection.query(sql)
            # Convert to pandas first, then to polars
            pandas_df = query_job.to_dataframe()
            return pl.from_pandas(pandas_df)
        except GoogleAPIError as e:
            raise QueryError(f"Query failed: {sql}\nError: {e}") from e
        except Exception as e:
            raise QueryError(f"Query failed: {sql}\nError: {e}") from e

    def execute(self, sql: str) -> None:
        """Execute SQL statement (DDL/DML).

        Args:
            sql: The SQL statement to execute.

        Raises:
            QueryError: If the statement fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Statement: {sql}")

        try:
            query_job = self._connection.query(sql)
            query_job.result()  # Wait for completion
        except GoogleAPIError as e:
            raise QueryError(f"Statement failed: {sql}\nError: {e}") from e
        except Exception as e:
            raise QueryError(f"Statement failed: {sql}\nError: {e}") from e

    def get_table(
        self,
        table: str,
        schema: str | None = None,
        limit: int | None = None,
    ) -> pl.DataFrame:
        """Retrieve data from a table.

        For BigQuery, the schema parameter is interpreted as the dataset name.
        Table references can be:
        - Fully qualified: `project.dataset.table`
        - Dataset qualified: `dataset.table`
        - Unqualified: `table` (uses default dataset if set)

        Args:
            table: The table name to query.
            schema: Optional dataset name. If provided, queries `dataset.table`.
            limit: Optional maximum number of rows to return.

        Returns:
            Polars DataFrame containing the table data.

        Raises:
            QueryError: If the query fails to execute.
        """
        # Build qualified table name
        if schema:
            qualified_name = f"`{schema}.{table}`"
        elif self._dataset:
            qualified_name = f"`{self._dataset}.{table}`"
        else:
            qualified_name = f"`{table}`"

        sql = f"SELECT * FROM {qualified_name}"  # nosec B608
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"

        return self.query(sql)
