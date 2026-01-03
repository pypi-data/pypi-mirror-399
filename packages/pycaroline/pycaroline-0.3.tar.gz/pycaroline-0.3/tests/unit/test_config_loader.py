"""Unit tests for ConfigLoader."""

import os
from pathlib import Path

import pytest
import yaml

from pycaroline.config.loader import ConfigLoader, ConfigurationError
from pycaroline.config.models import ValidationConfig
from pycaroline.connectors.factory import DatabaseType


class TestConfigLoaderLoad:
    """Tests for ConfigLoader.load method."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        config_dict = {
            "source": {
                "type": "snowflake",
                "connection": {"account": "test", "user": "user", "password": "pass"},
            },
            "target": {"type": "bigquery", "connection": {"project": "test-project"}},
            "tables": [{"source_table": "users", "join_columns": ["id"]}],
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        result = ConfigLoader.load(config_path)

        assert isinstance(result, ValidationConfig)
        assert result.source_db_type == DatabaseType.SNOWFLAKE
        assert result.target_db_type == DatabaseType.BIGQUERY
        assert len(result.tables) == 1

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML raises ConfigurationError."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(ConfigurationError, match="Invalid YAML"):
            ConfigLoader.load(config_path)

    def test_load_empty_file(self, tmp_path):
        """Test loading empty file raises ConfigurationError."""
        config_path = tmp_path / "config.yaml"
        config_path.touch()

        with pytest.raises(ConfigurationError, match="empty"):
            ConfigLoader.load(config_path)


class TestConfigLoaderEnvVarSubstitution:
    """Tests for environment variable substitution."""

    def test_substitute_single_env_var(self):
        """Test substituting a single environment variable."""
        os.environ["TEST_VAR"] = "test_value"
        config = {"key": "${TEST_VAR}"}

        result = ConfigLoader._substitute_env_vars(config)

        assert result["key"] == "test_value"
        del os.environ["TEST_VAR"]

    def test_substitute_multiple_env_vars(self):
        """Test substituting multiple environment variables."""
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "value2"
        config = {"key": "${VAR1}-${VAR2}"}

        result = ConfigLoader._substitute_env_vars(config)

        assert result["key"] == "value1-value2"
        del os.environ["VAR1"]
        del os.environ["VAR2"]

    def test_substitute_nested_dict(self):
        """Test substituting in nested dictionaries."""
        os.environ["NESTED_VAR"] = "nested_value"
        config = {"outer": {"inner": "${NESTED_VAR}"}}

        result = ConfigLoader._substitute_env_vars(config)

        assert result["outer"]["inner"] == "nested_value"
        del os.environ["NESTED_VAR"]

    def test_substitute_in_list(self):
        """Test substituting in lists."""
        os.environ["LIST_VAR"] = "list_value"
        config = {"items": ["${LIST_VAR}", "static"]}

        result = ConfigLoader._substitute_env_vars(config)

        assert result["items"][0] == "list_value"
        assert result["items"][1] == "static"
        del os.environ["LIST_VAR"]

    def test_unset_env_var_becomes_empty(self):
        """Test that unset environment variables become empty strings."""
        config = {"key": "${UNSET_VAR_12345}"}

        result = ConfigLoader._substitute_env_vars(config)

        assert result["key"] == ""


class TestConfigLoaderValidation:
    """Tests for configuration validation."""

    def test_missing_source_key(self):
        """Test that missing 'source' key raises error."""
        config = {
            "target": {"type": "bigquery", "connection": {}},
            "tables": [{"source_table": "t", "join_columns": ["id"]}],
        }

        with pytest.raises(ConfigurationError, match="source"):
            ConfigLoader._validate_schema(config)

    def test_missing_target_key(self):
        """Test that missing 'target' key raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "tables": [{"source_table": "t", "join_columns": ["id"]}],
        }

        with pytest.raises(ConfigurationError, match="target"):
            ConfigLoader._validate_schema(config)

    def test_missing_tables_key(self):
        """Test that missing 'tables' key raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
        }

        with pytest.raises(ConfigurationError, match="tables"):
            ConfigLoader._validate_schema(config)

    def test_invalid_database_type(self):
        """Test that invalid database type raises error."""
        config = {
            "source": {"type": "invalid_db", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
            "tables": [{"source_table": "t", "join_columns": ["id"]}],
        }

        with pytest.raises(ConfigurationError, match="Invalid database type"):
            ConfigLoader._validate_schema(config)

    def test_empty_tables_list(self):
        """Test that empty tables list raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
            "tables": [],
        }

        with pytest.raises(ConfigurationError, match="at least one"):
            ConfigLoader._validate_schema(config)

    def test_missing_join_columns(self):
        """Test that missing join_columns raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
            "tables": [{"source_table": "t"}],
        }

        with pytest.raises(ConfigurationError, match="join_columns"):
            ConfigLoader._validate_schema(config)

    def test_empty_join_columns(self):
        """Test that empty join_columns raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
            "tables": [{"source_table": "t", "join_columns": []}],
        }

        with pytest.raises(ConfigurationError, match="non-empty"):
            ConfigLoader._validate_schema(config)

    def test_invalid_sample_size(self):
        """Test that invalid sample_size raises error."""
        config = {
            "source": {"type": "snowflake", "connection": {}},
            "target": {"type": "bigquery", "connection": {}},
            "tables": [
                {"source_table": "t", "join_columns": ["id"], "sample_size": -1}
            ],
        }

        with pytest.raises(ConfigurationError, match="sample_size"):
            ConfigLoader._validate_schema(config)


class TestConfigLoaderParsing:
    """Tests for configuration parsing."""

    def test_parse_with_comparison_settings(self, tmp_path):
        """Test parsing configuration with comparison settings."""
        config_dict = {
            "source": {"type": "snowflake", "connection": {"account": "test"}},
            "target": {"type": "bigquery", "connection": {"project": "test"}},
            "tables": [{"source_table": "users", "join_columns": ["id"]}],
            "comparison": {
                "abs_tol": 0.01,
                "rel_tol": 0.001,
                "ignore_case": True,
                "ignore_spaces": False,
            },
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        result = ConfigLoader.load(config_path)

        assert result.comparison.abs_tol == 0.01
        assert result.comparison.rel_tol == 0.001
        assert result.comparison.ignore_case is True
        assert result.comparison.ignore_spaces is False

    def test_parse_with_custom_output_dir(self, tmp_path):
        """Test parsing configuration with custom output directory."""
        config_dict = {
            "source": {"type": "snowflake", "connection": {"account": "test"}},
            "target": {"type": "bigquery", "connection": {"project": "test"}},
            "tables": [{"source_table": "users", "join_columns": ["id"]}],
            "output_dir": "/custom/output",
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        result = ConfigLoader.load(config_path)

        assert result.output_dir == Path("/custom/output")

    def test_parse_table_with_all_options(self, tmp_path):
        """Test parsing table configuration with all options."""
        config_dict = {
            "source": {"type": "snowflake", "connection": {"account": "test"}},
            "target": {"type": "bigquery", "connection": {"project": "test"}},
            "tables": [
                {
                    "source_table": "users",
                    "target_table": "users_copy",
                    "source_schema": "prod",
                    "target_schema": "staging",
                    "join_columns": ["id", "email"],
                    "source_query": "SELECT * FROM users WHERE active = true",
                    "target_query": "SELECT * FROM users_copy",
                    "sample_size": 1000,
                }
            ],
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        result = ConfigLoader.load(config_path)
        table = result.tables[0]

        assert table.source_table == "users"
        assert table.target_table == "users_copy"
        assert table.source_schema == "prod"
        assert table.target_schema == "staging"
        assert table.join_columns == ["id", "email"]
        assert table.source_query == "SELECT * FROM users WHERE active = true"
        assert table.sample_size == 1000
