"""Unit tests for data models."""

from pathlib import Path

import polars as pl

from pycaroline.comparison.models import ComparisonConfig, ComparisonResult
from pycaroline.config.models import ComparisonSettings, TableConfig, ValidationConfig
from pycaroline.connectors.factory import DatabaseType


class TestComparisonConfig:
    """Tests for ComparisonConfig dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        config = ComparisonConfig(join_columns=["id"])

        assert config.abs_tol == 0.0001
        assert config.rel_tol == 0.0
        assert config.ignore_case is False
        assert config.ignore_spaces is True

    def test_custom_values(self):
        """Test custom values are stored correctly."""
        config = ComparisonConfig(
            join_columns=["id", "name"],
            abs_tol=0.01,
            rel_tol=0.001,
            ignore_case=True,
            ignore_spaces=False,
        )

        assert config.join_columns == ["id", "name"]
        assert config.abs_tol == 0.01
        assert config.rel_tol == 0.001
        assert config.ignore_case is True
        assert config.ignore_spaces is False


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""

    def test_stores_all_fields(self):
        """Test all fields are stored correctly."""
        result = ComparisonResult(
            source_row_count=100,
            target_row_count=95,
            matching_rows=90,
            mismatched_rows=5,
            rows_only_in_source=pl.DataFrame({"id": [1]}),
            rows_only_in_target=pl.DataFrame({"id": [2]}),
            mismatched_columns=pl.DataFrame(),
            column_stats=pl.DataFrame(),
            report_text="Test report",
        )

        assert result.source_row_count == 100
        assert result.target_row_count == 95
        assert result.matching_rows == 90
        assert result.mismatched_rows == 5
        assert len(result.rows_only_in_source) == 1
        assert result.report_text == "Test report"


class TestTableConfig:
    """Tests for TableConfig dataclass."""

    def test_target_table_defaults_to_source(self):
        """Test target_table defaults to source_table."""
        config = TableConfig(source_table="users", join_columns=["id"])

        assert config.target_table == "users"

    def test_explicit_target_table(self):
        """Test explicit target_table is preserved."""
        config = TableConfig(
            source_table="users", target_table="users_copy", join_columns=["id"]
        )

        assert config.target_table == "users_copy"

    def test_optional_fields_default_to_none(self):
        """Test optional fields default to None."""
        config = TableConfig(source_table="users", join_columns=["id"])

        assert config.source_schema is None
        assert config.target_schema is None
        assert config.source_query is None
        assert config.target_query is None
        assert config.sample_size is None


class TestComparisonSettings:
    """Tests for ComparisonSettings dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        settings = ComparisonSettings()

        assert settings.abs_tol == 0.0001
        assert settings.rel_tol == 0.0
        assert settings.ignore_case is False
        assert settings.ignore_spaces is True


class TestValidationConfig:
    """Tests for ValidationConfig dataclass."""

    def test_output_dir_string_converted_to_path(self):
        """Test string output_dir is converted to Path."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="t", join_columns=["id"])],
            output_dir="./output",
        )

        assert isinstance(config.output_dir, Path)
        assert config.output_dir == Path("./output")

    def test_default_output_dir(self):
        """Test default output directory."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="t", join_columns=["id"])],
        )

        assert config.output_dir == Path("./validation_results")

    def test_default_comparison_settings(self):
        """Test default comparison settings."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={},
            tables=[TableConfig(source_table="t", join_columns=["id"])],
        )

        assert isinstance(config.comparison, ComparisonSettings)
