"""Additional tests for SnowflakeConnector to improve coverage.

Tests for TOML config loading, private key auth, and edge cases.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import tempfile

import pytest


class TestSnowflakeConnectorTOMLConfig:
    """Tests for TOML configuration file loading."""

    def test_load_toml_config_success(self, tmp_path):
        """Test loading valid TOML config file."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import _load_toml_config

            config_content = """
[default]
account = "test_account"
user = "test_user"
password = "test_password"
"""
            config_file = tmp_path / "config.toml"
            config_file.write_text(config_content)

            result = _load_toml_config(str(config_file))

            assert result["default"]["account"] == "test_account"
            assert result["default"]["user"] == "test_user"

    def test_load_toml_config_file_not_found(self):
        """Test loading nonexistent TOML config file."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import _load_toml_config

            with pytest.raises(FileNotFoundError):
                _load_toml_config("/nonexistent/config.toml")

    def test_connector_with_config_file(self, tmp_path):
        """Test connector initialization with config file."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            config_content = """
[default]
account = "config_account"
user = "config_user"
password = "config_password"
warehouse = "config_warehouse"
"""
            config_file = tmp_path / "connections.toml"
            config_file.write_text(config_content)

            connector = SnowflakeConnector(config_path=str(config_file))

            assert connector._account == "config_account"
            assert connector._user == "config_user"
            assert connector._password == "config_password"
            assert connector._warehouse == "config_warehouse"

    def test_connector_direct_params_override_config(self, tmp_path):
        """Test that direct parameters override config file values."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            config_content = """
[default]
account = "config_account"
user = "config_user"
"""
            config_file = tmp_path / "connections.toml"
            config_file.write_text(config_content)

            connector = SnowflakeConnector(
                config_path=str(config_file),
                account="override_account",
            )

            assert connector._account == "override_account"
            assert connector._user == "config_user"

    def test_connector_with_custom_connection_name(self, tmp_path):
        """Test connector with custom connection name in config."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            config_content = """
[default]
account = "default_account"

[production]
account = "prod_account"
user = "prod_user"
"""
            config_file = tmp_path / "connections.toml"
            config_file.write_text(config_content)

            connector = SnowflakeConnector(
                config_path=str(config_file),
                connection_name="production",
                password="test",
            )

            assert connector._account == "prod_account"
            assert connector._user == "prod_user"


class TestSnowflakeConnectorPrivateKeyAuth:
    """Tests for private key authentication."""

    def test_private_key_with_passphrase(self, tmp_path):
        """Test private key loading with passphrase."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric import rsa

                # Generate a test private key
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )

                # Save with passphrase
                passphrase = b"test_passphrase"
                pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
                )

                key_file = tmp_path / "key.pem"
                key_file.write_bytes(pem)

                connector = SnowflakeConnector(
                    account="test_account",
                    user="test_user",
                    private_key_path=str(key_file),
                    private_key_passphrase="test_passphrase",
                )

                connector.connect()

                # Verify private key was used
                call_kwargs = mock_sf.connector.connect.call_args[1]
                assert "private_key" in call_kwargs


class TestSnowflakeConnectorEnvVars:
    """Tests for environment variable configuration."""

    def test_connector_uses_env_vars(self):
        """Test connector uses environment variables."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            from pycaroline.connectors.snowflake import SnowflakeConnector

            env_vars = {
                "SNOWFLAKE_ACCOUNT": "env_account",
                "SNOWFLAKE_USER": "env_user",
                "SNOWFLAKE_PASSWORD": "env_password",
                "SNOWFLAKE_WAREHOUSE": "env_warehouse",
                "SNOWFLAKE_DATABASE": "env_database",
                "SNOWFLAKE_SCHEMA": "env_schema",
                "SNOWFLAKE_ROLE": "env_role",
            }

            with patch.dict(os.environ, env_vars, clear=False):
                connector = SnowflakeConnector()

                assert connector._account == "env_account"
                assert connector._user == "env_user"
                assert connector._password == "env_password"
                assert connector._warehouse == "env_warehouse"
                assert connector._database == "env_database"
                assert connector._schema == "env_schema"
                assert connector._role == "env_role"


class TestSnowflakeConnectorImportError:
    """Tests for import error handling."""

    def test_connector_raises_import_error_when_not_available(self):
        """Test that connector raises ImportError when snowflake not installed."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", False):
            # Need to reload the module to trigger the check
            import importlib
            import pycaroline.connectors.snowflake as sf_module

            # Save original value
            original_available = sf_module.SNOWFLAKE_AVAILABLE

            try:
                sf_module.SNOWFLAKE_AVAILABLE = False

                with pytest.raises(ImportError) as exc_info:
                    sf_module.SnowflakeConnector(
                        account="test",
                        user="test",
                        password="test",
                    )

                assert "snowflake-connector-python is required" in str(exc_info.value)
            finally:
                sf_module.SNOWFLAKE_AVAILABLE = original_available


class TestSnowflakeConnectorConnectionParams:
    """Tests for connection parameter handling."""

    def test_connect_with_all_optional_params(self):
        """Test connection with all optional parameters."""
        with patch("pycaroline.connectors.snowflake.SNOWFLAKE_AVAILABLE", True):
            with patch("pycaroline.connectors.snowflake.snowflake") as mock_sf:
                from pycaroline.connectors.snowflake import SnowflakeConnector

                connector = SnowflakeConnector(
                    account="test_account",
                    user="test_user",
                    password="test_password",
                    warehouse="test_warehouse",
                    database="test_database",
                    schema="test_schema",
                    role="test_role",
                )

                connector.connect()

                call_kwargs = mock_sf.connector.connect.call_args[1]
                assert call_kwargs["account"] == "test_account"
                assert call_kwargs["user"] == "test_user"
                assert call_kwargs["password"] == "test_password"
                assert call_kwargs["warehouse"] == "test_warehouse"
                assert call_kwargs["database"] == "test_database"
                assert call_kwargs["schema"] == "test_schema"
                assert call_kwargs["role"] == "test_role"
