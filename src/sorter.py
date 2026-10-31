"""Group files in a folder into subdirectories named after their extensions."""

import pathlib
import sys


def sort_files_by_extension(path):
    path = pathlib.Path(path)

    for f in path.iterdir():
        if f.is_dir():
            continue

        ext = f.suffix[1:]  # Get the extension without the leading dot
        ext_dir = path / ext  # Build the path for the extension directory

        ext_dir.mkdir(exist_ok=True)

        dst = ext_dir / f.name  # Build the destination path
        f.rename(dst)


def main(argv=None):
    """Entry point.

    Takes an optional path as the first CLI argument; when omitted it
    prompts for the path interactively.
    """
    if argv is None:
        argv = sys.argv[1:]

    if argv:
        input_path = argv[0]
    else:
        input_path = input("Enter the path to the directory: ")

    sort_files_by_extension(input_path)
    print("Files have been sorted by extension.")


if __name__ == "__main__":
    main()
