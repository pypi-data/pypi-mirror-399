"""Unit tests for CLI compare-files command."""

import os
import tempfile

import polars as pl
import pytest
from click.testing import CliRunner

from pycaroline.cli import cli


class TestCompareFilesCommand:
    """Tests for the compare-files CLI command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_files(self):
        """Create temporary test files."""
        source_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        target_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        source_df.write_parquet(source_path)
        target_df.write_parquet(target_path)

        yield source_path, target_path

        os.unlink(source_path)
        os.unlink(target_path)

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_compare_files_identical(self, runner, temp_files, temp_output_dir):
        """Test comparing identical files."""
        source_path, target_path = temp_files

        result = runner.invoke(
            cli,
            [
                "compare-files",
                "--source",
                source_path,
                "--target",
                target_path,
                "--join-columns",
                "id",
                "--output",
                temp_output_dir,
            ],
        )

        assert "100.00%" in result.output
        assert "Files match!" in result.output

    def test_compare_files_with_differences(self, runner, temp_output_dir):
        """Test comparing files with differences."""
        source_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        target_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 25, 30]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert "Files have differences" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_file_not_found(self, runner, temp_output_dir):
        """Test error handling for missing file."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name
            pl.DataFrame({"id": [1]}).write_parquet(target_path)

        try:
            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    "/nonexistent/file.parquet",
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert result.exit_code != 0
            assert "Error" in result.output
        finally:
            os.unlink(target_path)

    def test_compare_files_invalid_source_options_json(
        self, runner, temp_files, temp_output_dir
    ):
        """Test error handling for invalid source options JSON."""
        source_path, target_path = temp_files

        result = runner.invoke(
            cli,
            [
                "compare-files",
                "-s",
                source_path,
                "-t",
                target_path,
                "-j",
                "id",
                "-o",
                temp_output_dir,
                "--source-options",
                "not valid json",
            ],
        )

        assert result.exit_code != 0
        assert "Invalid JSON" in result.output or "Error" in result.output

    def test_compare_files_invalid_target_options_json(
        self, runner, temp_files, temp_output_dir
    ):
        """Test error handling for invalid target options JSON."""
        source_path, target_path = temp_files

        result = runner.invoke(
            cli,
            [
                "compare-files",
                "-s",
                source_path,
                "-t",
                target_path,
                "-j",
                "id",
                "-o",
                temp_output_dir,
                "--target-options",
                "{invalid}",
            ],
        )

        assert result.exit_code != 0
        assert "Invalid JSON" in result.output or "Error" in result.output

    def test_compare_files_with_tolerance(self, runner, temp_output_dir):
        """Test comparing files with numeric tolerance."""
        source_df = pl.DataFrame({"id": [1, 2], "value": [10.0, 20.0]})
        target_df = pl.DataFrame({"id": [1, 2], "value": [10.00001, 20.00001]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                    "--tolerance",
                    "0.001",
                ],
            )

            assert "100.00%" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_with_rows_only_in_source(self, runner, temp_output_dir):
        """Test output when rows exist only in source."""
        source_df = pl.DataFrame({"id": [1, 2, 3, 4], "value": [10, 20, 30, 40]})
        target_df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert "Rows only in source" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_with_rows_only_in_target(self, runner, temp_output_dir):
        """Test output when rows exist only in target."""
        source_df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})
        target_df = pl.DataFrame({"id": [1, 2, 3, 4], "value": [10, 20, 30, 40]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert "Rows only in target" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_with_mismatched_rows(self, runner, temp_output_dir):
        """Test output shows mismatched rows count."""
        source_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        target_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 99, 30]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert "Mismatched rows" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_csv_with_options(self, runner, temp_output_dir):
        """Test comparing CSV files with format options."""
        df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            target_path = f.name

        try:
            df.write_csv(source_path, separator=";")
            df.write_csv(target_path, separator="|")

            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                    "--source-options",
                    '{"delimiter": ";"}',
                    "--target-options",
                    '{"delimiter": "|"}',
                ],
            )

            assert "100.00%" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_file_load_error(self, runner, temp_output_dir):
        """Test error handling for file load errors."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            f.write(b"not a valid parquet file")
            source_path = f.name

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            pl.DataFrame({"id": [1]}).write_parquet(f.name)
            target_path = f.name

        try:
            result = runner.invoke(
                cli,
                [
                    "compare-files",
                    "-s",
                    source_path,
                    "-t",
                    target_path,
                    "-j",
                    "id",
                    "-o",
                    temp_output_dir,
                ],
            )

            assert result.exit_code != 0
            assert "Error" in result.output
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_unexpected_error(self, runner, temp_output_dir):
        """Test error handling for unexpected exceptions."""
        from unittest.mock import patch

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            pl.DataFrame({"id": [1]}).write_parquet(f.name)
            source_path = f.name

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            pl.DataFrame({"id": [1]}).write_parquet(f.name)
            target_path = f.name

        try:
            with patch(
                "pycaroline.loaders.api.compare_files",
                side_effect=RuntimeError("Unexpected error"),
            ):
                result = runner.invoke(
                    cli,
                    [
                        "compare-files",
                        "-s",
                        source_path,
                        "-t",
                        target_path,
                        "-j",
                        "id",
                        "-o",
                        temp_output_dir,
                    ],
                )

                # Should exit with error code
                assert result.exit_code != 0
        finally:
            os.unlink(source_path)
            os.unlink(target_path)
