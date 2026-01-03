"""Unit tests for ReportGenerator."""

import json

import polars as pl
import pytest

from pycaroline.comparison.models import ComparisonResult
from pycaroline.reporting.generator import ReportGenerator


@pytest.fixture
def sample_result():
    """Create a sample ComparisonResult for testing."""
    return ComparisonResult(
        source_row_count=100,
        target_row_count=95,
        matching_rows=90,
        mismatched_rows=5,
        rows_only_in_source=pl.DataFrame({"id": [1, 2], "value": ["a", "b"]}),
        rows_only_in_target=pl.DataFrame({"id": [3], "value": ["c"]}),
        mismatched_columns=pl.DataFrame({"id": [4], "source": ["x"], "target": ["y"]}),
        column_stats=pl.DataFrame(
            {"column": ["id", "value"], "in_source": [True, True]}
        ),
        report_text="Sample report text",
    )


@pytest.fixture
def empty_result():
    """Create an empty ComparisonResult for testing."""
    return ComparisonResult(
        source_row_count=0,
        target_row_count=0,
        matching_rows=0,
        mismatched_rows=0,
        rows_only_in_source=pl.DataFrame(),
        rows_only_in_target=pl.DataFrame(),
        mismatched_columns=pl.DataFrame(),
        column_stats=pl.DataFrame({"column": [], "in_source": []}).cast(
            {"column": pl.Utf8, "in_source": pl.Boolean}
        ),
        report_text="",
    )


class TestReportGeneratorInit:
    """Tests for ReportGenerator initialization."""

    def test_creates_output_directory(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "new_dir" / "reports"

        generator = ReportGenerator(output_dir)

        assert output_dir.exists()
        assert generator.output_dir == output_dir

    def test_accepts_existing_directory(self, tmp_path):
        """Test that existing directory is accepted."""
        generator = ReportGenerator(tmp_path)

        assert generator.output_dir == tmp_path


class TestReportGeneratorGenerate:
    """Tests for the generate method."""

    def test_generate_returns_all_report_paths(self, tmp_path, sample_result):
        """Test that generate returns paths to all reports."""
        generator = ReportGenerator(tmp_path)

        reports = generator.generate(sample_result, "test_table")

        assert "json" in reports
        assert "csv" in reports
        assert "html" in reports
        assert reports["json"].exists()
        assert reports["html"].exists()

    def test_generate_creates_json_file(self, tmp_path, sample_result):
        """Test that JSON file is created with correct content."""
        generator = ReportGenerator(tmp_path)

        reports = generator.generate(sample_result, "test_table")

        with open(reports["json"]) as f:
            data = json.load(f)
        assert data["source_row_count"] == 100
        assert data["matching_rows"] == 90

    def test_generate_creates_html_file(self, tmp_path, sample_result):
        """Test that HTML file is created."""
        generator = ReportGenerator(tmp_path)

        reports = generator.generate(sample_result, "test_table")

        html_content = reports["html"].read_text()
        assert "test_table" in html_content
        assert "90" in html_content  # matching rows


class TestReportGeneratorJSON:
    """Tests for JSON report generation."""

    def test_json_contains_all_fields(self, tmp_path, sample_result):
        """Test that JSON contains all required fields."""
        generator = ReportGenerator(tmp_path)
        json_path = tmp_path / "test.json"

        generator._generate_json(sample_result, json_path)

        with open(json_path) as f:
            data = json.load(f)
        assert "source_row_count" in data
        assert "target_row_count" in data
        assert "matching_rows" in data
        assert "mismatched_rows" in data
        assert "match_percentage" in data

    def test_json_match_percentage_calculation(self, tmp_path, sample_result):
        """Test that match percentage is calculated correctly."""
        generator = ReportGenerator(tmp_path)
        json_path = tmp_path / "test.json"

        generator._generate_json(sample_result, json_path)

        with open(json_path) as f:
            data = json.load(f)
        assert data["match_percentage"] == 90.0  # 90/100 * 100


class TestReportGeneratorCSV:
    """Tests for CSV report generation."""

    def test_csv_creates_column_stats(self, tmp_path, sample_result):
        """Test that column stats CSV is always created."""
        generator = ReportGenerator(tmp_path)

        csv_paths = generator._generate_csv(sample_result, "test")

        assert "column_stats" in csv_paths
        assert csv_paths["column_stats"].exists()

    def test_csv_creates_rows_only_in_source(self, tmp_path, sample_result):
        """Test that rows_only_in_source CSV is created when data exists."""
        generator = ReportGenerator(tmp_path)

        csv_paths = generator._generate_csv(sample_result, "test")

        assert "rows_only_in_source" in csv_paths

    def test_csv_skips_empty_dataframes(self, tmp_path, empty_result):
        """Test that empty DataFrames don't create CSV files."""
        generator = ReportGenerator(tmp_path)

        csv_paths = generator._generate_csv(empty_result, "test")

        assert "rows_only_in_source" not in csv_paths
        assert "rows_only_in_target" not in csv_paths


class TestReportGeneratorHTML:
    """Tests for HTML report generation."""

    def test_html_contains_table_name(self, tmp_path, sample_result):
        """Test that HTML contains the table name."""
        generator = ReportGenerator(tmp_path)
        html_path = tmp_path / "test.html"

        generator._generate_html(sample_result, html_path, "my_table")

        content = html_path.read_text()
        assert "my_table" in content

    def test_html_shows_pass_for_100_percent(self, tmp_path):
        """Test that HTML shows PASS for 100% match."""
        result = ComparisonResult(
            source_row_count=10,
            target_row_count=10,
            matching_rows=10,
            mismatched_rows=0,
            rows_only_in_source=pl.DataFrame(),
            rows_only_in_target=pl.DataFrame(),
            mismatched_columns=pl.DataFrame(),
            column_stats=pl.DataFrame(),
            report_text="",
        )
        generator = ReportGenerator(tmp_path)
        html_path = tmp_path / "test.html"

        generator._generate_html(result, html_path, "test")

        content = html_path.read_text()
        assert "PASS" in content

    def test_html_shows_fail_for_low_match(self, tmp_path):
        """Test that HTML shows FAIL for low match percentage."""
        result = ComparisonResult(
            source_row_count=100,
            target_row_count=100,
            matching_rows=50,
            mismatched_rows=50,
            rows_only_in_source=pl.DataFrame(),
            rows_only_in_target=pl.DataFrame(),
            mismatched_columns=pl.DataFrame(),
            column_stats=pl.DataFrame(),
            report_text="",
        )
        generator = ReportGenerator(tmp_path)
        html_path = tmp_path / "test.html"

        generator._generate_html(result, html_path, "test")

        content = html_path.read_text()
        assert "FAIL" in content


class TestReportGeneratorJSONSummary:
    """Tests for generate_json_summary method."""

    def test_returns_dict_without_file(self, tmp_path, sample_result):
        """Test that generate_json_summary returns dict without creating file."""
        generator = ReportGenerator(tmp_path)

        summary = generator.generate_json_summary(sample_result)

        assert isinstance(summary, dict)
        assert summary["source_row_count"] == 100
        assert summary["matching_rows"] == 90
