"""ReportGenerator class for generating validation reports in multiple formats."""

import json
from pathlib import Path
from typing import Any

from pycaroline.comparison.models import ComparisonResult


class ReportGenerator:
    """Generates validation reports in multiple formats.

    Supports JSON summary, CSV detail files, and HTML reports.

    Attributes:
        output_dir: Directory where reports will be saved.
    """

    def __init__(self, output_dir: Path):
        """Initialize the report generator.

        Args:
            output_dir: Directory where reports will be saved.
                       Will be created if it doesn't exist.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, result: ComparisonResult, table_name: str) -> dict[str, Any]:
        """Generate all report formats for a comparison result.

        Args:
            result: ComparisonResult from a data comparison.
            table_name: Name of the table being compared (used in filenames).

        Returns:
            Dictionary with paths to generated reports:
            - "json": Path to JSON summary file
            - "csv": Dictionary of CSV file paths
            - "html": Path to HTML report file
        """
        reports: dict[str, Any] = {}

        # JSON summary
        json_path = self.output_dir / f"{table_name}_summary.json"
        reports["json"] = self._generate_json(result, json_path)

        # CSV details
        csv_paths = self._generate_csv(result, table_name)
        reports["csv"] = csv_paths

        # HTML report
        html_path = self.output_dir / f"{table_name}_report.html"
        reports["html"] = self._generate_html(result, html_path, table_name)

        return reports

    def _generate_json(self, result: ComparisonResult, path: Path) -> Path:
        """Generate JSON summary report.

        Args:
            result: ComparisonResult from a data comparison.
            path: Path where JSON file will be saved.

        Returns:
            Path to the generated JSON file.
        """
        summary = {
            "source_row_count": int(result.source_row_count),
            "target_row_count": int(result.target_row_count),
            "matching_rows": int(result.matching_rows),
            "mismatched_rows": int(result.mismatched_rows),
            "rows_only_in_source": int(len(result.rows_only_in_source)),
            "rows_only_in_target": int(len(result.rows_only_in_target)),
            "match_percentage": float(
                result.matching_rows / max(result.source_row_count, 1) * 100
            ),
        }
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        return path

    def _generate_csv(
        self, result: ComparisonResult, table_name: str
    ) -> dict[str, Path]:
        """Generate CSV detail files.

        Generates separate CSV files for:
        - Rows only in source (if any)
        - Rows only in target (if any)
        - Mismatched rows (if any)
        - Column statistics

        Args:
            result: ComparisonResult from a data comparison.
            table_name: Name of the table being compared (used in filenames).

        Returns:
            Dictionary mapping report type to file path.
        """
        paths: dict[str, Path] = {}

        if len(result.rows_only_in_source) > 0:
            path = self.output_dir / f"{table_name}_rows_only_in_source.csv"
            result.rows_only_in_source.write_csv(path)
            paths["rows_only_in_source"] = path

        if len(result.rows_only_in_target) > 0:
            path = self.output_dir / f"{table_name}_rows_only_in_target.csv"
            result.rows_only_in_target.write_csv(path)
            paths["rows_only_in_target"] = path

        if len(result.mismatched_columns) > 0:
            path = self.output_dir / f"{table_name}_mismatched_rows.csv"
            result.mismatched_columns.write_csv(path)
            paths["mismatched_rows"] = path

        path = self.output_dir / f"{table_name}_column_stats.csv"
        result.column_stats.write_csv(path)
        paths["column_stats"] = path

        return paths

    def _generate_html(
        self, result: ComparisonResult, path: Path, table_name: str
    ) -> Path:
        """Generate HTML report.

        Args:
            result: ComparisonResult from a data comparison.
            path: Path where HTML file will be saved.
            table_name: Name of the table being compared.

        Returns:
            Path to the generated HTML file.
        """
        match_pct = result.matching_rows / max(result.source_row_count, 1) * 100

        # Determine status color
        if match_pct >= 100:
            status_color = "#28a745"  # Green
            status_text = "PASS"
        elif match_pct >= 90:
            status_color = "#ffc107"  # Yellow
            status_text = "WARNING"
        else:
            status_color = "#dc3545"  # Red
            status_text = "FAIL"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Validation Report - {table_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            background-color: {status_color};
            color: white;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .report-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .report-section h2 {{
            margin-top: 0;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Validation Report</h1>
        <p>Table: <strong>{table_name}</strong></p>
        <span class="status-badge">{status_text} - {match_pct:.1f}% Match</span>
    </div>

    <div class="summary-grid">
        <div class="summary-card">
            <h3>Source Rows</h3>
            <div class="value">{result.source_row_count:,}</div>
        </div>
        <div class="summary-card">
            <h3>Target Rows</h3>
            <div class="value">{result.target_row_count:,}</div>
        </div>
        <div class="summary-card">
            <h3>Matching Rows</h3>
            <div class="value">{result.matching_rows:,}</div>
        </div>
        <div class="summary-card">
            <h3>Mismatched Rows</h3>
            <div class="value">{result.mismatched_rows:,}</div>
        </div>
        <div class="summary-card">
            <h3>Only in Source</h3>
            <div class="value">{len(result.rows_only_in_source):,}</div>
        </div>
        <div class="summary-card">
            <h3>Only in Target</h3>
            <div class="value">{len(result.rows_only_in_target):,}</div>
        </div>
    </div>

    <div class="report-section">
        <h2>Detailed Report</h2>
        <pre>{result.report_text}</pre>
    </div>
</body>
</html>"""

        with open(path, "w") as f:
            f.write(html_content)
        return path

    def generate_json_summary(self, result: ComparisonResult) -> dict[str, Any]:
        """Generate JSON summary as a dictionary (without writing to file).

        Useful for programmatic access to report data.

        Args:
            result: ComparisonResult from a data comparison.

        Returns:
            Dictionary containing the summary data.
        """
        return {
            "source_row_count": result.source_row_count,
            "target_row_count": result.target_row_count,
            "matching_rows": result.matching_rows,
            "mismatched_rows": result.mismatched_rows,
            "rows_only_in_source": len(result.rows_only_in_source),
            "rows_only_in_target": len(result.rows_only_in_target),
            "match_percentage": (
                result.matching_rows / max(result.source_row_count, 1) * 100
            ),
        }
