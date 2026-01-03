"""Data models for file loading.

This module defines the FileFormat enum for supported file formats.
"""

from enum import Enum


class FileFormat(Enum):
    """Supported file formats for loading.

    Each format corresponds to a specific file type that can be loaded
    into a polars DataFrame.
    """

    PARQUET = "parquet"
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    JSON = "json"
    NDJSON = "ndjson"
    AVRO = "avro"
    IPC = "ipc"
    FEATHER = "feather"
