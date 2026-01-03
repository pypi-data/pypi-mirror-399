"""Report utilities for the project."""

from pathlib import Path

from find_dups.utils.fileutils import DupFileReasonEnum


def format_duplicate_report(
    duplicates: dict[DupFileReasonEnum, dict[str, list[Path]]],
) -> str:
    """Format a report of potential duplicate files.

    Args:
        duplicates (dict[DupFileReasonEnum, list[list[Path]]]): Dictionary mapping
          duplicate reasons to lists of file paths.

    Returns:
        str: Formatted report string.
    """
    report_lines = []
    for reason, files_dict in duplicates.items():
        report_lines.append(f"Reason: {reason.value}")
        if not files_dict:
            report_lines.append("    No potential duplicates found.\n")
            continue
        for _, files in files_dict.items():  # noqa: PERF102
            report_lines.extend([f"    - {file}" for file in files])
            report_lines.append("")  # Add an empty line between groups of duplicates
        report_lines.append("")  # Add an empty line between reasons
    return "\n".join(report_lines)
