"""Exceptions for file loading.

This module defines custom exceptions for file loading operations.
"""

from pathlib import Path


class FileLoadError(Exception):
    """Raised when a file cannot be loaded.

    This exception is raised when a file cannot be loaded due to:
    - Corrupted or malformed file content
    - Missing required dependencies for a format (e.g., openpyxl for Excel)
    - Invalid format-specific options

    Attributes:
        path: The path to the file that failed to load.
        message: A description of what went wrong.
        cause: The underlying exception that caused the failure, if any.
    """

    def __init__(
        self,
        path: Path | str,
        message: str,
        cause: Exception | None = None,
    ) -> None:
        """Initialize FileLoadError.

        Args:
            path: The path to the file that failed to load.
            message: A description of what went wrong.
            cause: The underlying exception that caused the failure.
        """
        self.path = Path(path) if isinstance(path, str) else path
        self.message = message
        self.cause = cause
        super().__init__(f"Failed to load {path}: {message}")
