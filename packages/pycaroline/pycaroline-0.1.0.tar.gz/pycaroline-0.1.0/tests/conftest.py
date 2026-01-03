"""Pytest configuration and fixtures for pycaroline tests."""

from pathlib import Path
from typing import Any

import polars as pl
import pytest


@pytest.fixture
def sample_source_df() -> pl.DataFrame:
    """Create a sample source DataFrame for testing."""
    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "value": [100.0, 200.0, 300.0, 400.0, 500.0],
        }
    )


@pytest.fixture
def sample_target_df() -> pl.DataFrame:
    """Create a sample target DataFrame for testing."""
    return pl.DataFrame(
        {
            "id": [1, 2, 3, 4, 6],
            "name": ["Alice", "Bob", "Charlie", "David", "Frank"],
            "value": [100.0, 200.0, 350.0, 400.0, 600.0],
        }
    )


@pytest.fixture
def sample_config_dict() -> dict[str, Any]:
    """Create a sample configuration dictionary for testing."""
    return {
        "source": {
            "type": "snowflake",
            "connection": {
                "account": "test_account",
                "user": "test_user",
                "password": "test_password",
                "warehouse": "test_warehouse",
                "database": "test_db",
            },
        },
        "target": {
            "type": "bigquery",
            "connection": {
                "project": "test_project",
                "dataset": "test_dataset",
            },
        },
        "tables": [
            {
                "source_table": "customers",
                "target_table": "customers",
                "join_columns": ["customer_id"],
            },
        ],
        "output_dir": "./test_results",
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config_dict) -> Path:
    """Create a temporary YAML config file for testing."""
    import yaml

    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f)
    return config_path
