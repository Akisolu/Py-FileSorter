"""Command-line interface for Py-FileSorter.

Runs without arguments it prints a colored mini quick guide. Use
``-d/--dir`` to sort a directory; ``--version`` and ``--help`` round out
the flags. Colors are dropped automatically when the output is not a
terminal or ``NO_COLOR`` is set.

``app_gui.py`` (graphical interface) is planned to live alongside it.
"""

import argparse
import json
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
        return "1.1.2"


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
        f"  {paint(f'{PROG} -d <directory> --json', YELLOW, colored)}"
        + f"  {paint('write a machine-readable result', DIM, colored)}",
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
    parser.add_argument(
        "--json",
        action="store_true",
        help=paint("write the sorting result as JSON", YELLOW, colored),
    )
    return parser


def _json_error(code: str, message: str, **details) -> str:
    return json.dumps(
        {"status": "error", "error": {"code": code, "message": message, **details}},
        ensure_ascii=False,
    )


def _json_result(directory: pathlib.Path, result: sorter.SortResult) -> str:
    skipped = [
        {
            "path": str(item.path),
            "reason": item.reason,
            **(
                {"destination": str(item.destination)}
                if item.destination is not None
                else {}
            ),
        }
        for item in result.skipped
    ]
    conflicts = any(item.reason == "destination_exists" for item in result.skipped)
    return json.dumps(
        {
            "status": "completed_with_warnings" if conflicts else "completed",
            "directory": str(directory),
            "summary": {
                "moved": len(result.moved),
                "skipped": len(result.skipped),
            },
            "moved": [
                {"source": str(item.source), "destination": str(item.destination)}
                for item in result.moved
            ],
            "skipped": skipped,
        },
        ensure_ascii=False,
    )


def _human_summary(result: sorter.SortResult, directory: pathlib.Path) -> str:
    moved = len(result.moved)
    if moved:
        message = f"Files have been sorted by extension. Moved {moved} file(s)."
    else:
        message = f"No files were moved from '{directory}'."

    no_extension = sum(item.reason == "no_extension" for item in result.skipped)
    if no_extension:
        message += f" Left {no_extension} file(s) without an extension unchanged."

    return message


def main(argv=None) -> int:
    """Entry point. Returns a process exit code."""
    colorama.just_fix_windows_console()

    if argv is None:
        argv = sys.argv[1:]

    if not argv:  # Running the executable bare equals the mini quick guide.
        print(mini_guide(use_color()))
        return 0

    args = build_parser(use_color()).parse_args(argv)

    if args.dir is None:
        message = "A directory is required. Use --dir DIR to choose one."
        if args.json:
            print(_json_error("missing_directory", message))
        else:
            print(
                paint(f"error: {message}", RED, use_color(sys.stderr)),
                file=sys.stderr,
            )
        return 2

    target = pathlib.Path(args.dir)
    if not target.is_dir():
        message = f"'{args.dir}' is not a directory"
        if args.json:
            print(
                _json_error(
                    "not_a_directory",
                    message,
                    path=str(target),
                )
            )
        else:
            print(
                paint(f"error: {message}", RED, use_color(sys.stderr)),
                file=sys.stderr,
            )
        return 2

    try:
        result = sorter.sort_files_by_extension(target)
    except OSError as exc:
        if args.json:
            print(
                _json_error(
                    "filesystem_error",
                    str(exc),
                    partial_changes_possible=True,
                )
            )
        else:
            print(
                paint(
                    "error: sorting failed; some files may already have been "
                    f"moved: {exc}",
                    RED,
                    use_color(sys.stderr),
                ),
                file=sys.stderr,
            )
        return 1

    if args.json:
        print(_json_result(target, result))
        return 0

    print(paint(_human_summary(result, target), GREEN, use_color()))
    for item in result.skipped:
        if item.reason == "destination_exists":
            print(
                paint(
                    f"warning: '{item.path.name}' was left in place because "
                    f"'{item.destination}' already exists.",
                    YELLOW,
                    use_color(sys.stderr),
                ),
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
