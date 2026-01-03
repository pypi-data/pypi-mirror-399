"""File utilities for the project."""

from enum import Enum
from pathlib import Path

from find_dups.utils.file_dict_utils import (
    get_files_by_hash,
    get_files_by_name,
    get_files_by_size,
    get_files_by_stem_diff_suffix,
    prune_non_duplicates,
)


class DupFileReasonEnum(Enum):
    """Enum for potential duplicate file reasons."""

    SAME_SIZE_AND_HASH = "same size and hash"
    SAME_NAME = "same name"
    SAME_STEM_DIFF_SUFFIX = "same stem different suffix"


def get_files(directory: Path, extensions: list[str] | None = None) -> list[Path]:
    """Retrieve files from the directory, optionally filtering by extensions.

    Args:
        directory (Path): The root directory to search.
        extensions (list[str] | None): List of file extensions to filter by.

    Returns:
        list[Path]: List of file paths.
    """
    return [
        f
        for f in directory.rglob("*")
        if f.is_file() and (extensions is None or f.suffix in extensions)
    ]


def find_potential_duplicates(
    directory: Path,
    extensions: list[str] | None = None,
) -> dict[DupFileReasonEnum, dict[str, list[Path]]]:
    """Find potential duplicate files using different strategies.

    Args:
        directory (Path): The root directory to search.
        extensions (list[str] | None): List of file extensions to filter by.

    Returns:
        list[list[Path]]: List of lists of file paths that are potential duplicates.
    """
    files = get_files(directory, extensions)
    by_size_dups_dict = prune_non_duplicates(get_files_by_size(files))
    by_md5_dups_dict = prune_non_duplicates(get_files_by_hash(by_size_dups_dict))
    by_name_dups_dict = prune_non_duplicates(get_files_by_name(files))
    by_stem_dups_dict = prune_non_duplicates(get_files_by_stem_diff_suffix(files))

    return {
        DupFileReasonEnum.SAME_SIZE_AND_HASH: by_md5_dups_dict,
        DupFileReasonEnum.SAME_NAME: by_name_dups_dict,
        DupFileReasonEnum.SAME_STEM_DIFF_SUFFIX: by_stem_dups_dict,
    }
