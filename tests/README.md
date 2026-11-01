# Tests

Test suite documentation for Py-FileSorter.

## Running the tests

```shell
uv run pytest
```

Coverage is enabled out of the box via `[tool.pytest.ini_options]` in
`pyproject.toml` (`--cov=src --cov-report=term-missing`).

The repository also ships `verify.py`, a colored all-in-one runner for
`ruff check`, `ruff format --check`, `mypy` and `pytest -q`:

```shell
uv run python verify.py
```

## Snapshot

| Metric | Value |
| --- | --- |
| Tests | 29 (`test_app_cli.py`, `test_sorter.py`) |
| Total coverage | 95% (current environment) |
| `src/app_cli.py` | 96% |
| `src/sorter.py` | 100% |
| `src/py_filesorter/__init__.py` | 0% (packaging shim) |

## CLI test specification

The table defines the intended behavior contract, not a claim that every
case already has a dedicated assertion. The CLI is treated as a black box:
given an input, it produces output, filesystem side effects, and an exit
code. Remaining gaps in direct test coverage are listed under Planned scope.

### Invocation contract

| # | Expected behavior | Verify |
| --- | --- | --- |
| 1 | Running with **no arguments** prints the mini quick guide and exits `0`. The guide names every available flag and one example command. | Output text, exit code |
| 2 | `--version` (or `-v`) prints the program version and exits `0`. The version comes from the installed distribution; uninstalled, it falls back to a known default. | Output text, exit code |
| 3 | `--help` (or `-h`) shows the full usage description and exits `0`. | Output text, exit code |
| 4 | `--dir DIR` (or `-d DIR`) sorts the files of `DIR`: each file ends up inside a subfolder named after its extension; several files sharing an extension share the folder; a moved/skipped summary is printed; exit `0`. | Files relocated, output text, exit code |
| 5 | `DIR` doesn't exist, or is a file and not a directory: an error goes to **stderr** and exit code is `2`. No files are moved. | Streams separated, exit code |
| 6 | `--json` writes one JSON result to stdout; successful results contain status, directory, summary counts, moved files, and skipped files. | Parse JSON and verify schema |
| 7 | In JSON mode, invalid/missing directory errors are JSON on stdout (no human text on stderr); exit `2`. Filesystem failures return JSON and exit `1`. | Parse JSON, streams, exit code |

### Display contract

| # | Expected behavior | Verify |
| --- | --- | --- |
| 8 | On an interactive terminal, descriptions come out **colored** (ANSI codes). | Code presence on TTY |
| 9 | When output is not a terminal (piped, redirected), the same text is **plain**: no ANSI codes. | No codes without TTY |
| 10 | Setting `NO_COLOR` turns colors off even on a TTY. | No codes with env set |

### What must NOT be tested (yet)

- Implementation details: exit paths of internal helpers, order of
  statements, or private state.
- How exactly tests simulate terminals, streams, or imports — that is
  implementation of the tests themselves and may change at any time.

## `tests/test_sorter.py` — sorting contract (`src/sorter.py`)

The function sorts by side effect; the contract below mirrors the
docstring of `sort_files_by_extension` and only observes filesystem
outcomes (and one stderr rule), never internals.

| # | Expected behavior | Verify |
| --- | --- | --- |
| 1 | `photo.jpg` + `notes.txt` end up as `jpg/photo.jpg` and `txt/notes.txt`. | Files relocated |
| 2 | `uno.jpg` + `dos.jpg` both end up inside the same `jpg/`. | Folder contents |
| 3 | `backup.tar.gz` is filed under the **last** extension → `gz/`. | File relocated |
| 4 | A pre-existing subfolder is left untouched: not sorted, not wrapped, its contents intact. | Folder and inner file unchanged |
| 5 | Extension-less files (`README`) and dotfiles (`.gitignore`) **stay in place** — declared policy; no special folder is created. | Files unchanged |
| 6 | Destination collision: source file is kept (never overwritten), the destination file is untouched, the conflict is recorded in the result, and the rest of the batch still gets sorted. | Both files intact, returned result |
| 7 | Missing route → `FileNotFoundError`; route to a file → `NotADirectoryError`. The CLI (`app_cli`) maps these routes to a human message before they reach this layer, so the contract here is standard exceptions. | Exception type, nothing moved |

## `src/app_cli.py` mapping note

The CLI already validates `--dir` (missing path / non-directory → exit code
`2`), so sorter-level errors only surface when other code calls
`sort_files_by_extension` directly.
