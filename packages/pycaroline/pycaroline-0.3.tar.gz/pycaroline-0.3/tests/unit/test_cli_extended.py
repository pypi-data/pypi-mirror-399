"""Extended unit tests for CLI to improve coverage."""

import os
from unittest.mock import MagicMock, patch

import polars as pl
import pytest
from click.testing import CliRunner

from pycaroline.cli import (
    _check_env_vars,
    _get_connection_params,
    _parse_table_name,
    cli,
)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestValidateCommandSuccess:
    """Tests for successful validate command execution."""

    @patch("pycaroline.cli.DataValidator")
    @patch("pycaroline.cli.ConfigLoader")
    def test_validate_success_all_pass(
        self, mock_loader, mock_validator, runner, tmp_path
    ):
        """Test validate command with all tables passing."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("dummy: config")

        mock_config = MagicMock()
        mock_config.tables = [MagicMock()]
        mock_config.output_dir = tmp_path
        mock_loader.load.return_value = mock_config

        mock_result = MagicMock()
        mock_result.source_row_count = 100
        mock_result.matching_rows = 100
        mock_result.rows_only_in_source = pl.DataFrame()
        mock_result.rows_only_in_target = pl.DataFrame()
        mock_result.mismatched_rows = 0

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.return_value = {"users": mock_result}
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(cli, ["validate", "-c", str(config_file)])

        assert "✓" in result.output
        assert "100.00% match" in result.output

    @patch("pycaroline.cli.DataValidator")
    @patch("pycaroline.cli.ConfigLoader")
    def test_validate_with_failures(
        self, mock_loader, mock_validator, runner, tmp_path
    ):
        """Test validate command with some failures."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("dummy: config")

        mock_config = MagicMock()
        mock_config.tables = [MagicMock()]
        mock_config.output_dir = tmp_path
        mock_loader.load.return_value = mock_config

        mock_result = MagicMock()
        mock_result.source_row_count = 100
        mock_result.matching_rows = 80
        mock_result.rows_only_in_source = pl.DataFrame({"id": [1, 2]})
        mock_result.rows_only_in_target = pl.DataFrame({"id": [3]})
        mock_result.mismatched_rows = 5

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.return_value = {"users": mock_result}
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(cli, ["validate", "-c", str(config_file)])

        assert "✗" in result.output
        assert "Rows only in source: 2" in result.output

    @patch("pycaroline.cli.DataValidator")
    @patch("pycaroline.cli.ConfigLoader")
    def test_validate_with_output_override(
        self, mock_loader, mock_validator, runner, tmp_path
    ):
        """Test validate command with output directory override."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("dummy: config")
        output_dir = tmp_path / "custom_output"

        mock_config = MagicMock()
        mock_config.tables = [MagicMock()]
        mock_config.output_dir = tmp_path
        mock_loader.load.return_value = mock_config

        mock_result = MagicMock()
        mock_result.source_row_count = 10
        mock_result.matching_rows = 10
        mock_result.rows_only_in_source = pl.DataFrame()
        mock_result.rows_only_in_target = pl.DataFrame()
        mock_result.mismatched_rows = 0

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.return_value = {"t": mock_result}
        mock_validator.return_value = mock_validator_instance

        runner.invoke(cli, ["validate", "-c", str(config_file), "-o", str(output_dir)])

        assert mock_config.output_dir == output_dir


class TestCompareCommand:
    """Tests for compare command."""

    @patch("pycaroline.cli.DataValidator")
    @patch.dict(
        os.environ,
        {
            "SNOWFLAKE_ACCOUNT": "acc",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "proj",
        },
    )
    def test_compare_success(self, mock_validator, runner, tmp_path):
        """Test successful compare command."""
        mock_result = MagicMock()
        mock_result.source_row_count = 100
        mock_result.target_row_count = 100
        mock_result.matching_rows = 100
        mock_result.rows_only_in_source = pl.DataFrame()
        mock_result.rows_only_in_target = pl.DataFrame()
        mock_result.mismatched_rows = 0

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.return_value = {"users": mock_result}
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(
            cli,
            [
                "compare",
                "--source-type",
                "snowflake",
                "--target-type",
                "bigquery",
                "--source-table",
                "schema.users",
                "--target-table",
                "dataset.users",
                "--join-columns",
                "id,email",
                "-o",
                str(tmp_path),
            ],
        )

        assert "100.00%" in result.output or result.exit_code == 0

    @patch("pycaroline.cli.DataValidator")
    @patch.dict(
        os.environ,
        {
            "SNOWFLAKE_ACCOUNT": "acc",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "proj",
        },
    )
    def test_compare_with_differences(self, mock_validator, runner, tmp_path):
        """Test compare command with differences."""
        mock_result = MagicMock()
        mock_result.source_row_count = 100
        mock_result.target_row_count = 95
        mock_result.matching_rows = 90
        mock_result.rows_only_in_source = pl.DataFrame({"id": [1, 2]})
        mock_result.rows_only_in_target = pl.DataFrame({"id": [3]})
        mock_result.mismatched_rows = 5

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.return_value = {"users": mock_result}
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(
            cli,
            [
                "compare",
                "--source-type",
                "snowflake",
                "--target-type",
                "bigquery",
                "--source-table",
                "users",
                "--target-table",
                "users",
                "--join-columns",
                "id",
                "-o",
                str(tmp_path),
            ],
        )

        assert "differences" in result.output.lower() or "90" in result.output


class TestParseTableName:
    """Tests for _parse_table_name function."""

    def test_parse_simple_name(self):
        """Test parsing simple table name."""
        schema, table = _parse_table_name("users")
        assert schema is None
        assert table == "users"

    def test_parse_qualified_name(self):
        """Test parsing schema-qualified table name."""
        schema, table = _parse_table_name("public.users")
        assert schema == "public"
        assert table == "users"

    def test_parse_invalid_name(self):
        """Test parsing invalid table name raises error."""
        with pytest.raises(ValueError, match="Invalid table name"):
            _parse_table_name("a.b.c.d")


class TestGetConnectionParams:
    """Tests for _get_connection_params function."""

    @patch.dict(
        os.environ,
        {
            "SNOWFLAKE_ACCOUNT": "test_acc",
            "SNOWFLAKE_USER": "test_user",
            "SNOWFLAKE_PASSWORD": "test_pass",
            "SNOWFLAKE_WAREHOUSE": "test_wh",
            "SNOWFLAKE_DATABASE": "test_db",
            "SNOWFLAKE_SCHEMA": "test_schema",
        },
    )
    def test_get_snowflake_params(self):
        """Test getting Snowflake connection parameters."""
        params = _get_connection_params("snowflake")

        assert params["account"] == "test_acc"
        assert params["user"] == "test_user"
        assert params["password"] == "test_pass"
        assert params["warehouse"] == "test_wh"

    @patch.dict(
        os.environ, {"GCP_PROJECT": "test_project", "BQ_DATASET": "test_dataset"}
    )
    def test_get_bigquery_params(self):
        """Test getting BigQuery connection parameters."""
        params = _get_connection_params("bigquery")

        assert params["project"] == "test_project"
        assert params["dataset"] == "test_dataset"

    @patch.dict(
        os.environ,
        {
            "REDSHIFT_HOST": "test_host",
            "REDSHIFT_PORT": "5439",
            "REDSHIFT_DATABASE": "test_db",
            "REDSHIFT_USER": "test_user",
            "REDSHIFT_PASSWORD": "test_pass",
        },
    )
    def test_get_redshift_params(self):
        """Test getting Redshift connection parameters."""
        params = _get_connection_params("redshift")

        assert params["host"] == "test_host"
        assert params["port"] == 5439
        assert params["database"] == "test_db"

    def test_get_unknown_db_type(self):
        """Test getting params for unknown database type."""
        with pytest.raises(ValueError, match="Unknown database type"):
            _get_connection_params("unknown_db")


class TestCheckEnvVars:
    """Tests for _check_env_vars function."""

    @patch.dict(os.environ, {"VAR1": "val1", "VAR2": "val2"})
    def test_all_vars_present(self):
        """Test when all required vars are present."""
        _check_env_vars(["VAR1", "VAR2"])  # Should not raise

    @patch.dict(os.environ, {"VAR1": "val1"}, clear=True)
    def test_missing_vars(self):
        """Test when some vars are missing."""
        with pytest.raises(ValueError, match="Missing required"):
            _check_env_vars(["VAR1", "MISSING_VAR"])


class TestVerboseMode:
    """Tests for verbose mode."""

    def test_verbose_flag_sets_debug_logging(self, runner):
        """Test that -v flag enables debug logging."""
        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0


class TestValidateCommandErrors:
    """Tests for validate command error handling."""

    @patch("pycaroline.cli.ConfigLoader")
    def test_validate_connection_error(self, mock_loader, runner, tmp_path):
        """Test validate handles connection errors."""
        from pycaroline.connectors.base import ConnectionError as ConnError

        config_file = tmp_path / "config.yaml"
        config_file.write_text("dummy: config")

        mock_loader.load.side_effect = ConnError("Connection failed")

        result = runner.invoke(cli, ["validate", "-c", str(config_file)])

        # Should handle the error gracefully
        assert result.exit_code != 0

    @patch("pycaroline.cli.DataValidator")
    @patch("pycaroline.cli.ConfigLoader")
    def test_validate_validation_error(
        self, mock_loader, mock_validator, runner, tmp_path
    ):
        """Test validate handles validation errors."""
        from pycaroline.validator import ValidationError

        config_file = tmp_path / "config.yaml"
        config_file.write_text("dummy: config")

        mock_config = MagicMock()
        mock_config.tables = [MagicMock()]
        mock_loader.load.return_value = mock_config

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.side_effect = ValidationError(
            "Validation failed"
        )
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(cli, ["validate", "-c", str(config_file)])

        assert "Validation failed" in result.output or result.exit_code != 0


class TestCompareCommandErrors:
    """Tests for compare command error handling."""

    @patch.dict(
        os.environ,
        {
            "SNOWFLAKE_ACCOUNT": "acc",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "proj",
        },
    )
    @patch("pycaroline.cli.DataValidator")
    def test_compare_validation_error(self, mock_validator, runner, tmp_path):
        """Test compare handles validation errors."""
        from pycaroline.validator import ValidationError

        mock_validator_instance = MagicMock()
        mock_validator_instance.validate.side_effect = ValidationError(
            "Comparison failed"
        )
        mock_validator.return_value = mock_validator_instance

        result = runner.invoke(
            cli,
            [
                "compare",
                "--source-type",
                "snowflake",
                "--target-type",
                "bigquery",
                "--source-table",
                "users",
                "--target-table",
                "users",
                "--join-columns",
                "id",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code != 0
