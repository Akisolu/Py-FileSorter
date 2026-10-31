"""Group files in a folder into subdirectories named after their extensions."""

import pathlib
from dataclasses import dataclass, field
from typing import Literal

SkipReason = Literal["no_extension", "destination_exists"]


@dataclass(frozen=True)
class FileMove:
    source: pathlib.Path
    destination: pathlib.Path


@dataclass(frozen=True)
class SkippedFile:
    path: pathlib.Path
    reason: SkipReason
    destination: pathlib.Path | None = None


@dataclass
class SortResult:
    moved: list[FileMove] = field(default_factory=list)
    skipped: list[SkippedFile] = field(default_factory=list)


def sort_files_by_extension(path: str | pathlib.Path) -> SortResult:
    """Sort the files directly inside ``path`` into extension subfolders.

    Behavior contract (each rule is pinned by ``tests/test_sorter.py``):

    - Only files sitting directly in ``path`` are sorted; subfolders are
      left untouched.
    - ``backup.tar.gz`` is filed under ``gz`` (last extension wins).
    - Files without an extension, and dotfiles, stay where they are.
    - When the destination already holds a file with the same name the
      source keeps its place, the conflict is recorded, and sorting
      continues with the remaining files.
    - A missing ``path`` raises ``FileNotFoundError``; a ``path`` that is
      not a directory raises ``NotADirectoryError``.

    Returns the moved and skipped files so callers can present the result
    in a human-readable or machine-readable format.
    """
    path = pathlib.Path(path)
    result = SortResult()

    for f in path.iterdir():
        if f.is_dir():
            continue

        ext = f.suffix[1:]  # Get the extension without the leading dot
        if not ext:  # Policy: extension-less files and dotfiles stay put.
            result.skipped.append(SkippedFile(f, "no_extension"))
            continue

        ext_dir = path / ext  # Build the path for the extension directory

        ext_dir.mkdir(exist_ok=True)

        dst = ext_dir / f.name  # Build the destination path
        if dst.exists():  # Policy: never overwrite; warn and move on.
            result.skipped.append(SkippedFile(f, "destination_exists", dst))
            continue

        f.rename(dst)

        result.moved.append(FileMove(f, dst))

    return result
