"""Command-line interface for PyCaroline.

This module provides CLI commands for running data validations from the command line,
supporting both configuration file-based validation and ad-hoc table comparisons.
"""

import logging
from pathlib import Path

import click

from pycaroline.config.loader import ConfigLoader, ConfigurationError
from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.factory import DatabaseType
from pycaroline.validator import DataValidator, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_CONFIG_ERROR = 2
EXIT_CONNECTION_ERROR = 3


@click.group()
@click.version_option(prog_name="pycaroline")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose output (debug logging).",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Data validation CLI for comparing tables across databases.

    This tool helps validate data migrations by comparing tables between
    source and target databases (Snowflake, BigQuery, Redshift).

    Use 'pycaroline validate' for configuration file-based validation,
    or 'pycaroline compare' for quick ad-hoc comparisons.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to YAML configuration file.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output directory for reports (overrides config file setting).",
)
@click.pass_context
def validate(ctx: click.Context, config: str, output: str | None) -> None:
    """Run data validation based on configuration file.

    Reads validation settings from a YAML configuration file and runs
    comparisons for all configured tables. Generates reports in JSON,
    CSV, and HTML formats.

    Example:
        data-recon validate --config validation_config.yaml
        data-recon validate -c config.yaml -o ./reports
    """
    try:
        config_path = Path(config)
        logger.info(f"Loading configuration from: {config_path}")
        validation_config = ConfigLoader.load(config_path)

        # Override output directory if specified
        if output:
            validation_config.output_dir = Path(output)
            logger.info(f"Output directory overridden to: {output}")

        logger.info(f"Starting validation of {len(validation_config.tables)} table(s)")

        validator = DataValidator(validation_config)
        results = validator.validate()

        # Print summary
        click.echo("\n" + "=" * 60)
        click.echo("VALIDATION SUMMARY")
        click.echo("=" * 60)

        all_passed = True
        for table, result in results.items():
            match_pct = result.matching_rows / max(result.source_row_count, 1) * 100
            status = "✓" if match_pct == 100 else "✗"
            if match_pct < 100:
                all_passed = False

            click.echo(
                f"{status} {table}: {match_pct:.2f}% match "
                f"({result.matching_rows}/{result.source_row_count} rows)"
            )

            if (
                result.rows_only_in_source is not None
                and len(result.rows_only_in_source) > 0
            ):
                click.echo(
                    f"  - Rows only in source: {len(result.rows_only_in_source)}"
                )
            if (
                result.rows_only_in_target is not None
                and len(result.rows_only_in_target) > 0
            ):
                click.echo(
                    f"  - Rows only in target: {len(result.rows_only_in_target)}"
                )
            if result.mismatched_rows > 0:
                click.echo(f"  - Mismatched rows: {result.mismatched_rows}")

        click.echo("=" * 60)
        click.echo(f"Reports saved to: {validation_config.output_dir}")

        if all_passed:
            click.echo("\n✓ All validations passed!")
            ctx.exit(EXIT_SUCCESS)
        else:
            click.echo("\n✗ Some validations failed. Check reports for details.")
            ctx.exit(EXIT_VALIDATION_FAILED)

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        click.echo(f"Error: Configuration error - {e}", err=True)
        ctx.exit(EXIT_CONFIG_ERROR)

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        click.echo(f"Error: Connection failed - {e}", err=True)
        ctx.exit(EXIT_CONNECTION_ERROR)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        click.echo(f"Error: Validation failed - {e}", err=True)
        ctx.exit(EXIT_VALIDATION_FAILED)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(EXIT_VALIDATION_FAILED)


@cli.command()
@click.option(
    "--source-type",
    type=click.Choice(["snowflake", "bigquery", "redshift"], case_sensitive=False),
    required=True,
    help="Source database type.",
)
@click.option(
    "--target-type",
    type=click.Choice(["snowflake", "bigquery", "redshift"], case_sensitive=False),
    required=True,
    help="Target database type.",
)
@click.option(
    "--source-table",
    required=True,
    help="Source table name (format: schema.table or just table).",
)
@click.option(
    "--target-table",
    required=True,
    help="Target table name (format: schema.table or just table).",
)
@click.option(
    "--join-columns",
    required=True,
    help="Comma-separated list of join columns for matching rows.",
)
@click.option(
    "--source-query",
    default=None,
    help="Custom SQL query for source data (overrides --source-table).",
)
@click.option(
    "--target-query",
    default=None,
    help="Custom SQL query for target data (overrides --target-table).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="./validation_results",
    help="Output directory for reports.",
)
@click.option(
    "--tolerance",
    type=float,
    default=0.0001,
    help="Absolute tolerance for numeric comparisons.",
)
@click.option(
    "--ignore-case",
    is_flag=True,
    default=False,
    help="Ignore case when comparing strings.",
)
@click.option(
    "--ignore-spaces/--no-ignore-spaces",
    default=True,
    help="Ignore leading/trailing whitespace in strings.",
)
@click.option(
    "--sample-size",
    type=int,
    default=None,
    help="Limit number of rows to compare (for large tables).",
)
@click.pass_context
def compare(
    ctx: click.Context,
    source_type: str,
    target_type: str,
    source_table: str,
    target_table: str,
    join_columns: str,
    source_query: str | None,
    target_query: str | None,
    output: str,
    tolerance: float,
    ignore_case: bool,
    ignore_spaces: bool,
    sample_size: int | None,
) -> None:
    """Quick comparison of two tables.

    Performs an ad-hoc comparison between source and target tables without
    requiring a configuration file. Connection parameters are read from
    environment variables.

    Environment variables for Snowflake:
        SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
        SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA

    Environment variables for BigQuery:
        GOOGLE_APPLICATION_CREDENTIALS, GCP_PROJECT, BQ_DATASET

    Environment variables for Redshift:
        REDSHIFT_HOST, REDSHIFT_PORT, REDSHIFT_DATABASE,
        REDSHIFT_USER, REDSHIFT_PASSWORD

    Example:
        data-recon compare \\
            --source-type snowflake \\
            --target-type bigquery \\
            --source-table my_schema.customers \\
            --target-table my_dataset.customers \\
            --join-columns customer_id
    """

    try:
        # Parse join columns
        join_cols = [col.strip() for col in join_columns.split(",")]

        # Parse table names (handle schema.table format)
        source_schema, source_tbl = _parse_table_name(source_table)
        target_schema, target_tbl = _parse_table_name(target_table)

        # Get connection parameters from environment
        source_conn_params = _get_connection_params(source_type)
        target_conn_params = _get_connection_params(target_type)

        # Create table config
        table_config = TableConfig(
            source_table=source_tbl,
            target_table=target_tbl,
            source_schema=source_schema,
            target_schema=target_schema,
            join_columns=join_cols,
            source_query=source_query,
            target_query=target_query,
            sample_size=sample_size,
        )

        # Create validation config
        output_path = Path(output)
        validation_config = ValidationConfig(
            source_db_type=DatabaseType(source_type.lower()),
            source_connection=source_conn_params,
            target_db_type=DatabaseType(target_type.lower()),
            target_connection=target_conn_params,
            tables=[table_config],
            output_dir=output_path,
            comparison=ComparisonSettings(
                abs_tol=tolerance,
                ignore_case=ignore_case,
                ignore_spaces=ignore_spaces,
            ),
        )

        logger.info(f"Comparing {source_table} -> {target_table}")
        logger.info(f"Join columns: {join_cols}")

        validator = DataValidator(validation_config)
        results = validator.validate()

        # Print summary
        result = results[source_tbl]
        match_pct = result.matching_rows / max(result.source_row_count, 1) * 100

        click.echo("\n" + "=" * 60)
        click.echo("COMPARISON RESULT")
        click.echo("=" * 60)
        click.echo(f"Source: {source_table} ({result.source_row_count} rows)")
        click.echo(f"Target: {target_table} ({result.target_row_count} rows)")
        click.echo(f"Match: {match_pct:.2f}% ({result.matching_rows} rows)")

        if (
            result.rows_only_in_source is not None
            and len(result.rows_only_in_source) > 0
        ):
            click.echo(f"Rows only in source: {len(result.rows_only_in_source)}")
        if (
            result.rows_only_in_target is not None
            and len(result.rows_only_in_target) > 0
        ):
            click.echo(f"Rows only in target: {len(result.rows_only_in_target)}")
        if result.mismatched_rows > 0:
            click.echo(f"Mismatched rows: {result.mismatched_rows}")

        click.echo("=" * 60)
        click.echo(f"Reports saved to: {output}")

        if match_pct == 100:
            click.echo("\n✓ Tables match!")
            ctx.exit(EXIT_SUCCESS)
        else:
            click.echo("\n✗ Tables have differences. Check reports for details.")
            ctx.exit(EXIT_VALIDATION_FAILED)

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        click.echo(f"Error: Configuration error - {e}", err=True)
        ctx.exit(EXIT_CONFIG_ERROR)

    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        click.echo(f"Error: Connection failed - {e}", err=True)
        ctx.exit(EXIT_CONNECTION_ERROR)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        click.echo(f"Error: Validation failed - {e}", err=True)
        ctx.exit(EXIT_VALIDATION_FAILED)

    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(EXIT_CONFIG_ERROR)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(EXIT_VALIDATION_FAILED)


def _parse_table_name(table_name: str) -> tuple[str | None, str]:
    """Parse a table name that may include schema.

    Args:
        table_name: Table name in format 'schema.table' or 'table'.

    Returns:
        Tuple of (schema, table) where schema may be None.
    """
    parts = table_name.split(".")
    if len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return None, parts[0]
    else:
        raise ValueError(f"Invalid table name format: {table_name}")


def _get_connection_params(db_type: str) -> dict:
    """Get connection parameters from environment variables.

    Args:
        db_type: Database type (snowflake, bigquery, redshift).

    Returns:
        Dictionary of connection parameters.

    Raises:
        ValueError: If required environment variables are not set.
    """
    import os

    db_type = db_type.lower()

    if db_type == "snowflake":
        required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
        _check_env_vars(required)
        return {
            "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
            "user": os.environ.get("SNOWFLAKE_USER"),
            "password": os.environ.get("SNOWFLAKE_PASSWORD"),
            "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
            "database": os.environ.get("SNOWFLAKE_DATABASE"),
            "schema": os.environ.get("SNOWFLAKE_SCHEMA"),
        }

    elif db_type == "bigquery":
        required = ["GCP_PROJECT"]
        _check_env_vars(required)
        return {
            "project": os.environ.get("GCP_PROJECT"),
            "dataset": os.environ.get("BQ_DATASET"),
            "credentials_path": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        }

    elif db_type == "redshift":
        required = [
            "REDSHIFT_HOST",
            "REDSHIFT_DATABASE",
            "REDSHIFT_USER",
            "REDSHIFT_PASSWORD",
        ]
        _check_env_vars(required)
        return {
            "host": os.environ.get("REDSHIFT_HOST"),
            "port": int(os.environ.get("REDSHIFT_PORT", "5439")),
            "database": os.environ.get("REDSHIFT_DATABASE"),
            "user": os.environ.get("REDSHIFT_USER"),
            "password": os.environ.get("REDSHIFT_PASSWORD"),
        }

    else:
        raise ValueError(f"Unknown database type: {db_type}")


def _check_env_vars(required: list[str]) -> None:
    """Check that required environment variables are set.

    Args:
        required: List of required environment variable names.

    Raises:
        ValueError: If any required variables are not set.
    """
    import os

    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


if __name__ == "__main__":
    cli()
