"""Command-line interface for Py-FileSorter.

Runs without arguments it prints a colored mini quick guide. Use
``-d/--dir`` to sort a directory; ``--version`` and ``--help`` round out
the flags. Colors are dropped automatically when the output is not a
terminal or ``NO_COLOR`` is set.

``app_gui.py`` (graphical interface) is planned to live alongside it.
"""

import argparse
import os
import pathlib
import sys
from importlib import metadata

import colorama

import sorter

PROG = "py-filesorter"


def _version() -> str:
    """Distribution version, with a fallback when running outside an install."""
    try:
        return metadata.version("py-filesorter")
    except metadata.PackageNotFoundError:
        return "0.1.0"


# SGR codes: (1) bold, (2) dim, (31) red, (32) green, (36) cyan, (33) yellow
BOLD, DIM = "1", "2"
RED, GREEN, CYAN, YELLOW = "31", "32", "36", "33"


def paint(text: str, code: str, colored: bool) -> str:
    """Wrap ``text`` in ANSI ``code``; plain text when colors are off."""
    return f"\x1b[{code}m{text}\x1b[0m" if colored else text


def use_color(stream=None) -> bool:
    """Colors only when the stream is interactive, unless ``NO_COLOR`` is set."""
    if stream is None:
        stream = sys.stdout
    return stream.isatty() and not os.environ.get("NO_COLOR")


def mini_guide(colored: bool) -> str:
    """The quick guide an interpreter sees when running the executable bare."""
    lines = [
        paint(f"{PROG} v{_version()}", f"{BOLD};{CYAN}", colored)
        + " — sort files in a folder into subfolders by extension.",
        "",
        paint("Quick guide:", BOLD, colored),
        f"  {paint(f'{PROG} -d <directory>', YELLOW, colored)}"
        + "    sort the files of <directory>",
        f"  {paint(f'{PROG} --version, -v', YELLOW, colored)}"
        + f"  {paint('show the version', DIM, colored)}",
        f"  {paint(f'{PROG} --help, -h', YELLOW, colored)}"
        + f"     {paint('show the full help', DIM, colored)}",
        "",
        paint("Example:", BOLD, colored),
        f"  {paint(f'{PROG} -d C:\\Users\\you\\Downloads', GREEN, colored)}",
        "",
    ]
    return "\n".join(lines)


def build_parser(colored: bool) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=paint(
            "Sort files into subdirectories named after their extensions.",
            CYAN,
            colored,
        ),
    )
    parser.add_argument(
        "-d",
        "--dir",
        metavar="DIR",
        help=paint("directory whose files will be sorted", YELLOW, colored),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=paint(f"{PROG} v{_version()}", BOLD, colored),
    )
    return parser


def main(argv=None) -> int:
    """Entry point. Returns a process exit code."""
    colorama.just_fix_windows_console()

    if argv is None:
        argv = sys.argv[1:]

    if not argv:  # Running the executable bare equals the mini quick guide.
        print(mini_guide(use_color()))
        return 0

    args = build_parser(use_color()).parse_args(argv)

    target = pathlib.Path(args.dir)
    if not target.is_dir():
        print(
            paint(
                f"error: '{args.dir}' is not a directory",
                RED,
                use_color(sys.stderr),
            ),
            file=sys.stderr,
        )
        return 2

    sorter.sort_files_by_extension(target)
    print("Files have been sorted by extension.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
