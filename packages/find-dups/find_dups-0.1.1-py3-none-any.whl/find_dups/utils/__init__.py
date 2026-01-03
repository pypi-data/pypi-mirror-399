"""__init__.py file for the utils package."""

from find_dups.utils.fileutils import DupFileReasonEnum, find_potential_duplicates
from find_dups.utils.report import format_duplicate_report
from find_dups.utils.validation import fail_if_invalid, normalize_extensions

__all__ = [
    "DupFileReasonEnum",
    "fail_if_invalid",
    "find_potential_duplicates",
    "format_duplicate_report",
    "normalize_extensions",
]
