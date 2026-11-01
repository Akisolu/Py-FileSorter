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

### Install with pip

Create and activate a virtual environment, then install the project in editable mode:

```shell
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```shell
source .venv/bin/activate
```

```shell
python -m pip install -e .
```

Afterwards the `py-filesorter` console script is available inside the activated environment and every run command below works the same way.

### Run the console script

Running the executable without any flag prints a mini quick guide:

```shell
uv run py-filesorter
```

```text
py-filesorter v1.1.2 — sort files in a folder into subfolders by extension.

Quick guide:
  py-filesorter -d <directory>    sort the files of <directory>
  py-filesorter --version, -v  show the version
  py-filesorter --help, -h     show the full help
  py-filesorter -d <directory> --json  write a machine-readable result

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

### Machine-readable output

Use `--json` with `--dir` to write one JSON object to standard output instead
of the human-readable summary:

```shell
uv run py-filesorter --dir C:\Users\you\Downloads --json
```

Successful results contain a `status`, the `directory`, counts in `summary`,
and `moved` and `skipped` arrays. A skipped item has a `reason` of
`no_extension` or `destination_exists`; conflicts also include the existing
`destination`. For example:

```json
{
  "status": "completed_with_warnings",
  "directory": "C:\\Users\\you\\Downloads",
  "summary": {
    "moved": 1,
    "skipped": 1
  },
  "moved": [
    {
      "source": "C:\\Users\\you\\Downloads\\photo.jpg",
      "destination": "C:\\Users\\you\\Downloads\\jpg\\photo.jpg"
    }
  ],
  "skipped": [
    {
      "path": "C:\\Users\\you\\Downloads\\README",
      "reason": "no_extension"
    }
  ]
}
```

In JSON mode, validation and filesystem errors are also emitted as JSON on
standard output; standard error stays free of human-readable warnings. Exit
codes are `0` for a completed sort, `1` for a filesystem failure, and `2` for
an invalid or missing directory. A filesystem failure may occur after some
files have already been moved; the error result reports this possibility.

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
├── test_app_cli.py       # CLI tests
└── test_sorter.py        # Sorting behavior tests
```

### Run the checks

The repository ships `verify.py`, a small runner that executes every check with a final summary:

```shell
uv run python verify.py
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

Tests run with coverage enabled by default (`--cov=src --cov-report=term-missing`). The current suite has 29 tests; the exact coverage can vary with the installed Python version. Details, conventions and remaining planned test scope live in [`tests/README.md`](tests/README.md).

### Continuous Integration

Quality checks run on push to `main` and on pull requests:

| Workflow | Check |
| --- | --- |
| `ruff-check.yml` | `ruff check` |
| `ruff-format.yml` | `ruff format --check` |
| `mypy.yml` | `mypy .` |
| `tests.yml` | `pytest -q` |
| `build-executables.yml` | Build Windows, Linux, and macOS executables when a release is published, a tag is pushed, or manually dispatched |

### Download standalone executables

The **Build executables** workflow creates a standalone CLI executable for
Windows, Linux, and macOS when a GitHub Release is published or a tag is pushed.
When a release is published, the executables are attached to that release and
can be downloaded directly from its **Assets** section:

- `py-filesorter-windows.exe`
- `py-filesorter-linux`
- `py-filesorter-macos`

As an optional alternative, you can start a build from **Actions** using **Run
workflow** and download the resulting platform-specific artifacts from the
workflow run. Builds triggered by pushing a tag also provide artifacts there.
To attach a manual build to an existing release, enter its tag in the optional
`release_tag` field; leave it blank to keep the build available only as an
Actions artifact. Artifacts are available for 30 days. Each executable is built
on its target operating system and is for that runner's architecture.

### Development tooling (via `uv sync --group dev`)

- `pytest` + `pytest-cov` — test runner and coverage
- `ruff` — lint and format
- `mypy` — static type checking
- `types-colorama` — type stubs for `mypy`

`requirements.txt` is a pinned snapshot of the development environment for pip-only setups; the editable reference inside it uses `-e .` so it works from any checkout location.

## Notes and known limitations

- The program **moves** files directly into subfolders; it does not copy them and there is no undo operation. Try it on a test folder first.
- Existing subfolders are skipped. The program only sorts files directly inside the folder you provide.
- Files with the same extension are placed in the same subfolder. For example, `photo.jpg` and `banner.jpg` both go into `jpg`.
- Multi-extension names are filed under the last extension: `backup.tar.gz` goes into `gz`.
- Files without an extension (and dotfiles like `.gitignore`) are left in place; no special folder is created for them.
- If the destination folder already holds a file with the same name, the source file keeps its place, a warning is printed to stderr, and sorting continues with the remaining files.
- The default output is intended for people; add `--json` when another program needs to consume the result.
