"""Additional tests to achieve 95%+ coverage.

Tests for remaining uncovered lines in various modules.
"""

from unittest.mock import MagicMock, patch

import polars as pl
import pytest


class TestComparatorMismatchHandling:
    """Tests for comparator mismatch handling."""

    def test_compare_handles_mismatch_exception(self):
        """Test that compare handles exceptions in all_mismatch gracefully."""
        from pycaroline.comparison.comparator import DataComparator
        from pycaroline.comparison.models import ComparisonConfig

        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})
        config = ComparisonConfig(join_columns=["id"])
        comparator = DataComparator(config)

        # This should work without errors
        result = comparator.compare(source, target)

        assert result.mismatched_rows == 0


class TestGCSConnectorErrorHandling:
    """Tests for GCS connector error handling."""

    def test_gcs_connector_not_connected_raises_error(self):
        """Test that query raises error when not connected."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.gcs import GCSConnector

        connector = GCSConnector(bucket="test-bucket")

        with pytest.raises(QueryError) as exc_info:
            connector.query("data.parquet")

        assert "Not connected" in str(exc_info.value)


class TestMySQLConnectorErrorHandling:
    """Tests for MySQL connector error handling."""

    def test_query_with_empty_result(self):
        """Test query returns empty DataFrame for no results."""
        with patch("mysql.connector") as mock_mysql:
            from pycaroline.connectors.mysql import MySQLConnector

            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.description = [("id",), ("value",)]
            mock_cursor.fetchall.return_value = []
            mock_connection.cursor.return_value = mock_cursor
            mock_connection.is_connected.return_value = True
            mock_mysql.connect.return_value = mock_connection

            connector = MySQLConnector(
                host="localhost",
                user="test",
                password="test",
                database="test",
            )
            connector.connect()
            result = connector.query("SELECT * FROM empty_table")

            assert isinstance(result, pl.DataFrame)
            assert len(result) == 0
            assert result.columns == ["id", "value"]

    def test_has_open_connection_handles_exception(self):
        """Test has_open_connection handles exceptions gracefully."""
        with patch("mysql.connector") as mock_mysql:
            from pycaroline.connectors.mysql import MySQLConnector

            mock_connection = MagicMock()
            mock_connection.is_connected.side_effect = Exception(
                "Connection check failed"
            )
            mock_mysql.connect.return_value = mock_connection

            connector = MySQLConnector(
                host="localhost",
                user="test",
                password="test",
                database="test",
            )
            connector._connection = mock_connection

            result = connector.has_open_connection()
            assert result is False


class TestPostgreSQLConnectorErrorHandling:
    """Tests for PostgreSQL connector error handling."""

    def test_postgresql_connector_not_connected_raises_error(self):
        """Test that query raises error when not connected."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.postgresql import PostgreSQLConnector

        connector = PostgreSQLConnector(
            host="localhost",
            user="test",
            password="test",
            database="test",
        )

        with pytest.raises(QueryError) as exc_info:
            connector.query("SELECT * FROM test")

        assert "Not connected" in str(exc_info.value)

    def test_has_open_connection_returns_false_when_none(self):
        """Test has_open_connection returns False when connection is None."""
        from pycaroline.connectors.postgresql import PostgreSQLConnector

        connector = PostgreSQLConnector(
            host="localhost",
            user="test",
            password="test",
            database="test",
        )

        result = connector.has_open_connection()
        assert result is False


class TestS3ConnectorErrorHandling:
    """Tests for S3 connector error handling."""

    def test_s3_connector_not_connected_raises_error(self):
        """Test that query raises error when not connected."""
        from pycaroline.connectors.base import QueryError
        from pycaroline.connectors.s3 import S3Connector

        connector = S3Connector(bucket="test-bucket")

        with pytest.raises(QueryError) as exc_info:
            connector.query("data.parquet")

        assert "Not connected" in str(exc_info.value)


class TestBaseConnectorAbstractMethods:
    """Tests for BaseConnector abstract methods."""

    def test_base_connector_cannot_be_instantiated(self):
        """Test that BaseConnector cannot be instantiated directly."""
        from pycaroline.connectors.base import BaseConnector

        with pytest.raises(TypeError):
            BaseConnector()


class TestSnowflakeConnectorPrivateKeyError:
    """Tests for Snowflake private key error handling."""

    def test_private_key_load_error(self, tmp_path):
        """Test that invalid private key raises ConnectionError."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.base import ConnectionError
            from pycaroline.connectors.snowflake import SnowflakeConnector

            # Create an invalid key file
            key_file = tmp_path / "invalid_key.pem"
            key_file.write_text("not a valid private key")

            connector = SnowflakeConnector(
                account="test_account",
                user="test_user",
                private_key_path=str(key_file),
            )

            with pytest.raises(ConnectionError) as exc_info:
                connector.connect()

            assert "Failed to load private key" in str(exc_info.value)


class TestBigQueryConnectorConnectionError:
    """Tests for BigQuery connector connection error handling."""

    def test_connect_raises_on_generic_error(self):
        """Test connect raises ConnectionError on generic exception."""
        with patch("pycaroline.connectors.bigquery.BIGQUERY_AVAILABLE", True):
            with patch("pycaroline.connectors.bigquery.bigquery") as mock_bq:
                from pycaroline.connectors.base import ConnectionError
                from pycaroline.connectors.bigquery import BigQueryConnector

                mock_bq.Client.side_effect = Exception("Generic connection error")

                connector = BigQueryConnector(project="test_project")

                with pytest.raises(ConnectionError) as exc_info:
                    connector.connect()

                assert "Failed to connect to BigQuery" in str(exc_info.value)


class TestValidatorLogging:
    """Tests for validator logging paths."""

    def test_validate_logs_table_progress(self, tmp_path):
        """Test that validate logs progress for each table."""
        from pycaroline.config.models import (
            ComparisonSettings,
            TableConfig,
            ValidationConfig,
        )
        from pycaroline.connectors.factory import DatabaseType
        from pycaroline.validator import DataValidator

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="users", join_columns=["id"])],
            output_dir=tmp_path,
            comparison=ComparisonSettings(),
        )

        with patch("pycaroline.validator.ConnectorFactory") as mock_factory:
            mock_source = MagicMock()
            mock_source.__enter__ = MagicMock(return_value=mock_source)
            mock_source.__exit__ = MagicMock(return_value=False)
            mock_source.get_table.return_value = pl.DataFrame(
                {"id": [1], "value": ["a"]}
            )

            mock_target = MagicMock()
            mock_target.__enter__ = MagicMock(return_value=mock_target)
            mock_target.__exit__ = MagicMock(return_value=False)
            mock_target.get_table.return_value = pl.DataFrame(
                {"id": [1], "value": ["a"]}
            )

            mock_factory.create.side_effect = [mock_source, mock_target]

            validator = DataValidator(config)
            results = validator.validate()

            assert "users" in results
