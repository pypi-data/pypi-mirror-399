"""Additional tests for CLI to improve coverage.

Tests for edge cases and error handling paths.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from pycaroline.cli import cli


class TestValidateCommandEdgeCases:
    """Tests for validate command edge cases."""

    def test_validate_with_100_percent_match(self, tmp_path):
        """Test validate command with 100% match shows success."""
        runner = CliRunner()

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
            mock_config.tables = [MagicMock(source_table="users")]
            mock_config.output_dir = tmp_path
            mock_loader.load.return_value = mock_config

            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_result = MagicMock()
                mock_result.matching_rows = 100
                mock_result.source_row_count = 100
                mock_result.target_row_count = 100
                mock_result.rows_only_in_source = None
                mock_result.rows_only_in_target = None
                mock_result.mismatched_rows = 0

                mock_validator.return_value.validate.return_value = {"users": mock_result}

                result = runner.invoke(cli, ["validate", "--config", str(config_file)])

                assert "All validations passed" in result.output

    def test_validate_with_partial_match(self, tmp_path):
        """Test validate command with partial match shows failure."""
        runner = CliRunner()

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
            mock_config.tables = [MagicMock(source_table="users")]
            mock_config.output_dir = tmp_path
            mock_loader.load.return_value = mock_config

            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_result = MagicMock()
                mock_result.matching_rows = 80
                mock_result.source_row_count = 100
                mock_result.target_row_count = 100
                mock_result.rows_only_in_source = MagicMock(__len__=lambda x: 10)
                mock_result.rows_only_in_target = MagicMock(__len__=lambda x: 5)
                mock_result.mismatched_rows = 5

                mock_validator.return_value.validate.return_value = {"users": mock_result}

                result = runner.invoke(cli, ["validate", "--config", str(config_file)])

                assert "Some validations failed" in result.output

    def test_validate_with_configuration_error(self, tmp_path):
        """Test validate command handles ConfigurationError."""
        runner = CliRunner()

        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: config")

        with patch("pycaroline.cli.ConfigLoader") as mock_loader:
            from pycaroline.config.loader import ConfigurationError
            mock_loader.load.side_effect = ConfigurationError("Invalid config")

            result = runner.invoke(cli, ["validate", "--config", str(config_file)])

            assert result.exit_code == 2
            assert "Configuration error" in result.output

    def test_validate_with_validation_error(self, tmp_path):
        """Test validate command handles ValidationError."""
        runner = CliRunner()

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
                from pycaroline.validator import ValidationError
                mock_validator.return_value.validate.side_effect = ValidationError("Validation failed")

                result = runner.invoke(cli, ["validate", "--config", str(config_file)])

                assert result.exit_code == 1
                assert "Validation failed" in result.output


class TestCompareCommandEdgeCases:
    """Tests for compare command edge cases."""

    def test_compare_with_source_query(self, tmp_path):
        """Test compare command with source query option."""
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
                        "--source-table", "users",
                        "--target-table", "users",
                        "--join-columns", "id",
                        "--source-query", "SELECT * FROM users WHERE active = true",
                        "--output", str(tmp_path),
                    ],
                )

                # Should have been called
                assert mock_validator.called

    def test_compare_with_target_query(self, tmp_path):
        """Test compare command with target query option."""
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
                        "--source-table", "users",
                        "--target-table", "users",
                        "--join-columns", "id",
                        "--target-query", "SELECT * FROM users WHERE status = 'active'",
                        "--output", str(tmp_path),
                    ],
                )

                assert mock_validator.called

    def test_compare_with_validation_error(self, tmp_path):
        """Test compare command handles ValidationError."""
        runner = CliRunner()

        env_vars = {
            "SNOWFLAKE_ACCOUNT": "test",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("pycaroline.cli.DataValidator") as mock_validator:
                from pycaroline.validator import ValidationError
                mock_validator.return_value.validate.side_effect = ValidationError("Validation failed")

                result = runner.invoke(
                    cli,
                    [
                        "compare",
                        "--source-type", "snowflake",
                        "--target-type", "bigquery",
                        "--source-table", "users",
                        "--target-table", "users",
                        "--join-columns", "id",
                        "--output", str(tmp_path),
                    ],
                )

                assert result.exit_code == 1
                assert "Validation failed" in result.output

    def test_compare_with_connection_error(self, tmp_path):
        """Test compare command handles ConnectionError."""
        runner = CliRunner()

        env_vars = {
            "SNOWFLAKE_ACCOUNT": "test",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_validator.return_value.validate.side_effect = ConnectionError("Connection failed")

                result = runner.invoke(
                    cli,
                    [
                        "compare",
                        "--source-type", "snowflake",
                        "--target-type", "bigquery",
                        "--source-table", "users",
                        "--target-table", "users",
                        "--join-columns", "id",
                        "--output", str(tmp_path),
                    ],
                )

                assert result.exit_code == 3
                assert "Connection failed" in result.output

    def test_compare_with_generic_exception(self, tmp_path):
        """Test compare command handles generic exceptions."""
        runner = CliRunner()

        env_vars = {
            "SNOWFLAKE_ACCOUNT": "test",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "pass",
            "GCP_PROJECT": "project",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("pycaroline.cli.DataValidator") as mock_validator:
                mock_validator.return_value.validate.side_effect = Exception("Unexpected error")

                result = runner.invoke(
                    cli,
                    [
                        "compare",
                        "--source-type", "snowflake",
                        "--target-type", "bigquery",
                        "--source-table", "users",
                        "--target-table", "users",
                        "--join-columns", "id",
                        "--output", str(tmp_path),
                    ],
                )

                assert result.exit_code == 1
                assert "Unexpected error" in result.output


class TestCliHelp:
    """Tests for CLI help output."""

    def test_main_help(self):
        """Test main CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Data validation CLI" in result.output

    def test_validate_help(self):
        """Test validate command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "--config" in result.output

    def test_compare_help(self):
        """Test compare command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--help"])

        assert result.exit_code == 0
        assert "--source-type" in result.output
        assert "--target-type" in result.output
