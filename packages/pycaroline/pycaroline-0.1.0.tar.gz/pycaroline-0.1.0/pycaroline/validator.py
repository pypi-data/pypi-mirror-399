"""DataValidator class for orchestrating data validation workflows.

This module provides the main orchestrator that coordinates database connections,
data comparison, and report generation for validating data migrations.
"""

import logging

from pycaroline.comparison.comparator import DataComparator
from pycaroline.comparison.models import ComparisonConfig, ComparisonResult
from pycaroline.config.models import TableConfig, ValidationConfig
from pycaroline.connectors.base import BaseConnector
from pycaroline.connectors.factory import ConnectorFactory
from pycaroline.reporting.generator import ReportGenerator

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when a validation operation fails."""

    pass


class DataValidator:
    """Main orchestrator for data validation.

    This class coordinates the entire validation workflow:
    1. Creates database connectors for source and target
    2. Retrieves data from configured tables
    3. Compares data using DataComparator
    4. Generates reports using ReportGenerator

    Attributes:
        config: ValidationConfig with all validation settings.
        reporter: ReportGenerator for creating output reports.

    Example:
        config = ConfigLoader.load(Path("validation_config.yaml"))
        validator = DataValidator(config)
        results = validator.validate()

        for table, result in results.items():
            print(f"{table}: {result.matching_rows}/{result.source_row_count} rows match")
    """

    def __init__(self, config: ValidationConfig):
        """Initialize the DataValidator.

        Args:
            config: ValidationConfig containing all validation settings including
                   source/target database connections, table configurations,
                   comparison settings, and output directory.
        """
        self.config = config
        self.reporter = ReportGenerator(config.output_dir)

    def validate(self) -> dict[str, ComparisonResult]:
        """Run validation for all configured tables.

        Creates connections to source and target databases, then iterates
        through all configured tables, comparing data and generating reports.

        Returns:
            Dictionary mapping table names to their ComparisonResult objects.

        Raises:
            ValidationError: If validation fails for any table.
            ConnectionError: If database connections cannot be established.
        """
        results: dict[str, ComparisonResult] = {}

        logger.info(f"Starting validation with {len(self.config.tables)} table(s)")

        # Create connectors
        source_conn = ConnectorFactory.create(
            self.config.source_db_type, **self.config.source_connection
        )
        target_conn = ConnectorFactory.create(
            self.config.target_db_type, **self.config.target_connection
        )

        try:
            with source_conn, target_conn:
                for table_config in self.config.tables:
                    table_name = table_config.source_table
                    logger.info(f"Validating table: {table_name}")

                    try:
                        result = self._validate_table(
                            source_conn, target_conn, table_config
                        )
                        results[table_name] = result

                        # Generate reports for this table
                        self.reporter.generate(result, table_name)

                        # Log summary
                        match_pct = (
                            result.matching_rows / max(result.source_row_count, 1) * 100
                        )
                        logger.info(
                            f"Table {table_name}: {match_pct:.2f}% match "
                            f"({result.matching_rows}/{result.source_row_count} rows)"
                        )

                    except Exception as e:
                        logger.error(f"Failed to validate table {table_name}: {e}")
                        raise ValidationError(
                            f"Validation failed for table {table_name}: {e}"
                        ) from e

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            logger.error(f"Validation failed: {e}")
            raise ValidationError(f"Validation failed: {e}") from e

        logger.info(f"Validation complete. Processed {len(results)} table(s)")
        return results

    def _validate_table(
        self,
        source_conn: BaseConnector,
        target_conn: BaseConnector,
        table_config: TableConfig,
    ) -> ComparisonResult:
        """Validate a single table.

        Retrieves data from source and target databases, then compares
        using the configured comparison settings.

        Args:
            source_conn: Connected source database connector.
            target_conn: Connected target database connector.
            table_config: Configuration for the table to validate.

        Returns:
            ComparisonResult containing all comparison outputs.

        Raises:
            ValidationError: If data retrieval or comparison fails.
        """
        # Get source data
        if table_config.source_query:
            logger.debug(f"Executing source query for {table_config.source_table}")
            source_df = source_conn.query(table_config.source_query)
        else:
            logger.debug(
                f"Getting source table: {table_config.source_schema}.{table_config.source_table}"
                if table_config.source_schema
                else f"Getting source table: {table_config.source_table}"
            )
            source_df = source_conn.get_table(
                table_config.source_table,
                table_config.source_schema,
                table_config.sample_size,
            )

        # Get target data
        target_table = table_config.target_table or table_config.source_table
        if table_config.target_query:
            logger.debug(f"Executing target query for {target_table}")
            target_df = target_conn.query(table_config.target_query)
        else:
            logger.debug(
                f"Getting target table: {table_config.target_schema}.{target_table}"
                if table_config.target_schema
                else f"Getting target table: {target_table}"
            )
            target_df = target_conn.get_table(
                target_table,
                table_config.target_schema,
                table_config.sample_size,
            )

        logger.debug(f"Source rows: {len(source_df)}, Target rows: {len(target_df)}")

        # Create comparison config from validation config
        comparison_config = ComparisonConfig(
            join_columns=table_config.join_columns,
            abs_tol=self.config.comparison.abs_tol,
            rel_tol=self.config.comparison.rel_tol,
            ignore_case=self.config.comparison.ignore_case,
            ignore_spaces=self.config.comparison.ignore_spaces,
        )

        # Compare
        comparator = DataComparator(comparison_config)
        return comparator.compare(
            source_df, target_df, source_name="source", target_name="target"
        )

    def validate_single_table(self, table_config: TableConfig) -> ComparisonResult:
        """Validate a single table without using the full config.

        Convenience method for validating just one table. Creates fresh
        connections for the validation.

        Args:
            table_config: Configuration for the table to validate.

        Returns:
            ComparisonResult containing all comparison outputs.

        Raises:
            ValidationError: If validation fails.
        """
        source_conn = ConnectorFactory.create(
            self.config.source_db_type, **self.config.source_connection
        )
        target_conn = ConnectorFactory.create(
            self.config.target_db_type, **self.config.target_connection
        )

        with source_conn, target_conn:
            result = self._validate_table(source_conn, target_conn, table_config)
            self.reporter.generate(result, table_config.source_table)
            return result
