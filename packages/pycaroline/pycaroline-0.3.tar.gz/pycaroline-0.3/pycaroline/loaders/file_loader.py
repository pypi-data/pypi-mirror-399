"""File loader for loading various file formats into polars DataFrames.

This module provides the FileLoader class which handles format detection
and loading of files into polars DataFrames.
"""

from pathlib import Path
from typing import Any

import polars as pl

from pycaroline.loaders.exceptions import FileLoadError
from pycaroline.loaders.models import FileFormat


class FileLoader:
    """Loads files into polars DataFrames with format auto-detection.

    This class provides methods to detect file formats from extensions
    and load files into polars DataFrames with format-specific options.

    Supported formats:
    - Parquet (.parquet)
    - CSV (.csv, .tsv)
    - Excel (.xlsx, .xls)
    - JSON (.json)
    - NDJSON (.ndjson, .jsonl)
    - Avro (.avro)
    - IPC/Feather (.ipc, .feather, .arrow)
    """

    # Extension to format mapping
    EXTENSION_MAP: dict[str, FileFormat] = {
        ".parquet": FileFormat.PARQUET,
        ".csv": FileFormat.CSV,
        ".tsv": FileFormat.CSV,  # TSV treated as CSV with tab delimiter
        ".xlsx": FileFormat.XLSX,
        ".xls": FileFormat.XLS,
        ".json": FileFormat.JSON,
        ".ndjson": FileFormat.NDJSON,
        ".jsonl": FileFormat.NDJSON,
        ".avro": FileFormat.AVRO,
        ".ipc": FileFormat.IPC,
        ".feather": FileFormat.FEATHER,
        ".arrow": FileFormat.IPC,
    }

    @classmethod
    def detect_format(cls, path: Path | str) -> FileFormat:
        """Detect file format from extension.

        Args:
            path: Path to the file.

        Returns:
            FileFormat enum value for the detected format.

        Raises:
            ValueError: If the file extension is not supported.
        """
        path = Path(path) if isinstance(path, str) else path
        extension = path.suffix.lower()

        if extension not in cls.EXTENSION_MAP:
            supported = sorted(set(cls.EXTENSION_MAP.keys()))
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported: {', '.join(supported)}"
            )

        return cls.EXTENSION_MAP[extension]

    @classmethod
    def load(
        cls,
        path: str | Path,
        format: FileFormat | str | None = None,
        **options: Any,
    ) -> pl.DataFrame:
        """Load a file into a polars DataFrame.

        Args:
            path: Path to the file to load.
            format: Optional format override. If None, auto-detects from extension.
                Can be a FileFormat enum or string (e.g., "csv", "parquet").
            **options: Format-specific options passed to the loader.

        Returns:
            Polars DataFrame containing the file data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the format is not supported.
            FileLoadError: If the file cannot be loaded.
        """
        path = Path(path) if isinstance(path, str) else path

        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Determine format
        if format is not None:
            if isinstance(format, str):
                try:
                    file_format = FileFormat(format.lower())
                except ValueError as e:
                    valid_formats = [f.value for f in FileFormat]
                    raise ValueError(
                        f"Unsupported file format: {format}. "
                        f"Supported: {', '.join(valid_formats)}"
                    ) from e
            else:
                file_format = format
        else:
            file_format = cls.detect_format(path)

        # Dispatch to format-specific loader
        loaders = {
            FileFormat.PARQUET: cls._load_parquet,
            FileFormat.CSV: cls._load_csv,
            FileFormat.XLSX: cls._load_excel,
            FileFormat.XLS: cls._load_excel,
            FileFormat.JSON: cls._load_json,
            FileFormat.NDJSON: cls._load_ndjson,
            FileFormat.AVRO: cls._load_avro,
            FileFormat.IPC: cls._load_ipc,
            FileFormat.FEATHER: cls._load_ipc,
        }

        loader = loaders.get(file_format)
        if loader is None:
            raise ValueError(f"No loader implemented for format: {file_format.value}")

        return loader(path, **options)

    @classmethod
    def _load_csv(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load CSV file with options.

        Args:
            path: Path to the CSV file.
            **options: CSV-specific options:
                - delimiter: Field delimiter (default: ",")
                - has_header: Whether first row is header (default: True)
                - encoding: File encoding (default: "utf-8")
                - skip_rows: Number of rows to skip (default: 0)
                - n_rows: Maximum rows to read (default: None)
                - columns: Specific columns to load (default: None)

        Returns:
            Polars DataFrame containing the CSV data.

        Raises:
            FileLoadError: If the CSV cannot be parsed.
        """
        try:
            # Extract options with defaults
            delimiter = options.get("delimiter", ",")
            has_header = options.get("has_header", True)
            encoding = options.get("encoding", "utf-8")
            skip_rows = options.get("skip_rows", 0)
            n_rows = options.get("n_rows")
            columns = options.get("columns")

            # Handle TSV files - auto-detect tab delimiter from extension
            if path.suffix.lower() == ".tsv" and "delimiter" not in options:
                delimiter = "\t"

            return pl.read_csv(
                path,
                separator=delimiter,
                has_header=has_header,
                encoding=encoding,
                skip_rows=skip_rows,
                n_rows=n_rows,
                columns=columns,
            )
        except Exception as e:
            raise FileLoadError(path, f"Failed to parse CSV: {e}", cause=e) from e

    @classmethod
    def _load_excel(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load Excel file with options.

        Args:
            path: Path to the Excel file.
            **options: Excel-specific options:
                - sheet_name: Sheet name to load (default: None, loads first)
                - sheet_index: Sheet index to load (default: 0)
                - has_header: Whether first row is header (default: True)
                - skip_rows: Number of rows to skip (default: 0)
                - columns: Specific columns to load (default: None)

        Returns:
            Polars DataFrame containing the Excel data.

        Raises:
            FileLoadError: If the Excel file cannot be read.
        """
        try:
            sheet_name = options.get("sheet_name")
            sheet_index = options.get("sheet_index", 0)
            has_header = options.get("has_header", True)
            skip_rows = options.get("skip_rows", 0)
            columns = options.get("columns")

            # Determine which sheet to load
            # sheet_name takes precedence over sheet_index
            sheet_id = sheet_name if sheet_name is not None else sheet_index

            # Build read_excel kwargs
            read_kwargs: dict[str, Any] = {
                "source": path,
                "sheet_id": sheet_id,
                "has_header": has_header,
            }

            # Handle skip_rows - polars uses read_options for this
            if skip_rows > 0:
                read_kwargs["read_options"] = {"skip_rows": skip_rows}

            # Handle columns selection
            if columns is not None:
                read_kwargs["columns"] = columns

            result: pl.DataFrame = pl.read_excel(**read_kwargs)
            return result

        except ImportError as e:
            # Provide helpful error for missing dependencies
            ext = path.suffix.lower()
            if ext == ".xlsx":
                raise FileLoadError(
                    path,
                    "Excel (.xlsx) support requires openpyxl. "
                    "Install with: pip install openpyxl",
                    cause=e,
                ) from e
            elif ext == ".xls":
                raise FileLoadError(
                    path,
                    "Excel (.xls) support requires xlrd. "
                    "Install with: pip install xlrd",
                    cause=e,
                ) from e
            else:
                raise FileLoadError(
                    path,
                    f"Excel support requires additional dependencies: {e}",
                    cause=e,
                ) from e
        except Exception as e:
            # Check if it's a sheet not found error
            error_str = str(e).lower()
            if "sheet" in error_str and (
                "not found" in error_str or "does not exist" in error_str
            ):
                # Try to get available sheets for a better error message
                try:
                    import openpyxl

                    wb = openpyxl.load_workbook(path, read_only=True)
                    available_sheets = wb.sheetnames
                    wb.close()
                    raise FileLoadError(
                        path,
                        f"Sheet '{sheet_name or sheet_index}' not found. "
                        f"Available: {', '.join(available_sheets)}",
                        cause=e,
                    )
                except FileLoadError:
                    raise
                except Exception:  # nosec B110
                    pass
            raise FileLoadError(path, f"Failed to read Excel: {e}", cause=e) from e

    @classmethod
    def _load_parquet(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load Parquet file with options.

        Args:
            path: Path to the Parquet file.
            **options: Parquet-specific options:
                - columns: Specific columns to load (default: None)
                - n_rows: Maximum rows to read (default: None)

        Returns:
            Polars DataFrame containing the Parquet data.

        Raises:
            FileLoadError: If the Parquet file cannot be read.
        """
        try:
            columns = options.get("columns")
            n_rows = options.get("n_rows")

            return pl.read_parquet(
                path,
                columns=columns,
                n_rows=n_rows,
            )
        except Exception as e:
            raise FileLoadError(path, f"Failed to read Parquet: {e}", cause=e) from e

    @classmethod
    def _load_json(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load JSON file.

        Args:
            path: Path to the JSON file.
            **options: JSON-specific options:
                - n_rows: Maximum rows to read (default: None)

        Returns:
            Polars DataFrame containing the JSON data.

        Raises:
            FileLoadError: If the JSON file cannot be parsed.
        """
        try:
            n_rows = options.get("n_rows")

            df = pl.read_json(path)

            # Apply n_rows limit if specified
            if n_rows is not None:
                df = df.head(n_rows)

            return df
        except Exception as e:
            raise FileLoadError(path, f"Failed to parse JSON: {e}", cause=e) from e

    @classmethod
    def _load_ndjson(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load newline-delimited JSON file.

        Args:
            path: Path to the NDJSON file.
            **options: NDJSON-specific options:
                - n_rows: Maximum rows to read (default: None)

        Returns:
            Polars DataFrame containing the NDJSON data.

        Raises:
            FileLoadError: If the NDJSON file cannot be parsed.
        """
        try:
            n_rows = options.get("n_rows")

            return pl.read_ndjson(
                path,
                n_rows=n_rows,
            )
        except Exception as e:
            raise FileLoadError(path, f"Failed to parse NDJSON: {e}", cause=e) from e

    @classmethod
    def _load_avro(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load Avro file.

        Args:
            path: Path to the Avro file.
            **options: Avro-specific options:
                - columns: Specific columns to load (default: None)

        Returns:
            Polars DataFrame containing the Avro data.

        Raises:
            FileLoadError: If the Avro file cannot be read.
        """
        try:
            columns = options.get("columns")

            df = pl.read_avro(path, columns=columns)

            return df
        except ImportError as e:
            raise FileLoadError(
                path,
                "Avro support requires pyarrow. " "Install with: pip install pyarrow",
                cause=e,
            ) from e
        except Exception as e:
            raise FileLoadError(path, f"Failed to read Avro: {e}", cause=e) from e

    @classmethod
    def _load_ipc(cls, path: Path, **options: Any) -> pl.DataFrame:
        """Load IPC/Feather file.

        Args:
            path: Path to the IPC/Feather file.
            **options: IPC-specific options:
                - columns: Specific columns to load (default: None)
                - n_rows: Maximum rows to read (default: None)

        Returns:
            Polars DataFrame containing the IPC data.

        Raises:
            FileLoadError: If the IPC file cannot be read.
        """
        try:
            columns = options.get("columns")
            n_rows = options.get("n_rows")

            return pl.read_ipc(
                path,
                columns=columns,
                n_rows=n_rows,
            )
        except Exception as e:
            raise FileLoadError(
                path, f"Failed to read IPC/Feather: {e}", cause=e
            ) from e
