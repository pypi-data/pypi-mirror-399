"""Unit tests for DataValidator."""

from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from pycaroline.comparison.models import ComparisonResult
from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.base import BaseConnector
from pycaroline.connectors.factory import DatabaseType
from pycaroline.validator import DataValidator, ValidationError


class MockConnector(BaseConnector):
    """Mock connector for testing."""

    def __init__(self, data_map=None, **kwargs):
        self._connection = None
        self.data_map = data_map or {}

    def connect(self):
        self._connection = MagicMock()

    def disconnect(self):
        self._connection = None

    def query(self, sql):
        return pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    def get_table(self, table, schema=None, limit=None):
        key = f"{schema}.{table}" if schema else table
        return self.data_map.get(key, pl.DataFrame({"id": [1], "value": ["x"]}))


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample ValidationConfig."""
    return ValidationConfig(
        source_db_type=DatabaseType.SNOWFLAKE,
        source_connection={"account": "test", "user": "u", "password": "p"},
        target_db_type=DatabaseType.BIGQUERY,
        target_connection={"project": "test"},
        tables=[TableConfig(source_table="users", join_columns=["id"])],
        output_dir=tmp_path,
        comparison=ComparisonSettings(),
    )


class TestDataValidatorInit:
    """Tests for DataValidator initialization."""

    def test_init_creates_reporter(self, sample_config):
        """Test that initialization creates a ReportGenerator."""
        validator = DataValidator(sample_config)

        assert validator.reporter is not None
        assert validator.config == sample_config

    def test_init_creates_output_directory(self, tmp_path):
        """Test that output directory is created."""
        output_dir = tmp_path / "new_output"
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="t", join_columns=["id"])],
            output_dir=output_dir,
        )

        DataValidator(config)

        assert output_dir.exists()


class TestDataValidatorValidate:
    """Tests for the validate method."""

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_returns_results_dict(self, mock_factory, sample_config):
        """Test that validate returns a dictionary of results."""
        mock_source = MockConnector()
        mock_target = MockConnector()
        mock_factory.create.side_effect = [mock_source, mock_target]

        validator = DataValidator(sample_config)
        results = validator.validate()

        assert isinstance(results, dict)
        assert "users" in results

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_processes_all_tables(self, mock_factory, tmp_path):
        """Test that validate processes all configured tables."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[
                TableConfig(source_table="users", join_columns=["id"]),
                TableConfig(source_table="orders", join_columns=["id"]),
            ],
            output_dir=tmp_path,
        )
        mock_source = MockConnector()
        mock_target = MockConnector()
        mock_factory.create.side_effect = [mock_source, mock_target]

        validator = DataValidator(config)
        results = validator.validate()

        assert len(results) == 2
        assert "users" in results
        assert "orders" in results

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_generates_reports(self, mock_factory, sample_config):
        """Test that validate generates reports for each table."""
        mock_source = MockConnector()
        mock_target = MockConnector()
        mock_factory.create.side_effect = [mock_source, mock_target]

        validator = DataValidator(sample_config)
        validator.validate()

        # Check that report files were created
        json_file = sample_config.output_dir / "users_summary.json"
        html_file = sample_config.output_dir / "users_report.html"
        assert json_file.exists()
        assert html_file.exists()


class TestDataValidatorValidateTable:
    """Tests for the _validate_table method."""

    def test_validate_table_uses_custom_query(self, sample_config):
        """Test that custom queries are used when specified."""
        table_config = TableConfig(
            source_table="users",
            join_columns=["id"],
            source_query="SELECT * FROM users WHERE active = true",
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "query", return_value=pl.DataFrame({"id": [1]})
        ) as mock_query:
            with patch.object(
                mock_target, "get_table", return_value=pl.DataFrame({"id": [1]})
            ):
                validator._validate_table(mock_source, mock_target, table_config)
                mock_query.assert_called_once()

    def test_validate_table_uses_schema(self, sample_config):
        """Test that schema is passed to get_table."""
        table_config = TableConfig(
            source_table="users", source_schema="prod", join_columns=["id"]
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "get_table", return_value=pl.DataFrame({"id": [1]})
        ) as mock_get:
            with patch.object(
                mock_target, "get_table", return_value=pl.DataFrame({"id": [1]})
            ):
                validator._validate_table(mock_source, mock_target, table_config)
                mock_get.assert_called_with("users", "prod", None)

    def test_validate_table_returns_comparison_result(self, sample_config):
        """Test that _validate_table returns a ComparisonResult."""
        table_config = TableConfig(source_table="users", join_columns=["id"])
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)
        result = validator._validate_table(mock_source, mock_target, table_config)

        assert isinstance(result, ComparisonResult)


class TestDataValidatorValidateSingleTable:
    """Tests for validate_single_table method."""

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_single_table_creates_connections(
        self, mock_factory, sample_config
    ):
        """Test that validate_single_table creates fresh connections."""
        mock_source = MockConnector()
        mock_target = MockConnector()
        mock_factory.create.side_effect = [mock_source, mock_target]

        table_config = TableConfig(source_table="users", join_columns=["id"])
        validator = DataValidator(sample_config)
        result = validator.validate_single_table(table_config)

        assert isinstance(result, ComparisonResult)
        assert mock_factory.create.call_count == 2


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_message(self):
        """Test ValidationError stores message correctly."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
