"""Configuration loader for data-recon.

This module provides functionality to load and validate configuration from YAML files,
with support for environment variable substitution.
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.factory import DatabaseType


class ConfigurationError(Exception):
    """Exception raised for configuration validation errors."""

    pass


class ConfigLoader:
    """Loads and validates configuration from YAML files.

    This class provides methods to:
    - Load YAML configuration files
    - Substitute environment variables in configuration values
    - Validate configuration schema
    - Parse configuration into ValidationConfig objects

    Example:
        config = ConfigLoader.load(Path("validation_config.yaml"))
        validator = DataValidator(config)
        results = validator.validate()
    """

    # Required top-level keys in configuration
    REQUIRED_KEYS = ["source", "target", "tables"]

    # Required keys for source/target sections
    REQUIRED_CONNECTION_KEYS = ["type", "connection"]

    # Required keys for each table configuration
    REQUIRED_TABLE_KEYS = ["source_table", "join_columns"]

    @staticmethod
    def load(config_path: Path) -> ValidationConfig:
        """Load configuration from a YAML file.

        Args:
            config_path: Path to the YAML configuration file.

        Returns:
            ValidationConfig object with parsed configuration.

        Raises:
            ConfigurationError: If the configuration file is invalid or missing required keys.
            FileNotFoundError: If the configuration file does not exist.
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {e}") from e

        if raw_config is None:
            raise ConfigurationError("Configuration file is empty")

        # Substitute environment variables
        raw_config = ConfigLoader._substitute_env_vars(raw_config)

        # Validate schema
        ConfigLoader._validate_schema(raw_config)

        # Convert to ValidationConfig
        return ConfigLoader._parse_config(raw_config)

    @staticmethod
    def _substitute_env_vars(config: Any) -> Any:
        """Replace ${VAR} patterns with environment variable values.

        Recursively processes the configuration dictionary, replacing any
        string values containing ${VAR} patterns with the corresponding
        environment variable values.

        Args:
            config: Configuration value (dict, list, or scalar).

        Returns:
            Configuration with environment variables substituted.
        """

        def replace(value: Any) -> Any:
            if isinstance(value, str):
                pattern = r"\$\{(\w+)\}"
                matches = re.findall(pattern, value)
                for var in matches:
                    env_value = os.environ.get(var, "")
                    value = value.replace(f"${{{var}}}", env_value)
                return value
            elif isinstance(value, dict):
                return {k: replace(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace(v) for v in value]
            return value

        return replace(config)

    @staticmethod
    def _validate_schema(config: dict[str, Any]) -> None:
        """Validate configuration schema.

        Checks that all required keys are present and have valid values.

        Args:
            config: Raw configuration dictionary.

        Raises:
            ConfigurationError: If required keys are missing or values are invalid.
        """
        # Check required top-level keys
        missing_keys = []
        for key in ConfigLoader.REQUIRED_KEYS:
            if key not in config:
                missing_keys.append(key)

        if missing_keys:
            raise ConfigurationError(
                f"Missing required config key(s): {', '.join(missing_keys)}"
            )

        # Validate source section
        ConfigLoader._validate_connection_section(config["source"], "source")

        # Validate target section
        ConfigLoader._validate_connection_section(config["target"], "target")

        # Validate tables section
        if not isinstance(config["tables"], list):
            raise ConfigurationError("'tables' must be a list")

        if len(config["tables"]) == 0:
            raise ConfigurationError(
                "'tables' must contain at least one table configuration"
            )

        for i, table in enumerate(config["tables"]):
            ConfigLoader._validate_table_config(table, i)

    @staticmethod
    def _validate_connection_section(section: dict[str, Any], name: str) -> None:
        """Validate a connection section (source or target).

        Args:
            section: The connection section dictionary.
            name: Name of the section for error messages.

        Raises:
            ConfigurationError: If required keys are missing or values are invalid.
        """
        if not isinstance(section, dict):
            raise ConfigurationError(f"'{name}' must be a dictionary")

        for key in ConfigLoader.REQUIRED_CONNECTION_KEYS:
            if key not in section:
                raise ConfigurationError(
                    f"Missing required key '{key}' in '{name}' section"
                )

        # Validate database type
        db_type = section["type"]
        valid_types = [t.value for t in DatabaseType]
        if db_type not in valid_types:
            raise ConfigurationError(
                f"Invalid database type '{db_type}' in '{name}' section. "
                f"Valid types: {valid_types}"
            )

        # Validate connection is a dictionary
        if not isinstance(section["connection"], dict):
            raise ConfigurationError(f"'{name}.connection' must be a dictionary")

    @staticmethod
    def _validate_table_config(table: dict[str, Any], index: int) -> None:
        """Validate a table configuration.

        Args:
            table: The table configuration dictionary.
            index: Index of the table in the tables list for error messages.

        Raises:
            ConfigurationError: If required keys are missing or values are invalid.
        """
        if not isinstance(table, dict):
            raise ConfigurationError(
                f"Table configuration at index {index} must be a dictionary"
            )

        for key in ConfigLoader.REQUIRED_TABLE_KEYS:
            if key not in table:
                raise ConfigurationError(
                    f"Missing required key '{key}' in table configuration at index {index}"
                )

        # Validate join_columns is a non-empty list
        join_columns = table["join_columns"]
        if not isinstance(join_columns, list) or len(join_columns) == 0:
            raise ConfigurationError(
                f"'join_columns' must be a non-empty list in table configuration at index {index}"
            )

        # Validate sample_size if present
        if "sample_size" in table:
            sample_size = table["sample_size"]
            if not isinstance(sample_size, int) or sample_size <= 0:
                raise ConfigurationError(
                    f"'sample_size' must be a positive integer in table configuration at index {index}"
                )

    @staticmethod
    def _parse_config(raw_config: dict[str, Any]) -> ValidationConfig:
        """Parse raw config dict into ValidationConfig.

        Args:
            raw_config: Validated raw configuration dictionary.

        Returns:
            ValidationConfig object.
        """
        # Parse tables
        tables = [
            TableConfig(
                source_table=t["source_table"],
                target_table=t.get("target_table"),
                source_schema=t.get("source_schema"),
                target_schema=t.get("target_schema"),
                join_columns=t["join_columns"],
                source_query=t.get("source_query"),
                target_query=t.get("target_query"),
                sample_size=t.get("sample_size"),
            )
            for t in raw_config["tables"]
        ]

        # Parse comparison settings if present
        comparison_config = raw_config.get("comparison", {})
        comparison = ComparisonSettings(
            abs_tol=comparison_config.get("abs_tol", 0.0001),
            rel_tol=comparison_config.get("rel_tol", 0.0),
            ignore_case=comparison_config.get("ignore_case", False),
            ignore_spaces=comparison_config.get("ignore_spaces", True),
        )

        return ValidationConfig(
            source_db_type=DatabaseType(raw_config["source"]["type"]),
            source_connection=raw_config["source"]["connection"],
            target_db_type=DatabaseType(raw_config["target"]["type"]),
            target_connection=raw_config["target"]["connection"],
            tables=tables,
            output_dir=Path(raw_config.get("output_dir", "./validation_results")),
            comparison=comparison,
        )
