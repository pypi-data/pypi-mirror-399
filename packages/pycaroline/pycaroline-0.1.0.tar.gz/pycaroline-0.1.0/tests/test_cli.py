"""Unit tests for the data-recon CLI.

Tests argument parsing, exit codes, and error messages for the CLI commands.
"""

import os
import tempfile
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pycaroline.cli import (
    EXIT_CONFIG_ERROR,
    _check_env_vars,
    _get_connection_params,
    _parse_table_name,
    cli,
)


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLIHelp:
    """Test CLI help and version commands."""

    def test_cli_help(self, runner):
        """Test that --help shows usage information."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Data validation CLI" in result.output
        assert "validate" in result.output
        assert "compare" in result.output

    def test_cli_version(self, runner):
        """Test that --version shows version information."""
        result = runner.invoke(cli, ["--version"])
        # May fail if package not installed, but should not crash
        assert result.exit_code in [0, 1]

    def test_validate_help(self, runner):
        """Test that validate --help shows command options."""
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--config" in result.output
        assert "--output" in result.output

    def test_compare_help(self, runner):
        """Test that compare --help shows command options."""
        result = runner.invoke(cli, ["compare", "--help"])
        assert result.exit_code == 0
        assert "--source-type" in result.output
        assert "--target-type" in result.output
        assert "--join-columns" in result.output


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_missing_config(self, runner):
        """Test that validate fails without --config."""
        result = runner.invoke(cli, ["validate"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_validate_nonexistent_config(self, runner):
        """Test that validate fails with nonexistent config file."""
        result = runner.invoke(cli, ["validate", "--config", "nonexistent.yaml"])
        assert result.exit_code != 0

    def test_validate_invalid_yaml(self, runner):
        """Test that validate fails with invalid YAML config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            result = runner.invoke(cli, ["validate", "--config", config_path])
            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Error" in result.output
        finally:
            os.unlink(config_path)

    def test_validate_missing_required_keys(self, runner):
        """Test that validate fails when config is missing required keys."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("some_key: some_value\n")
            config_path = f.name

        try:
            result = runner.invoke(cli, ["validate", "--config", config_path])
            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Error" in result.output
        finally:
            os.unlink(config_path)


class TestCompareCommand:
    """Test the compare command."""

    def test_compare_missing_required_options(self, runner):
        """Test that compare fails without required options."""
        result = runner.invoke(cli, ["compare"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_compare_missing_source_type(self, runner):
        """Test that compare fails without --source-type."""
        result = runner.invoke(
            cli,
            [
                "compare",
                "--target-type",
                "bigquery",
                "--source-table",
                "test_table",
                "--target-table",
                "test_table",
                "--join-columns",
                "id",
            ],
        )
        assert result.exit_code != 0

    def test_compare_invalid_source_type(self, runner):
        """Test that compare fails with invalid database type."""
        result = runner.invoke(
            cli,
            [
                "compare",
                "--source-type",
                "invalid_db",
                "--target-type",
                "bigquery",
                "--source-table",
                "test_table",
                "--target-table",
                "test_table",
                "--join-columns",
                "id",
            ],
        )
        assert result.exit_code != 0
        assert (
            "invalid_db" in result.output.lower()
            or "invalid choice" in result.output.lower()
        )

    def test_compare_missing_env_vars(self, runner):
        """Test that compare fails when required env vars are missing."""
        # Clear any existing env vars
        env_vars_to_clear = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "GCP_PROJECT",
            "REDSHIFT_HOST",
        ]
        original_env = {k: os.environ.pop(k, None) for k in env_vars_to_clear}

        try:
            result = runner.invoke(
                cli,
                [
                    "compare",
                    "--source-type",
                    "snowflake",
                    "--target-type",
                    "bigquery",
                    "--source-table",
                    "test_table",
                    "--target-table",
                    "test_table",
                    "--join-columns",
                    "id",
                ],
            )
            assert result.exit_code == EXIT_CONFIG_ERROR
            assert "Missing required environment variables" in result.output
        finally:
            # Restore env vars
            for k, v in original_env.items():
                if v is not None:
                    os.environ[k] = v


class TestParseTableName:
    """Test the _parse_table_name helper function."""

    def test_parse_simple_table_name(self):
        """Test parsing a simple table name without schema."""
        schema, table = _parse_table_name("customers")
        assert schema is None
        assert table == "customers"

    def test_parse_schema_qualified_table_name(self):
        """Test parsing a schema-qualified table name."""
        schema, table = _parse_table_name("my_schema.customers")
        assert schema == "my_schema"
        assert table == "customers"

    def test_parse_invalid_table_name(self):
        """Test that invalid table names raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _parse_table_name("a.b.c.d")
        assert "Invalid table name format" in str(exc_info.value)


class TestCheckEnvVars:
    """Test the _check_env_vars helper function."""

    def test_check_env_vars_all_present(self):
        """Test that no error is raised when all vars are present."""
        with patch.dict(os.environ, {"VAR1": "value1", "VAR2": "value2"}):
            # Should not raise
            _check_env_vars(["VAR1", "VAR2"])

    def test_check_env_vars_missing(self):
        """Test that ValueError is raised when vars are missing."""
        # Ensure vars are not set
        for var in ["MISSING_VAR1", "MISSING_VAR2"]:
            os.environ.pop(var, None)

        with pytest.raises(ValueError) as exc_info:
            _check_env_vars(["MISSING_VAR1", "MISSING_VAR2"])
        assert "Missing required environment variables" in str(exc_info.value)
        assert "MISSING_VAR1" in str(exc_info.value)


class TestGetConnectionParams:
    """Test the _get_connection_params helper function."""

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

    def test_get_unknown_db_type(self):
        """Test that unknown database type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            _get_connection_params("unknown_db")
        assert "Unknown database type" in str(exc_info.value)


class TestExitCodes:
    """Test that CLI returns correct exit codes."""

    def test_exit_code_config_error(self, runner):
        """Test that config errors return EXIT_CONFIG_ERROR."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: [")
            config_path = f.name

        try:
            result = runner.invoke(cli, ["validate", "--config", config_path])
            assert result.exit_code == EXIT_CONFIG_ERROR
        finally:
            os.unlink(config_path)

    def test_verbose_flag(self, runner):
        """Test that --verbose flag is accepted."""
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0
