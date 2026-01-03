"""File dictionary utilities for the project."""

import hashlib
from pathlib import Path
from typing import Any


def get_files_by_size(files: list[Path]) -> dict[int, list[Path]]:
    """Group files by their size.

    Args:
        files (list[Path]): List of file paths.

    Returns:
        dict[int, list[Path]]: Dictionary mapping file sizes to lists of file paths.
    """
    size_dict: dict[int, list[Path]] = {}
    for file in files:
        size = file.stat().st_size
        if size not in size_dict:
            size_dict[size] = []
        size_dict[size].append(file)
    return size_dict


def prune_non_duplicates(
    files_dict: dict[Any, list[Path]],
) -> dict[Any, list[Path]]:
    """Remove entries from the size dictionary that do not have duplicates.

    Args:
        files_dict (dict[object, list[Path]]): Dictionary mapping some file metric
        to lists of file paths.

    Returns:
        dict[object, list[Path]]: Pruned dictionary with only entries that have
        potential duplicates.
    """
    return {metric: files for metric, files in files_dict.items() if len(files) > 1}


def get_files_by_hash(
    files_by_size_dict: dict[int | str, list[Path]],
) -> dict[str, list[Path]]:
    """Group files by their hash value.

    Args:
        files_by_size_dict (dict[int | str, list[Path]]): Dictionary mapping file sizes
          to lists of file paths.

    Returns:
        dict[int | str, list[Path]]: Dictionary mapping file hashes to lists of
          file paths.
    """
    hash_dict: dict[str, list[Path]] = {}

    for files in files_by_size_dict.values():
        for file in files:
            hasher = hashlib.md5()  # noqa: S324
            with file.open("rb") as f:
                # Read the file in chunks to avoid memory issues with large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            if file_hash not in hash_dict:
                hash_dict[file_hash] = []
            hash_dict[file_hash].append(file)

    return hash_dict


def get_files_by_name(files: list[Path]) -> dict[str, list[Path]]:
    """Group files by their name.

    Args:
        files (list[Path]): List of file paths.

    Returns:
        dict[str, list[Path]]: Dictionary mapping file names to lists of file paths.
    """
    name_dict: dict[str, list[Path]] = {}
    for file in files:
        name = file.name
        if name not in name_dict:
            name_dict[name] = []
        name_dict[name].append(file)
    return name_dict


def get_files_by_stem_diff_suffix(files: list[Path]) -> dict[str, list[Path]]:
    """Group files by their stem (name without extension) having different suffixes.

    Args:
        files (list[Path]): List of file paths.

    Returns:
        dict[str, list[Path]]: Dictionary mapping file stems to lists of file paths.
    """
    stem_dict: dict[str, list[Path]] = {}
    for file in files:
        stem = file.stem
        if stem not in stem_dict:
            stem_dict[stem] = []
        suffixes = {f.suffix for f in stem_dict[stem]}
        if file.suffix not in suffixes:
            stem_dict[stem].append(file)
    return stem_dict
