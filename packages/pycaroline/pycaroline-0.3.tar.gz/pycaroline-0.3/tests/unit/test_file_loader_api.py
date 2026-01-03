"""Unit tests for file loader public API functions.

Tests for load_file and compare_files functions.
"""

import os
import tempfile

import polars as pl
import pytest

from pycaroline import compare_files, load_file


class TestLoadFile:
    """Tests for the load_file function."""

    def test_load_csv_file(self):
        """Test loading a CSV file."""
        df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path)
            loaded = load_file(temp_path)

            assert loaded.shape == df.shape
            assert loaded.columns == df.columns
        finally:
            os.unlink(temp_path)

    def test_load_parquet_file(self):
        """Test loading a Parquet file."""
        df = pl.DataFrame({"id": [1, 2, 3], "value": [10.5, 20.5, 30.5]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_path = f.name

        try:
            df.write_parquet(temp_path)
            loaded = load_file(temp_path)

            assert loaded.shape == df.shape
            assert loaded.columns == df.columns
            assert loaded.equals(df)
        finally:
            os.unlink(temp_path)

    def test_load_json_file(self):
        """Test loading a JSON file."""
        df = pl.DataFrame({"id": [1, 2], "data": ["x", "y"]})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_json(temp_path)
            loaded = load_file(temp_path)

            assert loaded.shape == df.shape
        finally:
            os.unlink(temp_path)

    def test_load_ndjson_file(self):
        """Test loading an NDJSON file."""
        df = pl.DataFrame({"id": [1, 2, 3], "status": ["ok", "ok", "fail"]})

        with tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_ndjson(temp_path)
            loaded = load_file(temp_path)

            assert loaded.shape == df.shape
        finally:
            os.unlink(temp_path)

    def test_load_ipc_file(self):
        """Test loading an IPC file."""
        df = pl.DataFrame({"id": [1, 2], "value": [100, 200]})

        with tempfile.NamedTemporaryFile(suffix=".ipc", delete=False) as f:
            temp_path = f.name

        try:
            df.write_ipc(temp_path)
            loaded = load_file(temp_path)

            assert loaded.shape == df.shape
            assert loaded.equals(df)
        finally:
            os.unlink(temp_path)

    def test_load_with_explicit_format(self):
        """Test loading with explicit format override."""
        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        # Save as CSV but with .txt extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path)
            loaded = load_file(temp_path, format="csv")

            assert loaded.shape == df.shape
        finally:
            os.unlink(temp_path)

    def test_load_csv_with_options(self):
        """Test loading CSV with custom options."""
        df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path, separator=";")
            loaded = load_file(temp_path, delimiter=";")

            assert loaded.shape == df.shape
            assert list(loaded["id"]) == [1, 2]
        finally:
            os.unlink(temp_path)

    def test_load_file_not_found(self):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            load_file("/nonexistent/path/file.csv")

    def test_load_unsupported_format(self):
        """Test that ValueError is raised for unsupported formats."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False, mode="w") as f:
            f.write("test")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported"):
                load_file(temp_path)
        finally:
            os.unlink(temp_path)


class TestCompareFiles:
    """Tests for the compare_files function."""

    def test_compare_identical_files(self):
        """Test comparing two identical files."""
        df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            df.write_parquet(source_path)
            df.write_parquet(target_path)

            result = compare_files(source_path, target_path, join_columns=["id"])

            assert result.source_row_count == 3
            assert result.target_row_count == 3
            assert result.matching_rows == 3
            assert result.mismatched_rows == 0
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_files_with_differences(self):
        """Test comparing files with value differences."""
        source_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        target_df = pl.DataFrame({"id": [1, 2, 3], "value": [10, 25, 30]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            source_df.write_parquet(source_path)
            target_df.write_parquet(target_path)

            result = compare_files(source_path, target_path, join_columns=["id"])

            assert result.source_row_count == 3
            assert result.target_row_count == 3
            # Row with id=2 has different value
            assert result.mismatched_rows >= 1
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_different_formats(self):
        """Test comparing files with different formats."""
        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            target_path = f.name

        try:
            df.write_parquet(source_path)
            df.write_csv(target_path)

            result = compare_files(source_path, target_path, join_columns=["id"])

            assert result.source_row_count == 2
            assert result.target_row_count == 2
            assert result.matching_rows == 2
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_with_format_options(self):
        """Test comparing files with format-specific options."""
        df = pl.DataFrame({"id": [1, 2], "value": [100, 200]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            target_path = f.name

        try:
            df.write_csv(source_path, separator=";")
            df.write_csv(target_path, separator="|")

            result = compare_files(
                source_path,
                target_path,
                join_columns=["id"],
                source_options={"delimiter": ";"},
                target_options={"delimiter": "|"},
            )

            assert result.source_row_count == 2
            assert result.target_row_count == 2
            assert result.matching_rows == 2
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_with_tolerance(self):
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

            result = compare_files(
                source_path,
                target_path,
                join_columns=["id"],
                abs_tol=0.001,
            )

            assert result.matching_rows == 2
        finally:
            os.unlink(source_path)
            os.unlink(target_path)

    def test_compare_file_not_found(self):
        """Test that FileNotFoundError is raised for missing source file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("id,value\n1,10")
            target_path = f.name

        try:
            with pytest.raises(FileNotFoundError):
                compare_files(
                    "/nonexistent/source.csv",
                    target_path,
                    join_columns=["id"],
                )
        finally:
            os.unlink(target_path)

    def test_compare_returns_report_text(self):
        """Test that compare_files returns a report text."""
        df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            source_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            target_path = f.name

        try:
            df.write_parquet(source_path)
            df.write_parquet(target_path)

            result = compare_files(source_path, target_path, join_columns=["id"])

            assert result.report_text is not None
            assert len(result.report_text) > 0
        finally:
            os.unlink(source_path)
            os.unlink(target_path)
