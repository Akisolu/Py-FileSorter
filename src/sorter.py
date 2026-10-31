"""Group files in a folder into subdirectories named after their extensions."""

import pathlib
import sys


def sort_files_by_extension(path):
    """Sort the files directly inside ``path`` into extension subfolders.

    Behavior contract (each rule is pinned by ``tests/test_sorter.py``):

    - Only files sitting directly in ``path`` are sorted; subfolders are
      left untouched.
    - ``backup.tar.gz`` is filed under ``gz`` (last extension wins).
    - Files without an extension, and dotfiles, stay where they are.
    - When the destination already holds a file with the same name the
      source keeps its place, a warning goes to stderr, and sorting
      continues with the remaining files.
    - A missing ``path`` raises ``FileNotFoundError``; a ``path`` that is
      not a directory raises ``NotADirectoryError``.
    """
    path = pathlib.Path(path)

    for f in path.iterdir():
        if f.is_dir():
            continue

        ext = f.suffix[1:]  # Get the extension without the leading dot
        if not ext:  # Policy: extension-less files and dotfiles stay put.
            continue

        ext_dir = path / ext  # Build the path for the extension directory

        ext_dir.mkdir(exist_ok=True)

        dst = ext_dir / f.name  # Build the destination path
        if dst.exists():  # Policy: never overwrite; warn and move on.
            print(
                f"warning: '{f.name}' already exists inside '{ext}', skipped",
                file=sys.stderr,
            )
            continue

        f.rename(dst)
