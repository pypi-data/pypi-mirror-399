"""Snowflake database connector.

This module provides a connector for Snowflake databases that extends BaseConnector.
"""

import os

import polars as pl

from pycaroline.connectors.base import BaseConnector, ConnectionError, QueryError
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType

try:
    import snowflake.connector
    from snowflake.connector.errors import DatabaseError, ProgrammingError

    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False


def _load_toml_config(config_path: str) -> dict:
    """Load configuration from a TOML file.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        Dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
    """
    import tomllib

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        return tomllib.load(f)


@ConnectorFactory.register(DatabaseType.SNOWFLAKE)
class SnowflakeConnector(BaseConnector):
    """Snowflake database connector.

    Supports multiple authentication methods:
    - Password authentication
    - Private key authentication
    - OAuth token authentication
    - SSO (externalbrowser) authentication

    Configuration can be provided via:
    - Direct parameters
    - Environment variables (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, etc.)
    - TOML configuration file

    Example:
        # Using environment variables
        with SnowflakeConnector() as conn:
            df = conn.query("SELECT * FROM my_table")

        # Using direct parameters
        connector = SnowflakeConnector(
            account="my_account",
            user="my_user",
            password="my_password",
            warehouse="my_warehouse",
            database="my_database"
        )

        # Using config file
        connector = SnowflakeConnector(config_path="~/.snowflake/connections.toml")
    """

    def __init__(
        self,
        account: str | None = None,
        user: str | None = None,
        password: str | None = None,
        private_key_path: str | None = None,
        private_key_passphrase: str | None = None,
        token: str | None = None,
        authenticator: str | None = None,
        warehouse: str | None = None,
        database: str | None = None,
        schema: str | None = None,
        role: str | None = None,
        config_path: str | None = None,
        connection_name: str = "default",
    ):
        """Initialize the Snowflake connector.

        Args:
            account: Snowflake account identifier.
            user: Username for authentication.
            password: Password for basic authentication.
            private_key_path: Path to private key file for key-pair auth.
            private_key_passphrase: Passphrase for encrypted private key.
            token: OAuth token for token-based authentication.
            authenticator: Authentication method ('externalbrowser' for SSO, 'oauth').
            warehouse: Default warehouse to use.
            database: Default database to use.
            schema: Default schema to use.
            role: Role to assume after connection.
            config_path: Path to TOML configuration file.
            connection_name: Name of connection profile in config file.
        """
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError(
                "snowflake-connector-python is required for SnowflakeConnector. "
                "Install it with: pip install data-recon[snowflake]"
            )

        self._connection = None
        self._config_path = config_path
        self._connection_name = connection_name

        # Load config from file if provided
        file_config = {}
        if config_path:
            expanded_path = os.path.expanduser(config_path)
            if os.path.exists(expanded_path):
                full_config = _load_toml_config(expanded_path)
                file_config = full_config.get(connection_name, {})

        # Priority: direct params > env vars > config file
        self._account = (
            account or os.environ.get("SNOWFLAKE_ACCOUNT") or file_config.get("account")
        )
        self._user = user or os.environ.get("SNOWFLAKE_USER") or file_config.get("user")
        self._password = (
            password
            or os.environ.get("SNOWFLAKE_PASSWORD")
            or file_config.get("password")
        )
        self._private_key_path = (
            private_key_path
            or os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH")
            or file_config.get("private_key_path")
        )
        self._private_key_passphrase = (
            private_key_passphrase
            or os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
            or file_config.get("private_key_passphrase")
        )
        self._token = (
            token or os.environ.get("SNOWFLAKE_TOKEN") or file_config.get("token")
        )
        self._authenticator = (
            authenticator
            or os.environ.get("SNOWFLAKE_AUTHENTICATOR")
            or file_config.get("authenticator")
        )
        self._warehouse = (
            warehouse
            or os.environ.get("SNOWFLAKE_WAREHOUSE")
            or file_config.get("warehouse")
        )
        self._database = (
            database
            or os.environ.get("SNOWFLAKE_DATABASE")
            or file_config.get("database")
        )
        self._schema = (
            schema or os.environ.get("SNOWFLAKE_SCHEMA") or file_config.get("schema")
        )
        self._role = role or os.environ.get("SNOWFLAKE_ROLE") or file_config.get("role")

    def connect(self) -> None:
        """Establish connection to Snowflake.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        if not self._account:
            raise ConnectionError(
                "Snowflake account is required. Set SNOWFLAKE_ACCOUNT environment "
                "variable or provide 'account' parameter."
            )
        if not self._user:
            raise ConnectionError(
                "Snowflake user is required. Set SNOWFLAKE_USER environment "
                "variable or provide 'user' parameter."
            )

        connection_params = {
            "account": self._account,
            "user": self._user,
        }

        # Add optional parameters
        if self._warehouse:
            connection_params["warehouse"] = self._warehouse
        if self._database:
            connection_params["database"] = self._database
        if self._schema:
            connection_params["schema"] = self._schema
        if self._role:
            connection_params["role"] = self._role

        # Handle authentication
        auth_params = self._get_auth_params()
        connection_params.update(auth_params)

        try:
            self._connection = snowflake.connector.connect(**connection_params)
        except (DatabaseError, ProgrammingError) as e:
            raise ConnectionError(
                f"Failed to connect to Snowflake account '{self._account}' "
                f"as user '{self._user}': {e}"
            ) from e

    def _get_auth_params(self) -> dict:
        """Get authentication parameters based on configured auth method.

        Returns:
            Dictionary of authentication parameters.

        Raises:
            ConnectionError: If no valid authentication method is configured.
        """
        # SSO authentication
        if self._authenticator == "externalbrowser":
            return {"authenticator": "externalbrowser"}

        # OAuth authentication
        if self._authenticator == "oauth" and self._token:
            return {"authenticator": "oauth", "token": self._token}

        # Private key authentication
        if self._private_key_path:
            private_key = self._load_private_key()
            return {"private_key": private_key}

        # Password authentication
        if self._password:
            return {"password": self._password}

        raise ConnectionError(
            "No valid authentication method configured. Provide one of: "
            "password, private_key_path, token (with authenticator='oauth'), "
            "or set authenticator='externalbrowser' for SSO."
        )

    def _load_private_key(self) -> bytes:
        """Load and convert private key to DER format.

        Returns:
            Private key in DER format.

        Raises:
            ConnectionError: If private key cannot be loaded.
        """
        from cryptography.hazmat.primitives import serialization

        if self._private_key_path is None:
            raise ConnectionError("Private key path is not set")

        expanded_path = os.path.expanduser(self._private_key_path)
        if not os.path.exists(expanded_path):
            raise ConnectionError(f"Private key file not found: {expanded_path}")

        passphrase: bytes | None = None
        if self._private_key_passphrase:
            passphrase = self._private_key_passphrase.encode()

        try:
            with open(expanded_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=passphrase,
                )
            return private_key.private_bytes(  # type: ignore[return-value, no-any-return]
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to load private key from '{expanded_path}': {e}"
            ) from e

    def disconnect(self) -> None:
        """Close the Snowflake connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL query and return results as Polars DataFrame.

        Args:
            sql: The SQL query to execute.

        Returns:
            Polars DataFrame containing the query results.

        Raises:
            QueryError: If the query fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Query: {sql}")

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            # Fetch as pandas first, then convert to polars
            pandas_df = cursor.fetch_pandas_all()
            return pl.from_pandas(pandas_df)
        except (DatabaseError, ProgrammingError) as e:
            raise QueryError(f"Query failed: {sql}\nError: {e}") from e

    def execute(self, sql: str) -> None:
        """Execute SQL statement (DDL/DML).

        Args:
            sql: The SQL statement to execute.

        Raises:
            QueryError: If the statement fails to execute.
        """
        if self._connection is None:
            raise QueryError(f"Not connected to database. Statement: {sql}")

        try:
            for cursor in self._connection.execute_string(sql):
                cursor.close()
        except (DatabaseError, ProgrammingError) as e:
            raise QueryError(f"Statement failed: {sql}\nError: {e}") from e
