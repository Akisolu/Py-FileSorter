
# Py-FileSorter Roadmap

This document tracks planned testing, architecture improvements, and future
features for Py-FileSorter.

## Planned testing

1. Add direct CLI tests for `--help` and `-h`. Verify that invalid paths produce
   no standard output and do not modify any files.
2. Add sorter edge-case tests covering:
   - Mixed-case extensions, whose behavior differs between Windows and POSIX.
   - File names containing spaces or Unicode characters.
   - Sorting a directory that has already been sorted.
   - Empty directories.
3. Add end-to-end smoke tests for the installed console script.
4. If `app_gui.py` is implemented as a graphical interface, define and test
   how it interacts with the CLI contract.

## Planned improvements

### Phase 1: Architecture and reliability

- **Domain-specific exceptions:** Define exceptions in `sorter.py` (such as
  `FileSorterError`) instead of exposing low-level operating-system errors to
  the CLI.
- **Safe destination directories:** Review extension-based directory creation
  (`path / ext`) to prevent collisions with directories that already exist.

### Phase 2: Features

- **Dry-run mode (`--dry-run`):** Preview and report planned file moves without
  changing files on disk.
- **Copy mode (`--copy`):** Copy files instead of moving them, using
  `shutil.copy2` to preserve metadata.
- **Include and exclude filters (`--include` / `--exclude`):** Select or omit
  specific extensions, with validation in the CLI.
- **Recursive mode (`--recursive` / `-r`):** Scan subdirectories without
  re-sorting files that are already inside destination folders.
- **Interactive conflict resolution:** Prompt for confirmation when name
  conflicts occur in interactive terminals, while keeping the default behavior
  safe.

## Long-term direction

- Add a graphical interface using the reserved `app_gui.py` module.

## Project principles

- Avoid unnecessary external dependencies.
- Keep the code thoroughly tested.
- Maintain a clear separation between business logic and the CLI and GUI.