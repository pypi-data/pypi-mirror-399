"""File loaders for pycaroline.

This module provides functionality for loading various file formats
into polars DataFrames for comparison and validation.

Supported formats:
- Parquet (.parquet)
- CSV (.csv, .tsv)
- Excel (.xlsx, .xls)
- JSON (.json)
- NDJSON (.ndjson, .jsonl)
- Avro (.avro)
- IPC/Feather (.ipc, .feather, .arrow)
"""

from pycaroline.loaders.api import compare_files, load_file
from pycaroline.loaders.exceptions import FileLoadError
from pycaroline.loaders.file_loader import FileLoader
from pycaroline.loaders.models import FileFormat

__all__ = [
    "FileFormat",
    "FileLoadError",
    "FileLoader",
    "compare_files",
    "load_file",
]
