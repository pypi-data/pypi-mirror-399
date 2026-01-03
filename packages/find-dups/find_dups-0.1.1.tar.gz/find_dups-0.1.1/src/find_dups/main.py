"""Find duplicates in a directory tree."""

import argparse
from pathlib import Path

from find_dups.utils import (
    fail_if_invalid,
    find_potential_duplicates,
    format_duplicate_report,
    normalize_extensions,
)


def main() -> None:
    """Application entry point."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files in a directory tree.",
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The root directory to search for duplicate files.",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        nargs="+",
        help="List of file extensions to include in the search.",
    )

    args = parser.parse_args()
    directory = Path(args.directory)
    extensions = normalize_extensions(args.extensions) if args.extensions else None
    fail_if_invalid(directory)

    duplicates = find_potential_duplicates(directory, extensions)
    print(format_duplicate_report(duplicates))


if __name__ == "__main__":
    main()
