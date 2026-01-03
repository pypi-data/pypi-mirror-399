"""Extended unit tests for ConfigLoader to improve coverage.

Tests for edge cases, validation errors, and environment variable substitution.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pycaroline.config.loader import ConfigLoader, ConfigurationError


class TestConfigLoaderEnvVarSubstitution:
    """Tests for environment variable substitution."""

    def test_substitute_single_env_var(self):
        """Test substituting a single environment variable."""
        config = {"password": "${MY_PASSWORD}"}

        with patch.dict(os.environ, {"MY_PASSWORD": "secret123"}):
            result = ConfigLoader._substitute_env_vars(config)

        assert result["password"] == "secret123"

    def test_substitute_multiple_env_vars_in_string(self):
        """Test substituting multiple env vars in one string."""
        config = {"connection_string": "${HOST}:${PORT}"}

        with patch.dict(os.environ, {"HOST": "localhost", "PORT": "5432"}):
            result = ConfigLoader._substitute_env_vars(config)

        assert result["connection_string"] == "localhost:5432"

    def test_substitute_missing_env_var_becomes_empty(self):
        """Test that missing env var becomes empty string."""
        config = {"value": "${NONEXISTENT_VAR}"}

        with patch.dict(os.environ, {}, clear=True):
            result = ConfigLoader._substitute_env_vars(config)

        assert result["value"] == ""

    def test_substitute_in_nested_dict(self):
        """Test substitution in nested dictionaries."""
        config = {"source": {"connection": {"password": "${DB_PASSWORD}"}}}

        with patch.dict(os.environ, {"DB_PASSWORD": "nested_secret"}):
            result = ConfigLoader._substitute_env_vars(config)

        assert result["source"]["connection"]["password"] == "nested_secret"

    def test_substitute_in_list(self):
        """Test substitution in lists."""
        config = {"hosts": ["${HOST1}", "${HOST2}"]}

        with patch.dict(os.environ, {"HOST1": "host1.com", "HOST2": "host2.com"}):
            result = ConfigLoader._substitute_env_vars(config)

        assert result["hosts"] == ["host1.com", "host2.com"]

    def test_substitute_preserves_non_string_values(self):
        """Test that non-string values are preserved."""
        config = {
            "port": 5432,
            "enabled": True,
            "ratio": 0.5,
            "items": None,
        }

        result = ConfigLoader._substitute_env_vars(config)

        assert result["port"] == 5432
        assert result["enabled"] is True
        assert result["ratio"] == 0.5
        assert result["items"] is None


class TestConfigLoaderValidation:
    """Tests for configuration validation."""

    def test_validate_missing_source_key(self, tmp_path):
        """Test validation fails when source key is missing."""
        config_content = """
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

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Missing required config key" in str(exc_info.value)
        assert "source" in str(exc_info.value)

    def test_validate_missing_target_key(self, tmp_path):
        """Test validation fails when target key is missing."""
        config_content = """
source:
  type: snowflake
  connection:
    account: test
tables:
  - source_table: users
    join_columns: [id]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Missing required config key" in str(exc_info.value)
        assert "target" in str(exc_info.value)

    def test_validate_missing_tables_key(self, tmp_path):
        """Test validation fails when tables key is missing."""
        config_content = """
source:
  type: snowflake
  connection:
    account: test
target:
  type: bigquery
  connection:
    project: test
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Missing required config key" in str(exc_info.value)
        assert "tables" in str(exc_info.value)

    def test_validate_source_not_dict(self, tmp_path):
        """Test validation fails when source is not a dict."""
        config_content = """
source: "not a dict"
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

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'source' must be a dictionary" in str(exc_info.value)

    def test_validate_missing_type_in_source(self, tmp_path):
        """Test validation fails when type is missing in source."""
        config_content = """
source:
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

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Missing required key 'type'" in str(exc_info.value)

    def test_validate_invalid_database_type(self, tmp_path):
        """Test validation fails for invalid database type."""
        config_content = """
source:
  type: invalid_db
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

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Invalid database type" in str(exc_info.value)

    def test_validate_connection_not_dict(self, tmp_path):
        """Test validation fails when connection is not a dict."""
        config_content = """
source:
  type: snowflake
  connection: "not a dict"
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

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'source.connection' must be a dictionary" in str(exc_info.value)

    def test_validate_tables_not_list(self, tmp_path):
        """Test validation fails when tables is not a list."""
        config_content = """
source:
  type: snowflake
  connection:
    account: test
target:
  type: bigquery
  connection:
    project: test
tables: "not a list"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'tables' must be a list" in str(exc_info.value)

    def test_validate_empty_tables_list(self, tmp_path):
        """Test validation fails when tables list is empty."""
        config_content = """
source:
  type: snowflake
  connection:
    account: test
target:
  type: bigquery
  connection:
    project: test
tables: []
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'tables' must contain at least one" in str(exc_info.value)

    def test_validate_table_not_dict(self, tmp_path):
        """Test validation fails when table config is not a dict."""
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
  - "not a dict"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "must be a dictionary" in str(exc_info.value)

    def test_validate_missing_source_table(self, tmp_path):
        """Test validation fails when source_table is missing."""
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
  - join_columns: [id]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Missing required key 'source_table'" in str(exc_info.value)

    def test_validate_empty_join_columns(self, tmp_path):
        """Test validation fails when join_columns is empty."""
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
    join_columns: []
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'join_columns' must be a non-empty list" in str(exc_info.value)

    def test_validate_invalid_sample_size(self, tmp_path):
        """Test validation fails for invalid sample_size."""
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
    sample_size: -1
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "'sample_size' must be a positive integer" in str(exc_info.value)


class TestConfigLoaderFileHandling:
    """Tests for file handling."""

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML raises ConfigurationError."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Invalid YAML syntax" in str(exc_info.value)

    def test_load_empty_file(self, tmp_path):
        """Test loading empty file raises ConfigurationError."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader.load(config_file)

        assert "Configuration file is empty" in str(exc_info.value)


class TestConfigLoaderParsing:
    """Tests for configuration parsing."""

    def test_parse_with_comparison_settings(self, tmp_path):
        """Test parsing config with comparison settings."""
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
comparison:
  abs_tol: 0.01
  rel_tol: 0.001
  ignore_case: true
  ignore_spaces: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        config = ConfigLoader.load(config_file)

        assert config.comparison.abs_tol == 0.01
        assert config.comparison.rel_tol == 0.001
        assert config.comparison.ignore_case is True
        assert config.comparison.ignore_spaces is False

    def test_parse_with_custom_output_dir(self, tmp_path):
        """Test parsing config with custom output directory."""
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
output_dir: /custom/output/path
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        config = ConfigLoader.load(config_file)

        assert config.output_dir == Path("/custom/output/path")

    def test_parse_table_with_all_options(self, tmp_path):
        """Test parsing table config with all optional fields."""
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
    target_table: customers
    source_schema: prod
    target_schema: staging
    join_columns: [id, email]
    source_query: "SELECT * FROM users WHERE active = true"
    target_query: "SELECT * FROM customers WHERE status = 'active'"
    sample_size: 1000
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        config = ConfigLoader.load(config_file)
        table = config.tables[0]

        assert table.source_table == "users"
        assert table.target_table == "customers"
        assert table.source_schema == "prod"
        assert table.target_schema == "staging"
        assert table.join_columns == ["id", "email"]
        assert "SELECT * FROM users" in table.source_query
        assert "SELECT * FROM customers" in table.target_query
        assert table.sample_size == 1000
