"""Integration tests for DataValidator.

Tests the full validation workflow with mocked connectors.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from pycaroline.comparison.models import ComparisonResult
from pycaroline.config.models import (
    ComparisonSettings,
    TableConfig,
    ValidationConfig,
)
from pycaroline.connectors.base import BaseConnector
from pycaroline.connectors.factory import ConnectorFactory, DatabaseType
from pycaroline.validator import DataValidator, ValidationError


class MockConnector(BaseConnector):
    """Mock connector for testing that returns predefined DataFrames."""

    def __init__(self, data_map: dict = None, **kwargs):
        """Initialize with a mapping of table names to DataFrames.

        Args:
            data_map: Dictionary mapping table names to DataFrames.
            **kwargs: Additional arguments (ignored).
        """
        self._connection = None
        self.data_map = data_map or {}
        self.queries_executed = []

    def connect(self) -> None:
        """Simulate connection."""
        self._connection = MagicMock()

    def disconnect(self) -> None:
        """Simulate disconnection."""
        self._connection = None

    def query(self, sql: str) -> pl.DataFrame:
        """Return predefined data based on query.

        Args:
            sql: SQL query string.

        Returns:
            DataFrame from data_map if table name found in query.
        """
        self.queries_executed.append(sql)
        # Try to find matching table in data_map
        for table_name, df in self.data_map.items():
            if table_name.lower() in sql.lower():
                result = df.clone()
                # Handle LIMIT clause
                if "LIMIT" in sql.upper():
                    import re

                    match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
                    if match:
                        limit = int(match.group(1))
                        result = result.head(limit)
                return result
        return pl.DataFrame()


class TestDataValidatorIntegration:
    """Integration tests for DataValidator with mocked connectors."""

    @pytest.fixture
    def sample_source_data(self):
        """Create sample source DataFrame."""
        return pl.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
            }
        )

    @pytest.fixture
    def sample_target_data(self):
        """Create sample target DataFrame (matching source)."""
        return pl.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
            }
        )

    @pytest.fixture
    def mismatched_target_data(self):
        """Create target DataFrame with some mismatches."""
        return pl.DataFrame(
            {
                "id": [1, 2, 4],  # 3 missing; 4 extra
                "name": ["Alice", "BOB", "David"],  # Bob -> BOB
            }
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def validation_config(self, temp_output_dir):
        """Create a basic validation config."""
        return ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test", "user": "test", "password": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test", "dataset": "test"},
            tables=[
                TableConfig(
                    source_table="customers",
                    target_table="customers",
                    join_columns=["id"],
                )
            ],
            output_dir=temp_output_dir,
            comparison=ComparisonSettings(),
        )

    def test_validate_matching_tables(
        self, sample_source_data, sample_target_data, validation_config
    ):
        """Test validation with perfectly matching source and target tables."""
        # Create mock connectors
        source_connector = MockConnector(data_map={"customers": sample_source_data})
        target_connector = MockConnector(data_map={"customers": sample_target_data})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            results = validator.validate()

        # Verify results
        assert "customers" in results
        result = results["customers"]
        assert isinstance(result, ComparisonResult)
        assert result.source_row_count == 3
        assert result.target_row_count == 3
        assert result.matching_rows == 3
        assert result.mismatched_rows == 0
        assert len(result.rows_only_in_source) == 0
        assert len(result.rows_only_in_target) == 0

    def test_validate_mismatched_tables(
        self, sample_source_data, mismatched_target_data, validation_config
    ):
        """Test validation with mismatched source and target tables."""
        source_connector = MockConnector(data_map={"customers": sample_source_data})
        target_connector = MockConnector(data_map={"customers": mismatched_target_data})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            results = validator.validate()

        result = results["customers"]
        # Source has ids 1-3, target has 1,2,4
        # Matching keys: 1, 2
        # Only in source: 3
        # Only in target: 4
        assert result.source_row_count == 3
        assert result.target_row_count == 3
        assert len(result.rows_only_in_source) == 1  # id 3
        assert len(result.rows_only_in_target) == 1  # id 4

    def test_validate_generates_json_report(
        self, sample_source_data, sample_target_data, validation_config
    ):
        """Test that validation generates JSON report file."""
        source_connector = MockConnector(data_map={"customers": sample_source_data})
        target_connector = MockConnector(data_map={"customers": sample_target_data})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            validator.validate()

        # Check JSON report exists
        json_path = validation_config.output_dir / "customers_summary.json"
        assert json_path.exists()

        # Verify JSON content
        with open(json_path) as f:
            report = json.load(f)

        assert report["source_row_count"] == 3
        assert report["target_row_count"] == 3
        assert report["matching_rows"] == 3
        assert report["match_percentage"] == 100.0

    def test_validate_generates_html_report(
        self, sample_source_data, sample_target_data, validation_config
    ):
        """Test that validation generates HTML report file."""
        source_connector = MockConnector(data_map={"customers": sample_source_data})
        target_connector = MockConnector(data_map={"customers": sample_target_data})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            validator.validate()

        # Check HTML report exists
        html_path = validation_config.output_dir / "customers_report.html"
        assert html_path.exists()

        # Verify HTML content
        with open(html_path) as f:
            html_content = f.read()

        assert "Data Validation Report" in html_content
        assert "customers" in html_content

    def test_validate_generates_csv_column_stats(
        self, sample_source_data, sample_target_data, validation_config
    ):
        """Test that validation generates CSV column stats file."""
        source_connector = MockConnector(data_map={"customers": sample_source_data})
        target_connector = MockConnector(data_map={"customers": sample_target_data})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            validator.validate()

        # Check CSV column stats exists
        csv_path = validation_config.output_dir / "customers_column_stats.csv"
        assert csv_path.exists()

        # Verify CSV can be read
        df = pl.read_csv(csv_path)
        assert "column" in df.columns

    def test_validate_multiple_tables(self, temp_output_dir):
        """Test validation with multiple tables configured."""
        # Create data for two tables
        customers_df = pl.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
            }
        )
        orders_df = pl.DataFrame(
            {
                "order_id": [101, 102, 103],
                "customer_id": [1, 2, 3],
                "amount": [50.0, 75.0, 100.0],
            }
        )

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="customers",
                    target_table="customers",
                    join_columns=["id"],
                ),
                TableConfig(
                    source_table="orders",
                    target_table="orders",
                    join_columns=["order_id"],
                ),
            ],
            output_dir=temp_output_dir,
        )

        source_connector = MockConnector(
            data_map={"customers": customers_df, "orders": orders_df}
        )
        target_connector = MockConnector(
            data_map={"customers": customers_df, "orders": orders_df}
        )

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            results = validator.validate()

        # Verify both tables were validated
        assert "customers" in results
        assert "orders" in results
        assert results["customers"].matching_rows == 3
        assert results["orders"].matching_rows == 3

        # Verify reports generated for both
        assert (temp_output_dir / "customers_summary.json").exists()
        assert (temp_output_dir / "orders_summary.json").exists()

    def test_validate_with_custom_query(self, temp_output_dir):
        """Test validation using custom SQL queries instead of table names."""
        source_df = pl.DataFrame(
            {
                "id": [1, 2],
                "value": [100, 200],
            }
        )
        target_df = pl.DataFrame(
            {
                "id": [1, 2],
                "value": [100, 200],
            }
        )

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="data",
                    target_table="data",
                    join_columns=["id"],
                    source_query="SELECT id, value FROM source_table WHERE active = 1",
                    target_query="SELECT id, value FROM target_table WHERE active = 1",
                ),
            ],
            output_dir=temp_output_dir,
        )

        # Mock connector that returns data for any query
        source_connector = MockConnector()
        source_connector.data_map = {"source_table": source_df}
        target_connector = MockConnector()
        target_connector.data_map = {"target_table": target_df}

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            validator.validate()

        # Verify custom queries were executed
        assert any("source_table" in q for q in source_connector.queries_executed)
        assert any("target_table" in q for q in target_connector.queries_executed)

    def test_validate_with_sample_size(self, temp_output_dir):
        """Test validation with sample_size limiting rows."""
        large_df = pl.DataFrame(
            {
                "id": list(range(1000)),
                "value": list(range(1000)),
            }
        )

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="large_table",
                    target_table="large_table",
                    join_columns=["id"],
                    sample_size=100,
                ),
            ],
            output_dir=temp_output_dir,
        )

        source_connector = MockConnector(data_map={"large_table": large_df})
        target_connector = MockConnector(data_map={"large_table": large_df})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            validator.validate()

        # Verify LIMIT was included in queries
        assert any("LIMIT 100" in q for q in source_connector.queries_executed)

    def test_validate_with_schema(self, temp_output_dir):
        """Test validation with schema-qualified table names."""
        df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="users",
                    target_table="users",
                    source_schema="prod",
                    target_schema="staging",
                    join_columns=["id"],
                ),
            ],
            output_dir=temp_output_dir,
        )

        source_connector = MockConnector(data_map={"prod.users": df, "users": df})
        target_connector = MockConnector(data_map={"staging.users": df, "users": df})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            validator.validate()

        # Verify schema-qualified names in queries
        assert any("prod.users" in q for q in source_connector.queries_executed)
        assert any("staging.users" in q for q in target_connector.queries_executed)

    def test_validate_with_comparison_settings(self, temp_output_dir):
        """Test validation with custom comparison settings."""
        source_df = pl.DataFrame(
            {
                "id": [1, 2],
                "name": ["  Alice  ", "BOB"],
                "value": [100.0, 200.0],
            }
        )
        target_df = pl.DataFrame(
            {
                "id": [1, 2],
                "name": ["Alice", "bob"],
                "value": [100.0001, 200.0],  # Small numeric difference
            }
        )

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="data",
                    target_table="data",
                    join_columns=["id"],
                ),
            ],
            output_dir=temp_output_dir,
            comparison=ComparisonSettings(
                abs_tol=0.001,  # Allow small numeric differences
                ignore_case=True,  # Case-insensitive string comparison
                ignore_spaces=True,  # Strip whitespace
            ),
        )

        source_connector = MockConnector(data_map={"data": source_df})
        target_connector = MockConnector(data_map={"data": target_df})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            results = validator.validate()

        # With these settings, rows should match
        result = results["data"]
        assert result.matching_rows == 2

    def test_validate_single_table_method(
        self, sample_source_data, sample_target_data, validation_config
    ):
        """Test validate_single_table convenience method."""
        source_connector = MockConnector(data_map={"orders": sample_source_data})
        target_connector = MockConnector(data_map={"orders": sample_target_data})

        table_config = TableConfig(
            source_table="orders",
            target_table="orders",
            join_columns=["id"],
        )

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(validation_config)
            result = validator.validate_single_table(table_config)

        assert isinstance(result, ComparisonResult)
        assert result.source_row_count == 3
        assert result.matching_rows == 3

    def test_validate_empty_tables(self, temp_output_dir):
        """Test validation with empty source and target tables."""
        empty_df = pl.DataFrame({"id": [], "name": [], "value": []}).cast(
            {"id": pl.Int64, "name": pl.Utf8, "value": pl.Float64}
        )

        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="empty_table",
                    target_table="empty_table",
                    join_columns=["id"],
                ),
            ],
            output_dir=temp_output_dir,
        )

        source_connector = MockConnector(data_map={"empty_table": empty_df})
        target_connector = MockConnector(data_map={"empty_table": empty_df})

        with patch.object(
            ConnectorFactory, "create", side_effect=[source_connector, target_connector]
        ):
            validator = DataValidator(config)
            results = validator.validate()

        result = results["empty_table"]
        assert result.source_row_count == 0
        assert result.target_row_count == 0
        assert result.matching_rows == 0


class TestDataValidatorErrorHandling:
    """Tests for DataValidator error handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_validate_raises_validation_error_on_query_failure(self, temp_output_dir):
        """Test that validation raises ValidationError when query fails."""
        config = ValidationConfig(
            source_db_type=DatabaseType.SNOWFLAKE,
            source_connection={"account": "test"},
            target_db_type=DatabaseType.BIGQUERY,
            target_connection={"project": "test"},
            tables=[
                TableConfig(
                    source_table="nonexistent",
                    target_table="nonexistent",
                    join_columns=["id"],
                ),
            ],
            output_dir=temp_output_dir,
        )

        # Create connector that raises error on query
        class FailingConnector(BaseConnector):
            def connect(self):
                self._connection = MagicMock()

            def disconnect(self):
                self._connection = None

            def query(self, sql):
                raise Exception("Table not found")

        with patch.object(
            ConnectorFactory,
            "create",
            side_effect=[FailingConnector(), FailingConnector()],
        ):
            validator = DataValidator(config)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate()

            assert "nonexistent" in str(exc_info.value)
