# Py-FileSorter

Py-FileSorter is a small Python command-line utility that organizes the files in a folder into subfolders named after their file extensions. For example, it moves `photo.jpg` into a `jpg` folder and `notes.txt` into a `txt` folder.

## What problem does it solve?

Folders such as Downloads can become difficult to browse when they contain many files of different types. Py-FileSorter helps reduce that clutter by grouping files by extension automatically.

## Requirements

- Python 3.15 or newer
- Either [uv](https://docs.astral.sh/uv/) or `pip`

The project currently has no runtime dependencies beyond Python's standard library.

## Get the project

Clone the repository and move into its directory:

```shell
git clone https://github.com/Akisolu/Py-FileSorter.git
cd Py-FileSorter
```

## Run locally with uv

Install the project dependencies and run the sorter:

```shell
uv sync
uv run python src/sorter.py
```

When prompted, enter the path of the folder you want to organize.

## Run locally with pip

Create and activate a virtual environment, then install the project:

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

Install the project and run the sorter:

```shell
python -m pip install requirements.txt
python src/sorter.py
```

Enter the folder path when prompted. For example, on Windows:

```text
C:\Users\YourName\Downloads
```

## Notes

- The program moves files directly into subfolders; it does not copy them or provide an undo operation. Try it on a test folder first.
- Existing subfolders are skipped. The program only sorts files directly inside the folder you provide.
- Files with the same extension are placed in the same subfolder. For example, `photo.jpg` and `banner.jpg` both go into `jpg`.
