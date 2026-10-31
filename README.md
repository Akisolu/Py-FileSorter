# Py-FileSorter

Py-FileSorter is a small Python command-line utility that organizes the files in a folder into subfolders named after their file extensions. For example, it moves `photo.jpg` into a `jpg` folder and `notes.txt` into a `txt` folder.

## What problem does it solve?

Folders such as Downloads can become difficult to browse when they contain many files of different types. Py-FileSorter helps reduce that clutter by grouping files by extension automatically.

## Requirements

- Python 3.15 or newer
- Either [uv](https://docs.astral.sh/uv/) or `pip`

Runtime dependencies are minimal: [colorama](https://pypi.org/project/colorama/) for colored terminal output. Everything else is Python's standard library.

## Get the project

Clone the repository and move into its directory:

```shell
git clone https://github.com/Akisolu/Py-FileSorter.git
cd Py-FileSorter
```

## Usage

### Install with uv

```shell
uv sync
```

### Run the console script

Running the executable without any flag prints a mini quick guide:

```shell
uv run py-filesorter
```

```text
py-filesorter v1.0.0 — sort files in a folder into subfolders by extension.

Quick guide:
  py-filesorter -d <directory>    sort the files of <directory>
  py-filesorter --version, -v     show the version
  py-filesorter --help, -h        show the full help

Example:
  py-filesorter -d C:\Users\you\Downloads
```

Sort a directory with `--dir` (or the short alias `-d`):

```shell
uv run py-filesorter -d C:\Users\you\Downloads
```

### All flags

| Flag | Description |
| --- | --- |
| `-d DIR`, `--dir DIR` | Sort the files of `DIR` into extension subfolders |
| `-v`, `--version` | Print the version and exit |
| `-h`, `--help` | Show the full help and exit |

### Run without installing the console script

```shell
uv run python src/app_cli.py -d <directory>
```

### Exit codes

- `0` — success (including the mini quick guide)
- `2` — usage error (for example, the path passed to `--dir` is not an existing directory)

### Colors

Output is colored on interactive terminals. Colors are disabled automatically when the output is piped or redirected, and can be turned off anywhere by setting the `NO_COLOR` environment variable.

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management and the `uv_build` build backend.

### Project layout

```text
src/
├── sorter.py             # sorting logic (plain module)
├── app_cli.py            # command-line interface
├── app_gui.py            # reserved for a future graphical interface
└── py_filesorter/
    └── __init__.py       # packaging shim required by the build backend
tests/
└── test_app_cli.py       # CLI test suite (see tests/README.md)
```

### Run the checks

The repository ships `verify.py`, a small runner that executes every check with a final summary:

```shell
python verify.py
```

It runs, in order:

1. `uv run ruff check .`
2. `uv run ruff format --check .`
3. `uv run mypy .`
4. `uv run pytest -q`

### Tests

```shell
uv run pytest
```

Tests run with coverage enabled by default (`--cov=src --cov-report=term-missing`). The current suite (14 tests) sits at about 92% coverage. Details, conventions and planned test scope live in [`tests/README.md`](tests/README.md).

### Continuous Integration

GitHub Actions run on push to `main` and on pull requests:

| Workflow | Check |
| --- | --- |
| `ruff-check.yml` | `ruff check` |
| `ruff-format.yml` | `ruff format --check` |
| `mypy.yml` | `mypy .` |
| `tests.yml` | `pytest -q` |

### Development tooling (via `uv sync --group dev`)

- `pytest` + `pytest-cov` — test runner and coverage
- `ruff` — lint and format
- `mypy` — static type checking

## Notes and known limitations

- The program **moves** files directly into subfolders; it does not copy them and there is no undo operation. Try it on a test folder first.
- Existing subfolders are skipped. The program only sorts files directly inside the folder you provide.
- Files with the same extension are placed in the same subfolder. For example, `photo.jpg` and `banner.jpg` both go into `jpg`.
- Files without an extension (and dotfiles like `.gitignore`) are left in place.
- If the destination already contains a file with the same name, the program fails and stops sorting.

## Roadmap

- Graphical interface (`app_gui.py` slot is already reserved in the source tree).
- Safer collisions on sort (suffix renames or skip-with-warning instead of failing).
