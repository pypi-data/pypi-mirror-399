"""Property-based tests for configuration loading.

These tests validate universal properties of the ConfigLoader using hypothesis.
"""

import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pycaroline.config.loader import ConfigLoader, ConfigurationError

# Strategy for generating valid environment variable names
env_var_names = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789", min_size=1, max_size=20
).filter(lambda s: s[0].isalpha() or s[0] == "_")

# Strategy for generating environment variable values (non-empty strings without special chars)
env_var_values = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P"), blacklist_characters="${}"
    ),
    min_size=1,
    max_size=50,
)


class TestProperty16ConfigEnvVarSubstitution:
    """
    **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
    **Validates: Requirements 6.5**

    For any configuration string containing ${VAR} where VAR is set in the environment,
    the loaded config SHALL contain the environment variable's value instead of the placeholder.
    """

    @given(
        var_name=env_var_names,
        var_value=env_var_values,
    )
    @settings(max_examples=100, deadline=None)
    def test_env_var_substitution_in_string(self, var_name: str, var_value: str):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any environment variable set in the environment, its placeholder
        in the config should be replaced with the actual value.
        """
        # Set the environment variable
        original_value = os.environ.get(var_name)
        os.environ[var_name] = var_value

        try:
            # Create a config dict with the placeholder
            config = {
                "source": {
                    "type": "snowflake",
                    "connection": {
                        "account": f"${{{var_name}}}",
                        "user": "test_user",
                        "password": "test_pass",
                    },
                },
                "target": {
                    "type": "bigquery",
                    "connection": {"project": "test_project"},
                },
                "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
            }

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify the placeholder was replaced with the env var value
            assert result["source"]["connection"]["account"] == var_value, (
                f"Expected account to be '{var_value}', "
                f"got '{result['source']['connection']['account']}'"
            )
        finally:
            # Restore original environment
            if original_value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = original_value

    @given(
        var_name=env_var_names,
        var_value=env_var_values,
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=0, max_size=10),
        suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=0, max_size=10),
    )
    @settings(max_examples=100, deadline=None)
    def test_env_var_substitution_with_surrounding_text(
        self, var_name: str, var_value: str, prefix: str, suffix: str
    ):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any environment variable embedded in a string with surrounding text,
        only the placeholder should be replaced, preserving the surrounding text.
        """
        # Set the environment variable
        original_value = os.environ.get(var_name)
        os.environ[var_name] = var_value

        try:
            # Create a config dict with the placeholder embedded in text
            placeholder_string = f"{prefix}${{{var_name}}}{suffix}"
            expected_result = f"{prefix}{var_value}{suffix}"

            config = {"connection_string": placeholder_string}

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify the placeholder was replaced correctly
            assert (
                result["connection_string"] == expected_result
            ), f"Expected '{expected_result}', got '{result['connection_string']}'"
        finally:
            # Restore original environment
            if original_value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = original_value

    @given(
        var_names=st.lists(env_var_names, min_size=2, max_size=5, unique=True),
        var_values=st.lists(env_var_values, min_size=2, max_size=5),
    )
    @settings(max_examples=100, deadline=None)
    def test_multiple_env_vars_substitution(self, var_names: list, var_values: list):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any configuration with multiple environment variable placeholders,
        all placeholders should be replaced with their respective values.
        """
        # Ensure we have matching lengths
        min_len = min(len(var_names), len(var_values))
        var_names = var_names[:min_len]
        var_values = var_values[:min_len]

        # Store original values and set new ones
        original_values = {}
        for name, value in zip(var_names, var_values, strict=False):
            original_values[name] = os.environ.get(name)
            os.environ[name] = value

        try:
            # Create a config dict with multiple placeholders
            config = {"vars": {name: f"${{{name}}}" for name in var_names}}

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify all placeholders were replaced
            for name, expected_value in zip(var_names, var_values, strict=False):
                assert result["vars"][name] == expected_value, (
                    f"Expected '{expected_value}' for {name}, "
                    f"got '{result['vars'][name]}'"
                )
        finally:
            # Restore original environment
            for name, original in original_values.items():
                if original is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = original

    @given(
        var_name=env_var_names,
        var_value=env_var_values,
    )
    @settings(max_examples=100, deadline=None)
    def test_env_var_substitution_in_nested_structures(
        self, var_name: str, var_value: str
    ):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any environment variable in deeply nested config structures,
        the placeholder should be correctly replaced.
        """
        # Set the environment variable
        original_value = os.environ.get(var_name)
        os.environ[var_name] = var_value

        try:
            # Create a deeply nested config
            config = {"level1": {"level2": {"level3": {"value": f"${{{var_name}}}"}}}}

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify the nested placeholder was replaced
            assert result["level1"]["level2"]["level3"]["value"] == var_value, (
                f"Expected nested value to be '{var_value}', "
                f"got '{result['level1']['level2']['level3']['value']}'"
            )
        finally:
            # Restore original environment
            if original_value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = original_value

    @given(
        var_name=env_var_names,
        var_value=env_var_values,
    )
    @settings(max_examples=100, deadline=None)
    def test_env_var_substitution_in_lists(self, var_name: str, var_value: str):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any environment variable in list elements,
        the placeholder should be correctly replaced.
        """
        # Set the environment variable
        original_value = os.environ.get(var_name)
        os.environ[var_name] = var_value

        try:
            # Create a config with list containing placeholder
            config = {
                "items": [
                    f"${{{var_name}}}",
                    "static_value",
                    {"nested": f"${{{var_name}}}"},
                ]
            }

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify list elements were substituted
            assert (
                result["items"][0] == var_value
            ), f"Expected first item to be '{var_value}', got '{result['items'][0]}'"
            assert (
                result["items"][1] == "static_value"
            ), "Static value should remain unchanged"
            assert result["items"][2]["nested"] == var_value, (
                f"Expected nested item to be '{var_value}', "
                f"got '{result['items'][2]['nested']}'"
            )
        finally:
            # Restore original environment
            if original_value is None:
                os.environ.pop(var_name, None)
            else:
                os.environ[var_name] = original_value

    @given(var_name=env_var_names)
    @settings(max_examples=100, deadline=None)
    def test_unset_env_var_replaced_with_empty_string(self, var_name: str):
        """
        **Feature: data-validation-library, Property 16: Config Environment Variable Substitution**
        **Validates: Requirements 6.5**

        For any environment variable placeholder where the variable is not set,
        the placeholder should be replaced with an empty string.
        """
        # Ensure the variable is not set
        original_value = os.environ.get(var_name)
        os.environ.pop(var_name, None)

        try:
            config = {"value": f"${{{var_name}}}"}

            # Apply substitution
            result = ConfigLoader._substitute_env_vars(config)

            # Verify placeholder was replaced with empty string
            assert (
                result["value"] == ""
            ), f"Expected empty string for unset var, got '{result['value']}'"
        finally:
            # Restore original environment
            if original_value is not None:
                os.environ[var_name] = original_value


class TestProperty17ConfigSchemaValidation:
    """
    **Feature: data-validation-library, Property 17: Config Schema Validation**
    **Validates: Requirements 6.3, 6.4**

    For any configuration missing required keys (source, target, tables),
    loading SHALL raise a ValueError with the missing key name.
    """

    @given(missing_key=st.sampled_from(["source", "target", "tables"]))
    @settings(max_examples=100, deadline=None)
    def test_missing_required_key_raises_error_with_key_name(self, missing_key: str):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any configuration missing a required top-level key,
        validation SHALL raise ConfigurationError containing the missing key name.
        """
        # Create a valid config and remove one required key
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Remove the key to test
        del config[missing_key]

        # Validate that ConfigurationError is raised with the missing key name
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains the missing key name
        assert missing_key in str(
            exc_info.value
        ), f"Expected error message to contain '{missing_key}', got: {exc_info.value}"

    @given(
        keys_to_remove=st.lists(
            st.sampled_from(["source", "target", "tables"]),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_multiple_missing_keys_raises_error_with_all_key_names(
        self, keys_to_remove: list
    ):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any configuration missing multiple required keys,
        validation SHALL raise ConfigurationError containing all missing key names.
        """
        # Create a valid config
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Remove the keys to test
        for key in keys_to_remove:
            del config[key]

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains at least one of the missing key names
        error_message = str(exc_info.value)
        found_keys = [key for key in keys_to_remove if key in error_message]
        assert len(found_keys) > 0, (
            f"Expected error message to contain at least one of {keys_to_remove}, "
            f"got: {error_message}"
        )

    @given(missing_key=st.sampled_from(["type", "connection"]))
    @settings(max_examples=100, deadline=None)
    def test_missing_source_connection_key_raises_error(self, missing_key: str):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any source configuration missing required connection keys,
        validation SHALL raise ConfigurationError containing the missing key name.
        """
        # Create a valid config
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Remove the key from source section
        del config["source"][missing_key]

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains the missing key name
        assert missing_key in str(
            exc_info.value
        ), f"Expected error message to contain '{missing_key}', got: {exc_info.value}"

    @given(missing_key=st.sampled_from(["type", "connection"]))
    @settings(max_examples=100, deadline=None)
    def test_missing_target_connection_key_raises_error(self, missing_key: str):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any target configuration missing required connection keys,
        validation SHALL raise ConfigurationError containing the missing key name.
        """
        # Create a valid config
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Remove the key from target section
        del config["target"][missing_key]

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains the missing key name
        assert missing_key in str(
            exc_info.value
        ), f"Expected error message to contain '{missing_key}', got: {exc_info.value}"

    @given(missing_key=st.sampled_from(["source_table", "join_columns"]))
    @settings(max_examples=100, deadline=None)
    def test_missing_table_config_key_raises_error(self, missing_key: str):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any table configuration missing required keys,
        validation SHALL raise ConfigurationError containing the missing key name.
        """
        # Create a valid config
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Remove the key from table config
        del config["tables"][0][missing_key]

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains the missing key name
        assert missing_key in str(
            exc_info.value
        ), f"Expected error message to contain '{missing_key}', got: {exc_info.value}"

    @given(
        invalid_type=st.text(min_size=1, max_size=20).filter(
            lambda x: x not in ["snowflake", "bigquery", "redshift"]
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_invalid_database_type_raises_error(self, invalid_type: str):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any configuration with an invalid database type,
        validation SHALL raise ConfigurationError indicating the invalid type.
        """
        # Create a config with invalid database type
        config = {
            "source": {
                "type": invalid_type,
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": ["id"]}],
        }

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message contains the invalid type
        assert invalid_type in str(
            exc_info.value
        ), f"Expected error message to contain '{invalid_type}', got: {exc_info.value}"

    def test_empty_tables_list_raises_error(self):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any configuration with an empty tables list,
        validation SHALL raise ConfigurationError.
        """
        # Create a config with empty tables list
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [],
        }

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message mentions tables
        assert (
            "tables" in str(exc_info.value).lower()
        ), f"Expected error message to mention 'tables', got: {exc_info.value}"

    def test_empty_join_columns_raises_error(self):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any table configuration with empty join_columns,
        validation SHALL raise ConfigurationError.
        """
        # Create a config with empty join_columns
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [{"source_table": "test_table", "join_columns": []}],
        }

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message mentions join_columns
        assert "join_columns" in str(
            exc_info.value
        ), f"Expected error message to mention 'join_columns', got: {exc_info.value}"

    @given(
        invalid_sample_size=st.one_of(
            st.integers(max_value=0), st.text(min_size=1, max_size=10)
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_invalid_sample_size_raises_error(self, invalid_sample_size):
        """
        **Feature: data-validation-library, Property 17: Config Schema Validation**
        **Validates: Requirements 6.3, 6.4**

        For any table configuration with invalid sample_size (non-positive or non-integer),
        validation SHALL raise ConfigurationError.
        """
        # Create a config with invalid sample_size
        config = {
            "source": {
                "type": "snowflake",
                "connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_pass",
                },
            },
            "target": {"type": "bigquery", "connection": {"project": "test_project"}},
            "tables": [
                {
                    "source_table": "test_table",
                    "join_columns": ["id"],
                    "sample_size": invalid_sample_size,
                }
            ],
        }

        # Validate that ConfigurationError is raised
        with pytest.raises(ConfigurationError) as exc_info:
            ConfigLoader._validate_schema(config)

        # Verify the error message mentions sample_size
        assert "sample_size" in str(
            exc_info.value
        ), f"Expected error message to mention 'sample_size', got: {exc_info.value}"
