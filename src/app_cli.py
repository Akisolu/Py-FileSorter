"""Command-line interface for Py-FileSorter.

Runs without arguments it prints a mini quick guide. Use ``-d/--dir`` to
sort a directory; ``--version`` and ``--help`` round out the flags.

"""

import argparse
import pathlib
import sys
from importlib import metadata

import sorter

PROG = "py-filesorter"


def _version() -> str:
    """Distribution version, with a fallback when running outside an install."""
    try:
        return metadata.version("py-filesorter")
    except metadata.PackageNotFoundError:
        return "0.1.0"


MINI_GUIDE = f"""\
{PROG} v{_version()} — sort files in a folder into subfolders by extension.

Quick guide:
  {PROG} -d <directory>    sort the files of <directory>
  {PROG} --version, -v     show the version
  {PROG} --help, -h        show the full help

Example:
  {PROG} -d C:\\Users\\you\\Downloads
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Sort files into subdirectories named after their extensions.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        metavar="DIR",
        help="directory whose files will be sorted",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{PROG} v{_version()}",
    )
    return parser


def main(argv=None) -> int:
    """Entry point. Returns a process exit code."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:  # Running the executable bare equals the mini quick guide.
        print(MINI_GUIDE, end="")
        return 0

    args = build_parser().parse_args(argv)

    target = pathlib.Path(args.dir)
    if not target.is_dir():
        print(f"error: '{args.dir}' is not a directory", file=sys.stderr)
        return 2

    sorter.sort_files_by_extension(target)
    print("Files have been sorted by extension.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
