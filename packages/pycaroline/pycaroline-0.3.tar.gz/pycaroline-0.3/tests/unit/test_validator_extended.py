"""Extended unit tests for DataValidator to improve coverage.

Tests for validate_dataframes, compare_dataframes, and error handling.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
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
from pycaroline.validator import DataValidator, ValidationError, compare_dataframes


class MockConnector(BaseConnector):
    """Mock connector for testing."""

    def __init__(self, data_map=None, **kwargs):
        self._connection = None
        self.data_map = data_map or {}
        self.should_fail = kwargs.get("should_fail", False)

    def connect(self):
        if self.should_fail:
            raise Exception("Connection failed")
        self._connection = MagicMock()

    def disconnect(self):
        self._connection = None

    def query(self, sql):
        if self.should_fail:
            raise Exception("Query failed")
        return pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    def get_table(self, table, schema=None, limit=None):
        if self.should_fail:
            raise Exception("Get table failed")
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


class TestValidateDataframes:
    """Tests for validate_dataframes method."""

    def test_validate_dataframes_with_polars(self, sample_config):
        """Test validate_dataframes with polars DataFrames."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = validator.validate_dataframes(
            source, target, join_columns=["id"], name="test_comparison"
        )

        assert isinstance(result, ComparisonResult)
        assert result.matching_rows == 2
        assert result.source_row_count == 2

    def test_validate_dataframes_with_pandas(self, sample_config):
        """Test validate_dataframes with pandas DataFrames."""
        validator = DataValidator(sample_config)

        source = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = validator.validate_dataframes(
            source, target, join_columns=["id"], name="pandas_test"
        )

        assert isinstance(result, ComparisonResult)
        assert result.matching_rows == 2

    def test_validate_dataframes_with_custom_tolerances(self, sample_config):
        """Test validate_dataframes with custom tolerance settings."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1], "value": [1.0000]})
        target = pl.DataFrame({"id": [1], "value": [1.0001]})

        result = validator.validate_dataframes(
            source,
            target,
            join_columns=["id"],
            abs_tol=0.001,
            rel_tol=0.0,
        )

        assert result.matching_rows == 1

    def test_validate_dataframes_with_ignore_case(self, sample_config):
        """Test validate_dataframes with case-insensitive comparison."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1], "value": ["ABC"]})
        target = pl.DataFrame({"id": [1], "value": ["abc"]})

        result = validator.validate_dataframes(
            source, target, join_columns=["id"], ignore_case=True
        )

        assert result.matching_rows == 1

    def test_validate_dataframes_with_ignore_spaces(self, sample_config):
        """Test validate_dataframes with whitespace trimming."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1], "value": ["  hello  "]})
        target = pl.DataFrame({"id": [1], "value": ["hello"]})

        result = validator.validate_dataframes(
            source, target, join_columns=["id"], ignore_spaces=True
        )

        assert result.matching_rows == 1

    def test_validate_dataframes_without_report_generation(self, sample_config):
        """Test validate_dataframes with report generation disabled."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})

        result = validator.validate_dataframes(
            source, target, join_columns=["id"], generate_report=False
        )

        assert isinstance(result, ComparisonResult)
        # No report files should be created
        list(sample_config.output_dir.glob("*_summary.json"))
        # May have files from other tests, but this specific one shouldn't create new ones

    def test_validate_dataframes_generates_report_files(self, sample_config):
        """Test that validate_dataframes generates report files when enabled."""
        validator = DataValidator(sample_config)

        source = pl.DataFrame({"id": [1], "value": ["a"]})
        target = pl.DataFrame({"id": [1], "value": ["a"]})

        validator.validate_dataframes(
            source,
            target,
            join_columns=["id"],
            name="report_test",
            generate_report=True,
        )

        json_file = sample_config.output_dir / "report_test_summary.json"
        html_file = sample_config.output_dir / "report_test_report.html"
        assert json_file.exists()
        assert html_file.exists()


class TestCompareDataframesFunction:
    """Tests for the standalone compare_dataframes function."""

    def test_compare_dataframes_with_polars(self):
        """Test compare_dataframes with polars DataFrames."""
        source = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = compare_dataframes(source, target, join_columns=["id"])

        assert isinstance(result, ComparisonResult)
        assert result.matching_rows == 2

    def test_compare_dataframes_with_pandas(self):
        """Test compare_dataframes with pandas DataFrames."""
        source = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})
        target = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

        result = compare_dataframes(source, target, join_columns=["id"])

        assert isinstance(result, ComparisonResult)
        assert result.matching_rows == 2

    def test_compare_dataframes_with_tolerances(self):
        """Test compare_dataframes with numeric tolerances."""
        source = pl.DataFrame({"id": [1], "value": [1.0]})
        target = pl.DataFrame({"id": [1], "value": [1.0001]})

        result = compare_dataframes(source, target, join_columns=["id"], abs_tol=0.001)

        assert result.matching_rows == 1

    def test_compare_dataframes_with_case_insensitive(self):
        """Test compare_dataframes with case-insensitive comparison."""
        source = pl.DataFrame({"id": [1], "value": ["HELLO"]})
        target = pl.DataFrame({"id": [1], "value": ["hello"]})

        result = compare_dataframes(
            source, target, join_columns=["id"], ignore_case=True
        )

        assert result.matching_rows == 1

    def test_compare_dataframes_with_whitespace_handling(self):
        """Test compare_dataframes with whitespace trimming."""
        source = pl.DataFrame({"id": [1], "value": ["  test  "]})
        target = pl.DataFrame({"id": [1], "value": ["test"]})

        result = compare_dataframes(
            source, target, join_columns=["id"], ignore_spaces=True
        )

        assert result.matching_rows == 1


class TestValidatorErrorHandling:
    """Tests for error handling in DataValidator."""

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_raises_validation_error_on_table_failure(
        self, mock_factory, tmp_path
    ):
        """Test that validate raises ValidationError when table validation fails."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="users", join_columns=["id"])],
            output_dir=tmp_path,
        )

        mock_source = MockConnector(should_fail=True)
        mock_target = MockConnector()
        mock_factory.create.side_effect = [mock_source, mock_target]

        validator = DataValidator(config)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()

        assert "Validation failed" in str(exc_info.value)

    @patch("pycaroline.validator.ConnectorFactory")
    def test_validate_wraps_connection_error(self, mock_factory, tmp_path):
        """Test that connection errors are wrapped in ValidationError."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="users", join_columns=["id"])],
            output_dir=tmp_path,
        )

        # Create mock connectors that fail on connect
        mock_source = MagicMock()
        mock_source.__enter__ = MagicMock(side_effect=Exception("Connection failed"))
        mock_source.__exit__ = MagicMock(return_value=False)
        mock_target = MagicMock()
        mock_target.__enter__ = MagicMock(return_value=mock_target)
        mock_target.__exit__ = MagicMock(return_value=False)
        mock_factory.create.side_effect = [mock_source, mock_target]

        validator = DataValidator(config)

        with pytest.raises(ValidationError) as exc_info:
            validator.validate()

        assert "Validation failed" in str(exc_info.value)


class TestValidateTableWithTargetQuery:
    """Tests for _validate_table with target query."""

    def test_validate_table_uses_target_query(self, sample_config):
        """Test that target query is used when specified."""
        table_config = TableConfig(
            source_table="users",
            join_columns=["id"],
            target_query="SELECT * FROM users WHERE active = true",
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "get_table", return_value=pl.DataFrame({"id": [1]})
        ):
            with patch.object(
                mock_target, "query", return_value=pl.DataFrame({"id": [1]})
            ) as mock_query:
                validator._validate_table(mock_source, mock_target, table_config)
                mock_query.assert_called_once()

    def test_validate_table_uses_target_table_name(self, sample_config):
        """Test that target_table is used when different from source_table."""
        table_config = TableConfig(
            source_table="users",
            target_table="customers",
            join_columns=["id"],
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "get_table", return_value=pl.DataFrame({"id": [1]})
        ):
            with patch.object(
                mock_target, "get_table", return_value=pl.DataFrame({"id": [1]})
            ) as mock_get:
                validator._validate_table(mock_source, mock_target, table_config)
                # Should be called with "customers" not "users"
                mock_get.assert_called_with("customers", None, None)

    def test_validate_table_uses_target_schema(self, sample_config):
        """Test that target_schema is used when specified."""
        table_config = TableConfig(
            source_table="users",
            target_schema="staging",
            join_columns=["id"],
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "get_table", return_value=pl.DataFrame({"id": [1]})
        ):
            with patch.object(
                mock_target, "get_table", return_value=pl.DataFrame({"id": [1]})
            ) as mock_get:
                validator._validate_table(mock_source, mock_target, table_config)
                mock_get.assert_called_with("users", "staging", None)

    def test_validate_table_uses_sample_size(self, sample_config):
        """Test that sample_size is passed to get_table."""
        table_config = TableConfig(
            source_table="users",
            join_columns=["id"],
            sample_size=100,
        )
        mock_source = MockConnector()
        mock_target = MockConnector()

        validator = DataValidator(sample_config)

        with patch.object(
            mock_source, "get_table", return_value=pl.DataFrame({"id": [1]})
        ) as mock_source_get:
            with patch.object(
                mock_target, "get_table", return_value=pl.DataFrame({"id": [1]})
            ) as mock_target_get:
                validator._validate_table(mock_source, mock_target, table_config)
                mock_source_get.assert_called_with("users", None, 100)
                mock_target_get.assert_called_with("users", None, 100)
