"""Validation and normalization utilities for the project."""

import sys
from pathlib import Path


def normalize_extensions(extensions: list[str]) -> list[str]:
    """Normalize file extensions to ensure they start with a dot.

    Args:
        extensions (list[str]): List of file extensions.

    Returns:
        list[str]: Normalized list of file extensions.
    """
    return [ext if ext.startswith(".") else f".{ext}" for ext in extensions]


def fail_if_invalid(directory: Path) -> None:
    """Validate that the provided path is a directory.

    Args:
        directory (Path): The directory path to validate.
    """
    if not directory.exists():
        print(f"The directory '{directory}' does not exist.")
        sys.exit(1)
    if not directory.is_dir():
        print(f"The path '{directory}' is not a valid directory.")
        sys.exit(1)
