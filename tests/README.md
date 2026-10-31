# Tests

Test suite documentation for Py-FileSorter.

## Running the tests

```shell
uv run pytest
```

It runs every test with coverage enabled out of the box:
`[tool.pytest.ini_options]` in `pyproject.toml` sets
`testpaths = ["tests"]` and the addopts `--cov=src --cov-report=term-missing`.

For the quick-per-check variant the repository also ships `verificar.py`
(runner for `ruff check`, `ruff format --check`, `mypy` and `pytest -q`):

```shell
python verificar.py
```

## Current snapshot

| Metric | Value |
| --- | --- |
| Tests | 14 (`tests/test_app_cli.py`) |
| Total coverage | 92% |
| `src/app_cli.py` | 98% (only the `__main__` guard uncovered) |
| `src/sorter.py` | 91% (only the directory-skip `continue`) |
| `src/py_filesorter/__init__.py` | 0% (packaging shim, no tests import it) |

Target: >= 90% total, enforced manually (no `--cov-fail-under` yet — it can
be added once GUI code lands so failing runs do not pre-date the feature).

## Test files

### `tests/test_app_cli.py` — CLI surface (`src/app_cli.py`)

Tests `app_cli.main()` directly (returns exit codes, no subprocesses) and
its helpers `paint` / `use_color` / `mini_guide`.

Behavior under test:

| Group | Tests | What is pinned down |
| --- | --- | --- |
| Mini quick guide | `test_no_args_prints_mini_guide`, `test_mini_guide_prints_plain_text_without_tty` | Running with no arguments prints the guide, exit `0`; **no ANSI escapes** when stdout is not a TTY |
| Colors | `test_mini_guide_prints_colors_when_tty`, `test_paint_wraps_in_ansi_only_when_enabled`, `test_use_color_tty_and_no_color` | ANSI codes are emitted on TTY-like streams; `paint()` wraps only when enabled; `NO_COLOR` env var turns colors off everywhere |
| `--version` / `-v` | `test_version_flag` (parametrized for both flags) | Prints the version and exits `0` |
| Version source | `test_version_reads_distribution_metadata`, `test_version_falls_back_when_distribution_not_installed` | Reads version from installed distribution metadata; falls back to `0.1.0` when the package is not installed |
| `--dir` / `-d` | `test_dir_flag_sorts_files`, `test_short_d_flag_is_alias` | Sorts the directory by extension, prints the success message; `-d` is a full alias of `--dir` |
| Directory validation | `test_dir_missing_returns_error`, `test_dir_pointing_at_a_file_returns_error` | Non-directory targets print `error: ... is not a directory` to stderr and exit `2` |
| Defaults | `test_argv_defaults_to_sys_argv` | `main()` without arguments reads real `sys.argv[1:]` |

### `src/sorter.py` — reached through the CLI tests

The sorting logic (`sort_files_by_extension`) is exercised end-to-end via
the `--dir` tests above rather than unit-tested directly. Known behaviors
documented by the current pencil-through runs and worth dedicated tests
later (see "planned scope"):

- Name collisions with an existing destination file crash with
  `FileExistsError`.
- Extension-less files and dotfiles (`.gitignore`) stay in place silently.

## Conventions

- **Filesystem isolation**: tests only write inside pytest's `tmp_path` /
  `tmp_path_factory` sandboxes; no test touches a real user directory.
- **Determinism**: randomness is not used; palette/TTY behavior is forced
  with fake stream objects (`FakeTty`, `FakeNotTty`, `StreamRecorder`) and
  `monkeypatch`.
- **Exit codes as the contract**: CLI tests assert return values
  (`0` success, `2` usage error) and stderr content instead of parsing
  fancy output.
- **English-only output strings** match the CLI so substring assertions
  stay meaningful.
- **No network, no shared state**: the whole suite runs in well under a
  second and is safe to run in parallel (`pytest -n` works because every
  test owns its own sandbox).

## Planned scope (not yet implemented)

From the agreed test plan, remaining work:

1. **Knowledge-first bug fixes**: name collisions (today: `FileExistsError`
   crash) and silent behavior for extension-less files — failing tests
   first, then the fix.
2. **Edge cases unit suite**: dotfiles, mixed-case extensions per platform
   (`JPG` vs `jpg` differs between Windows and POSIX), spacing/Unicode file
   names, re-running the sorter on an already sorted folder, empty
   directory.
3. **CLI end-to-end**: smoke tests driving the installed console script
   (subprocess) instead of calling `main()` in-process.
4. **`app_gui.py`** (once it exists): its own test file, likely with an
   in-memory or offscreen backend so CI stays deterministic.
