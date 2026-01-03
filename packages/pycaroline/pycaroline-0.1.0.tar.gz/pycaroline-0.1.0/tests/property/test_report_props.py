"""Property-based tests for report generation.

These tests validate universal properties of the ReportGenerator using hypothesis.
"""

import json
import tempfile
from pathlib import Path

import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pycaroline.comparison.models import ComparisonResult
from pycaroline.reporting.generator import ReportGenerator


# Strategy for generating valid ComparisonResult objects
@st.composite
def comparison_results(draw):
    """Generate valid ComparisonResult objects for testing."""
    # Generate row counts
    source_count = draw(st.integers(min_value=0, max_value=100))
    target_count = draw(st.integers(min_value=0, max_value=100))

    # Generate matching/mismatched counts (must be <= min of source/target)
    max_matching = min(source_count, target_count)
    matching = draw(st.integers(min_value=0, max_value=max_matching))
    mismatched = draw(st.integers(min_value=0, max_value=max_matching - matching))

    # Generate rows only in source/target
    only_in_source_count = draw(
        st.integers(min_value=0, max_value=max(0, source_count - matching - mismatched))
    )
    only_in_target_count = draw(
        st.integers(min_value=0, max_value=max(0, target_count - matching - mismatched))
    )

    # Create DataFrames for rows only in source
    if only_in_source_count > 0:
        rows_only_in_source = pl.DataFrame(
            {
                "id": list(range(only_in_source_count)),
                "value": [f"source_{i}" for i in range(only_in_source_count)],
            }
        )
    else:
        rows_only_in_source = pl.DataFrame({"id": [], "value": []}).cast(
            {"id": pl.Int64, "value": pl.Utf8}
        )

    # Create DataFrames for rows only in target
    if only_in_target_count > 0:
        rows_only_in_target = pl.DataFrame(
            {
                "id": list(range(only_in_target_count)),
                "value": [f"target_{i}" for i in range(only_in_target_count)],
            }
        )
    else:
        rows_only_in_target = pl.DataFrame({"id": [], "value": []}).cast(
            {"id": pl.Int64, "value": pl.Utf8}
        )

    # Create DataFrame for mismatched columns
    if mismatched > 0:
        mismatched_columns = pl.DataFrame(
            {
                "id": list(range(mismatched)),
                "value_source": [f"src_{i}" for i in range(mismatched)],
                "value_target": [f"tgt_{i}" for i in range(mismatched)],
            }
        )
    else:
        mismatched_columns = pl.DataFrame()

    # Create column stats DataFrame
    column_stats = pl.DataFrame(
        {
            "column": ["id", "value"],
            "in_source": [True, True],
            "in_target": [True, True],
            "source_dtype": ["int64", "object"],
            "target_dtype": ["int64", "object"],
        }
    )

    return ComparisonResult(
        source_row_count=source_count,
        target_row_count=target_count,
        matching_rows=matching,
        mismatched_rows=mismatched,
        rows_only_in_source=rows_only_in_source,
        rows_only_in_target=rows_only_in_target,
        mismatched_columns=mismatched_columns,
        column_stats=column_stats,
        report_text="Test report text",
    )


class TestProperty13ReportCompleteness:
    """
    **Feature: data-validation-library, Property 13: Report Completeness**
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

    For any comparison result, the generated report SHALL contain:
    source_row_count, target_row_count, matching_rows, mismatched_rows,
    rows_only_in_source count, and rows_only_in_target count.
    """

    @given(result=comparison_results())
    @settings(max_examples=100, deadline=None)
    def test_json_report_contains_all_required_fields(self, result: ComparisonResult):
        """
        **Feature: data-validation-library, Property 13: Report Completeness**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

        For any comparison result, the JSON report must contain all required fields.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(Path(tmpdir))
            reports = generator.generate(result, "test_table")

            # Read the JSON report
            with open(reports["json"]) as f:
                json_data = json.load(f)

            # Verify all required fields are present
            required_fields = [
                "source_row_count",
                "target_row_count",
                "matching_rows",
                "mismatched_rows",
                "rows_only_in_source",
                "rows_only_in_target",
            ]

            for field in required_fields:
                assert field in json_data, f"Missing required field: {field}"

            # Verify values match the input
            assert json_data["source_row_count"] == result.source_row_count
            assert json_data["target_row_count"] == result.target_row_count
            assert json_data["matching_rows"] == result.matching_rows
            assert json_data["mismatched_rows"] == result.mismatched_rows
            assert json_data["rows_only_in_source"] == len(result.rows_only_in_source)
            assert json_data["rows_only_in_target"] == len(result.rows_only_in_target)


class TestProperty14JSONReportValidity:
    """
    **Feature: data-validation-library, Property 14: JSON Report Validity**
    **Validates: Requirements 4.7**

    For any comparison result, the JSON report output SHALL be valid JSON
    that can be parsed back into a dictionary.
    """

    @given(result=comparison_results())
    @settings(max_examples=100, deadline=None)
    def test_json_report_is_valid_json(self, result: ComparisonResult):
        """
        **Feature: data-validation-library, Property 14: JSON Report Validity**
        **Validates: Requirements 4.7**

        For any comparison result, the JSON report must be valid JSON.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(Path(tmpdir))
            reports = generator.generate(result, "test_table")

            # Read the raw file content
            with open(reports["json"]) as f:
                raw_content = f.read()

            # Verify it can be parsed as valid JSON
            try:
                parsed = json.loads(raw_content)
            except json.JSONDecodeError as e:
                pytest.fail(f"JSON report is not valid JSON: {e}")

            # Verify it's a dictionary
            assert isinstance(parsed, dict), "JSON report should parse to a dictionary"

            # Verify round-trip: re-serializing should produce equivalent JSON
            re_serialized = json.dumps(parsed, indent=2)
            re_parsed = json.loads(re_serialized)
            assert parsed == re_parsed, "JSON round-trip should preserve data"


class TestProperty15CSVReportValidity:
    """
    **Feature: data-validation-library, Property 15: CSV Report Validity**
    **Validates: Requirements 4.8**

    For any comparison result with mismatched rows, the CSV output SHALL be
    valid CSV that can be parsed back into a DataFrame with the same row count.
    """

    @given(result=comparison_results())
    @settings(max_examples=100, deadline=None)
    def test_csv_reports_are_valid_csv(self, result: ComparisonResult):
        """
        **Feature: data-validation-library, Property 15: CSV Report Validity**
        **Validates: Requirements 4.8**

        For any comparison result, all generated CSV files must be valid CSV
        that can be parsed back into DataFrames with correct row counts.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(Path(tmpdir))
            reports = generator.generate(result, "test_table")

            csv_reports = reports.get("csv", {})

            # Verify rows_only_in_source CSV if it exists
            if "rows_only_in_source" in csv_reports:
                path = csv_reports["rows_only_in_source"]
                parsed_df = pl.read_csv(path)
                assert len(parsed_df) == len(result.rows_only_in_source), (
                    f"rows_only_in_source CSV row count mismatch: "
                    f"expected {len(result.rows_only_in_source)}, got {len(parsed_df)}"
                )

            # Verify rows_only_in_target CSV if it exists
            if "rows_only_in_target" in csv_reports:
                path = csv_reports["rows_only_in_target"]
                parsed_df = pl.read_csv(path)
                assert len(parsed_df) == len(result.rows_only_in_target), (
                    f"rows_only_in_target CSV row count mismatch: "
                    f"expected {len(result.rows_only_in_target)}, got {len(parsed_df)}"
                )

            # Verify mismatched_rows CSV if it exists
            if "mismatched_rows" in csv_reports:
                path = csv_reports["mismatched_rows"]
                parsed_df = pl.read_csv(path)
                assert len(parsed_df) == len(result.mismatched_columns), (
                    f"mismatched_rows CSV row count mismatch: "
                    f"expected {len(result.mismatched_columns)}, got {len(parsed_df)}"
                )

            # Verify column_stats CSV always exists and is valid
            assert (
                "column_stats" in csv_reports
            ), "column_stats CSV should always be generated"
            path = csv_reports["column_stats"]
            parsed_df = pl.read_csv(path)
            assert len(parsed_df) == len(result.column_stats), (
                f"column_stats CSV row count mismatch: "
                f"expected {len(result.column_stats)}, got {len(parsed_df)}"
            )

    @given(
        num_mismatched=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100, deadline=None)
    def test_csv_with_mismatched_rows_round_trips(self, num_mismatched: int):
        """
        **Feature: data-validation-library, Property 15: CSV Report Validity**
        **Validates: Requirements 4.8**

        For any comparison result with mismatched rows, the CSV output
        must preserve the row count when parsed back.
        """
        # Create a result with specific number of mismatched rows
        mismatched_columns = pl.DataFrame(
            {
                "id": list(range(num_mismatched)),
                "value_source": [f"src_{i}" for i in range(num_mismatched)],
                "value_target": [f"tgt_{i}" for i in range(num_mismatched)],
            }
        )

        result = ComparisonResult(
            source_row_count=num_mismatched,
            target_row_count=num_mismatched,
            matching_rows=0,
            mismatched_rows=num_mismatched,
            rows_only_in_source=pl.DataFrame({"id": [], "value": []}).cast(
                {"id": pl.Int64, "value": pl.Utf8}
            ),
            rows_only_in_target=pl.DataFrame({"id": [], "value": []}).cast(
                {"id": pl.Int64, "value": pl.Utf8}
            ),
            mismatched_columns=mismatched_columns,
            column_stats=pl.DataFrame(
                {
                    "column": ["id", "value"],
                    "in_source": [True, True],
                    "in_target": [True, True],
                }
            ),
            report_text="Test report",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(Path(tmpdir))
            reports = generator.generate(result, "test_table")

            # Verify mismatched_rows CSV exists and has correct row count
            assert (
                "mismatched_rows" in reports["csv"]
            ), "mismatched_rows CSV should be generated when there are mismatches"

            path = reports["csv"]["mismatched_rows"]
            parsed_df = pl.read_csv(path)

            assert len(parsed_df) == num_mismatched, (
                f"CSV round-trip failed: expected {num_mismatched} rows, "
                f"got {len(parsed_df)}"
            )
