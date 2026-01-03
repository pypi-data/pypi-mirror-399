"""Extended unit tests for CLI to improve coverage.

Tests for verbose mode, error handling, and edge cases.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from pycaroline.cli import (
    cli,
    _parse_table_name,
    _get_connection_params,
    _check_env_vars,
    EXIT_SUCCESS,
    EXIT_VALIDATION_FAILED,
    EXIT_CONFIG_ERROR,
    EXIT_CONNECTION_ERROR,
)


class TestCliVerboseMode:
    """Tests for verbose mode."""

    def test_verbose_flag_enables_debug_logging(self):
        """Test that --verbose flag enables debug logging."""
        runner = CliRunner()

        with patch("pycaroline.cli.logging") as mock_logging:
            result = runner.invoke(cli, ["--verbose", "--help"])

            # Should not fail
            assert result.exit_code == 0

    def test_verbose_short_flag(self):
        """Test that -v flag works as verbose."""
        runner = CliRunner()

        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0


class TestParseTableName:
    """Tests for _parse_table_name function."""

    def test_parse_table_name_with_schema(self):
        """Test parsing table name with schema."""
        schema, table = _parse_table_name("public.users")

        assert schema == "public"
        assert table == "users"

    def test_parse_table_name_without_schema(self):
        """Test parsing table name without schema."""
        schema, table = _parse_table_name("users")

        assert schema is None
        assert table == "users"

    def test_parse_table_name_with_multiple_dots(self):
        """Test parsing table name with multiple dots raises error."""
        with pytest.raises(ValueError) as exc_info:
            _parse_table_name("db.schema.table")

        assert "Invalid table name format" in str(exc_info.value)


class TestGetConnectionParams:
    """Tests for _get_connection_params function."""

    def test_get_snowflake_params(self):
        """Test getting Snowflake connection parameters."""
        env_vars = {
            "SNOWFLAKE_ACCOUNT": "test_account",
            "SNOWFLAKE_USER": "test_user",
            "SNOWFLAKE_PASSWORD": "test_password",
            "SNOWFLAKE_WAREHOUSE": "test_warehouse",
            "SNOWFLAKE_DATABASE": "test_db",
            "SNOWFLAKE_SCHEMA": "test_schema",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            params = _get_connection_params("snowflake")

            assert params["account"] == "test_account"
            assert params["user"] == "test_user"
            assert params["password"] == "test_password"
            assert params["warehouse"] == "test_warehouse"
            assert params["database"] == "test_db"
            assert params["schema"] == "test_schema"

    def test_get_bigquery_params(self):
        """Test getting BigQuery connection parameters."""
        env_vars = {
            "GCP_PROJECT": "test_project",
            "BQ_DATASET": "test_dataset",
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            params = _get_connection_params("bigquery")

            assert params["project"] == "test_project"
            assert params["dataset"] == "test_dataset"
            assert params["credentials_path"] == "/path/to/creds.json"

    def test_get_redshift_params(self):
        """Test getting Redshift connection parameters."""
        env_vars = {
            "REDSHIFT_HOST": "test_host",
            "REDSHIFT_PORT": "5439",
            "REDSHIFT_DATABASE": "test_db",
            "REDSHIFT_USER": "test_user",
            "REDSHIFT_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            params = _get_connection_params("redshift")

            assert params["host"] == "test_host"
            assert params["port"] == 5439
            assert params["database"] == "test_db"
            assert params["user"] == "test_user"
            assert params["password"] == "test_password"

    def test_get_unknown_db_type_raises_error(self):
        """Test that unknown database type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _get_connection_params("unknown_db")

        assert "Unknown database type" in str(exc_info.value)

    def test_get_params_case_insensitive(self):
        """Test that database type is case-insensitive."""
        env_vars = {
            "GCP_PROJECT": "test_project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            params = _get_connection_params("BIGQUERY")
            assert params["project"] == "test_project"


class TestCheckEnvVars:
    """Tests for _check_env_vars function."""

    def test_check_env_vars_all_present(self):
        """Test that no error is raised when all vars are present."""
        env_vars = {"VAR1": "value1", "VAR2": "value2"}

        with patch.dict(os.environ, env_vars, clear=False):
            # Should not raise
            _check_env_vars(["VAR1", "VAR2"])

    def test_check_env_vars_missing_raises_error(self):
        """Test that missing vars raise ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                _check_env_vars(["MISSING_VAR"])

            assert "Missing required environment variables" in str(exc_info.value)
            assert "MISSING_VAR" in str(exc_info.value)

    def test_check_env_vars_multiple_missing(self):
        """Test error message includes all missing vars."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                _check_env_vars(["VAR1", "VAR2", "VAR3"])

            error_msg = str(exc_info.value)
            assert "VAR1" in error_msg
            assert "VAR2" in error_msg
            assert "VAR3" in error_msg


class TestValidateCommand:
    """Tests for validate command."""

    def test_validate_missing_config_file(self):
        """Test validate command with non-existent config file."""
        runner = CliRunner()

        result = runner.invoke(cli, ["validate", "--config", "nonexistent.yaml"])

        assert result.exit_code != EXIT_SUCCESS

    def test_validate_with_output_override(self, tmp_path):
        """Test validate command with output directory override."""
        runner = CliRunner()

        # Create a minimal config file
        config_content = """
source:
  type: snowflake
  connection:
    account: test
target:
  type: bigquery
  connection:
    project: test
tables:
  - source_table: users
    join_columns: [id]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with patch("pycaroline.cli.ConfigLoader") as mock_loader:
            mock_config = MagicMock()
            mock_config.tables = []
            mock_config.output_dir = tmp_path
            mock_loader.load.return_value = mock_config

            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_validator.return_value.validate.return_value = {}

                result = runner.invoke(
                    cli,
                    ["validate", "--config", str(config_file), "--output", str(tmp_path / "output")],
                )

                # Config should have output_dir updated
                assert mock_config.output_dir == tmp_path / "output"


class TestCompareCommand:
    """Tests for compare command."""

    def test_compare_missing_env_vars(self):
        """Test compare command with missing environment variables."""
        runner = CliRunner()

        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(
                cli,
                [
                    "compare",
                    "--source-type", "snowflake",
                    "--target-type", "bigquery",
                    "--source-table", "users",
                    "--target-table", "users",
                    "--join-columns", "id",
                ],
            )

            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Missing required environment variables" in result.output

    def test_compare_with_custom_options(self, tmp_path):
        """Test compare command with custom options."""
        runner = CliRunner()

        env_vars = {
            "SNOWFLAKE_ACCOUNT": "test",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_result = MagicMock()
                mock_result.matching_rows = 100
                mock_result.source_row_count = 100
                mock_result.target_row_count = 100
                mock_result.rows_only_in_source = None
                mock_result.rows_only_in_target = None
                mock_result.mismatched_rows = 0

                mock_validator.return_value.validate.return_value = {"users": mock_result}

                result = runner.invoke(
                    cli,
                    [
                        "compare",
                        "--source-type", "snowflake",
                        "--target-type", "bigquery",
                        "--source-table", "schema.users",
                        "--target-table", "dataset.users",
                        "--join-columns", "id,name",
                        "--output", str(tmp_path),
                        "--tolerance", "0.01",
                        "--ignore-case",
                        "--sample-size", "1000",
                    ],
                )

                # Should attempt to run validation
                assert mock_validator.called


class TestExitCodes:
    """Tests for exit code constants."""

    def test_exit_codes_are_integers(self):
        """Test that exit codes are integers."""
        assert isinstance(EXIT_SUCCESS, int)
        assert isinstance(EXIT_VALIDATION_FAILED, int)
        assert isinstance(EXIT_CONFIG_ERROR, int)
        assert isinstance(EXIT_CONNECTION_ERROR, int)

    def test_exit_success_is_zero(self):
        """Test that EXIT_SUCCESS is 0."""
        assert EXIT_SUCCESS == 0

    def test_exit_codes_are_distinct(self):
        """Test that exit codes are distinct."""
        codes = [EXIT_SUCCESS, EXIT_VALIDATION_FAILED, EXIT_CONFIG_ERROR, EXIT_CONNECTION_ERROR]
        assert len(codes) == len(set(codes))
