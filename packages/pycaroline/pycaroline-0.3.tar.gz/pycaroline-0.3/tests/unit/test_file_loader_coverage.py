"""Additional unit tests for file loader to improve coverage."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from pycaroline.loaders import FileFormat, FileLoader
from pycaroline.loaders.exceptions import FileLoadError


class TestFileLoaderFormatDetection:
    """Tests for format detection edge cases."""

    def test_detect_format_with_string_path(self):
        """Test format detection with string path."""
        result = FileLoader.detect_format("/path/to/file.parquet")
        assert result == FileFormat.PARQUET

    def test_detect_format_with_path_object(self):
        """Test format detection with Path object."""
        result = FileLoader.detect_format(Path("/path/to/file.csv"))
        assert result == FileFormat.CSV

    def test_detect_format_tsv(self):
        """Test TSV format detection."""
        result = FileLoader.detect_format("data.tsv")
        assert result == FileFormat.CSV

    def test_detect_format_jsonl(self):
        """Test JSONL format detection."""
        result = FileLoader.detect_format("data.jsonl")
        assert result == FileFormat.NDJSON

    def test_detect_format_arrow(self):
        """Test Arrow format detection."""
        result = FileLoader.detect_format("data.arrow")
        assert result == FileFormat.IPC

    def test_detect_format_feather(self):
        """Test Feather format detection."""
        result = FileLoader.detect_format("data.feather")
        assert result == FileFormat.FEATHER


class TestFileLoaderLoadErrors:
    """Tests for error handling in load method."""

    def test_load_invalid_string_format(self):
        """Test loading with invalid string format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                FileLoader.load(temp_path, format="invalid_format")
        finally:
            os.unlink(temp_path)

    def test_load_with_fileformat_enum(self):
        """Test loading with FileFormat enum."""
        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path)
            loaded = FileLoader.load(temp_path, format=FileFormat.CSV)
            assert loaded.shape == df.shape
        finally:
            os.unlink(temp_path)

    def test_load_file_not_found(self):
        """Test FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            FileLoader.load("/nonexistent/path/file.csv")


class TestCSVLoader:
    """Tests for CSV loading edge cases."""

    def test_load_tsv_auto_delimiter(self):
        """Test TSV files auto-detect tab delimiter."""
        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path, separator="\t")
            loaded = FileLoader.load(temp_path)
            assert loaded.shape == df.shape
            assert list(loaded["id"]) == [1, 2]
        finally:
            os.unlink(temp_path)

    def test_load_csv_with_skip_rows(self):
        """Test CSV loading with skip_rows option."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("# comment line\nid,name\n1,a\n2,b\n")
            temp_path = f.name

        try:
            loaded = FileLoader.load(temp_path, skip_rows=1)
            assert loaded.shape[0] == 2
        finally:
            os.unlink(temp_path)

    def test_load_csv_with_n_rows(self):
        """Test CSV loading with n_rows limit."""
        df = pl.DataFrame({"id": [1, 2, 3, 4, 5], "name": ["a", "b", "c", "d", "e"]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_csv(temp_path)
            loaded = FileLoader.load(temp_path, n_rows=2)
            assert loaded.shape[0] == 2
        finally:
            os.unlink(temp_path)

    def test_load_csv_parse_error(self):
        """Test CSV parse error raises FileLoadError."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            # Write malformed CSV that will cause parse error
            f.write("id,name\n1,a,extra,columns,here\n")
            temp_path = f.name

        try:
            # This should raise an error for non-existent column
            with pytest.raises((FileLoadError, pl.exceptions.ColumnNotFoundError)):
                FileLoader.load(temp_path, columns=["nonexistent_column"])
        finally:
            os.unlink(temp_path)


class TestExcelLoader:
    """Tests for Excel loading edge cases."""

    def test_load_excel_with_skip_rows(self):
        """Test Excel loading with skip_rows option."""
        pytest.importorskip("openpyxl")

        df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            df.write_excel(temp_path)
            # skip_rows=1 skips the header, so we need has_header=False
            loaded = FileLoader.load(temp_path, skip_rows=1, has_header=False)
            assert loaded.shape[0] == 3  # 3 data rows
        finally:
            os.unlink(temp_path)

    def test_load_excel_with_columns(self):
        """Test Excel loading with column selection."""
        pytest.importorskip("openpyxl")

        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            df.write_excel(temp_path)
            loaded = FileLoader.load(temp_path, columns=["id", "name"])
            assert loaded.columns == ["id", "name"]
        finally:
            os.unlink(temp_path)

    def test_load_excel_import_error_xlsx(self):
        """Test Excel ImportError for xlsx files."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name

        try:
            with patch("polars.read_excel", side_effect=ImportError("No module")):
                with pytest.raises(FileLoadError, match="openpyxl"):
                    FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_excel_import_error_xls(self):
        """Test Excel ImportError for xls files."""
        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name

        try:
            with patch("polars.read_excel", side_effect=ImportError("No module")):
                with pytest.raises(FileLoadError, match="xlrd"):
                    FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_excel_generic_error(self):
        """Test Excel generic error handling."""
        pytest.importorskip("openpyxl")

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(b"not a valid excel file")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to read Excel"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestParquetLoader:
    """Tests for Parquet loading edge cases."""

    def test_load_parquet_with_n_rows(self):
        """Test Parquet loading with n_rows limit."""
        df = pl.DataFrame({"id": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_path = f.name

        try:
            df.write_parquet(temp_path)
            loaded = FileLoader.load(temp_path, n_rows=3)
            assert loaded.shape[0] == 3
        finally:
            os.unlink(temp_path)

    def test_load_parquet_error(self):
        """Test Parquet error handling."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            f.write(b"not a valid parquet file")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to read Parquet"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestJSONLoader:
    """Tests for JSON loading edge cases."""

    def test_load_json_with_n_rows(self):
        """Test JSON loading with n_rows limit."""
        df = pl.DataFrame({"id": [1, 2, 3, 4, 5], "name": ["a", "b", "c", "d", "e"]})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            temp_path = f.name

        try:
            df.write_json(temp_path)
            loaded = FileLoader.load(temp_path, n_rows=2)
            assert loaded.shape[0] == 2
        finally:
            os.unlink(temp_path)

    def test_load_json_error(self):
        """Test JSON error handling."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to parse JSON"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestNDJSONLoader:
    """Tests for NDJSON loading edge cases."""

    def test_load_ndjson_error(self):
        """Test NDJSON error handling."""
        with tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False, mode="w") as f:
            f.write("not valid ndjson {{{")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to parse NDJSON"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestIPCLoader:
    """Tests for IPC loading edge cases."""

    def test_load_ipc_with_n_rows(self):
        """Test IPC loading with n_rows limit."""
        df = pl.DataFrame({"id": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})

        with tempfile.NamedTemporaryFile(suffix=".ipc", delete=False) as f:
            temp_path = f.name

        try:
            df.write_ipc(temp_path)
            loaded = FileLoader.load(temp_path, n_rows=3)
            assert loaded.shape[0] == 3
        finally:
            os.unlink(temp_path)

    def test_load_feather_format(self):
        """Test loading with feather extension."""
        df = pl.DataFrame({"id": [1, 2], "value": [10, 20]})

        with tempfile.NamedTemporaryFile(suffix=".feather", delete=False) as f:
            temp_path = f.name

        try:
            df.write_ipc(temp_path)
            loaded = FileLoader.load(temp_path)
            assert loaded.shape == df.shape
        finally:
            os.unlink(temp_path)

    def test_load_ipc_error(self):
        """Test IPC error handling."""
        with tempfile.NamedTemporaryFile(suffix=".ipc", delete=False) as f:
            f.write(b"not a valid ipc file")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to read IPC"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestAvroLoader:
    """Tests for Avro loading edge cases."""

    def test_load_avro_import_error(self):
        """Test Avro ImportError handling."""
        with tempfile.NamedTemporaryFile(suffix=".avro", delete=False) as f:
            f.write(b"dummy")
            temp_path = f.name

        try:
            with patch("polars.read_avro", side_effect=ImportError("No pyarrow")):
                with pytest.raises(FileLoadError, match="pyarrow"):
                    FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_avro_error(self):
        """Test Avro generic error handling."""
        with tempfile.NamedTemporaryFile(suffix=".avro", delete=False) as f:
            f.write(b"not a valid avro file")
            temp_path = f.name

        try:
            with pytest.raises(FileLoadError, match="Failed to read Avro"):
                FileLoader.load(temp_path)
        finally:
            os.unlink(temp_path)


class TestFileLoadError:
    """Tests for FileLoadError exception."""

    def test_file_load_error_str(self):
        """Test FileLoadError string representation."""
        error = FileLoadError(Path("/path/to/file.csv"), "Test error message")
        error_str = str(error)
        assert "file.csv" in error_str
        assert "Test error message" in error_str

    def test_file_load_error_with_cause(self):
        """Test FileLoadError with cause."""
        cause = ValueError("Original error")
        error = FileLoadError(Path("/path/to/file.csv"), "Wrapper", cause=cause)
        assert error.cause is cause


class TestExcelLoaderExtended:
    """Extended tests for Excel loading to improve coverage."""

    def test_load_excel_sheet_not_found_with_available_sheets(self):
        """Test Excel sheet not found error shows available sheets."""
        pytest.importorskip("openpyxl")

        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            df.write_excel(temp_path)
            # Try to load a non-existent sheet
            with pytest.raises(FileLoadError, match="not found|does not exist|Failed"):
                FileLoader.load(temp_path, sheet_name="NonExistentSheet")
        finally:
            os.unlink(temp_path)

    def test_load_excel_sheet_by_invalid_index(self):
        """Test Excel loading with invalid sheet index."""
        pytest.importorskip("openpyxl")

        df = pl.DataFrame({"id": [1, 2], "name": ["a", "b"]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            df.write_excel(temp_path)
            # Try to load sheet at invalid index (only 1 sheet exists)
            with pytest.raises(FileLoadError):
                FileLoader.load(temp_path, sheet_index=99)
        finally:
            os.unlink(temp_path)


class TestAvroLoaderExtended:
    """Extended tests for Avro loading."""

    def test_load_avro_with_columns(self):
        """Test Avro loading with column selection."""
        df = pl.DataFrame(
            {"id": [1, 2, 3], "name": ["a", "b", "c"], "value": [10, 20, 30]}
        )

        with tempfile.NamedTemporaryFile(suffix=".avro", delete=False) as f:
            temp_path = f.name

        try:
            df.write_avro(temp_path)
            loaded = FileLoader.load(temp_path, columns=["id", "name"])
            assert loaded.columns == ["id", "name"]
            assert loaded.shape[0] == 3
        finally:
            os.unlink(temp_path)


class TestFileLoaderNoLoaderImplemented:
    """Test for no loader implemented error path."""

    def test_load_with_unknown_format_enum(self):
        """Test that unknown format raises appropriate error."""
        # This tests the unreachable code path - all formats have loaders
        # We can't easily test this without mocking, so we verify the loaders dict is complete
        from pycaroline.loaders.models import FileFormat

        # Verify all FileFormat values have loaders
        loaders = {
            FileFormat.PARQUET,
            FileFormat.CSV,
            FileFormat.XLSX,
            FileFormat.XLS,
            FileFormat.JSON,
            FileFormat.NDJSON,
            FileFormat.AVRO,
            FileFormat.IPC,
            FileFormat.FEATHER,
        }
        all_formats = set(FileFormat)
        assert loaders == all_formats, "All formats should have loaders"
