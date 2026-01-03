"""Data models for validation configuration.

This module defines the dataclasses used for configuring data validation runs,
including database connections, table specifications, and comparison settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pycaroline.connectors.factory import DatabaseType


@dataclass
class TableConfig:
    """Configuration for a single table validation.

    Attributes:
        source_table: Name of the source table to validate.
        target_table: Name of the target table to validate (defaults to source_table).
        join_columns: List of column names to use as join keys for matching rows.
        source_schema: Optional schema name for the source table.
        target_schema: Optional schema name for the target table.
        source_query: Optional custom SQL query for source data (overrides source_table).
        target_query: Optional custom SQL query for target data (overrides target_table).
        sample_size: Optional limit on number of rows to compare.
    """

    source_table: str
    join_columns: list[str]
    target_table: str | None = None
    source_schema: str | None = None
    target_schema: str | None = None
    source_query: str | None = None
    target_query: str | None = None
    sample_size: int | None = None

    def __post_init__(self) -> None:
        """Set target_table to source_table if not provided."""
        if self.target_table is None:
            self.target_table = self.source_table


@dataclass
class ComparisonSettings:
    """Settings for data comparison behavior.

    Attributes:
        abs_tol: Absolute tolerance for numeric comparison (default: 0.0001).
        rel_tol: Relative tolerance for numeric comparison (default: 0.0).
        ignore_case: If True, string comparisons are case-insensitive (default: False).
        ignore_spaces: If True, leading/trailing whitespace is stripped (default: True).
    """

    abs_tol: float = 0.0001
    rel_tol: float = 0.0
    ignore_case: bool = False
    ignore_spaces: bool = True


@dataclass
class ValidationConfig:
    """Configuration for a complete validation run.

    Attributes:
        source_db_type: Type of the source database (snowflake, bigquery, redshift).
        source_connection: Connection parameters for the source database.
        target_db_type: Type of the target database (snowflake, bigquery, redshift).
        target_connection: Connection parameters for the target database.
        tables: List of table configurations to validate.
        output_dir: Directory path for output reports (default: ./validation_results).
        comparison: Optional comparison settings (tolerances, case sensitivity, etc.).
    """

    source_db_type: DatabaseType
    source_connection: dict[str, Any]
    target_db_type: DatabaseType
    target_connection: dict[str, Any]
    tables: list[TableConfig]
    output_dir: Path = field(default_factory=lambda: Path("./validation_results"))
    comparison: ComparisonSettings = field(default_factory=ComparisonSettings)

    def __post_init__(self) -> None:
        """Convert output_dir to Path if it's a string."""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
