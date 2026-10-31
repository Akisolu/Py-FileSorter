"""Compensation shim required by the uv build backend.

The backend derives the default module from the distribution name
(``py-filesorter`` -> ``py_filesorter``) and refuses to build without it
(unlike ``sorter.py``, a standalone module is not packagable, see
astral-sh/uv#16766). All implementation lives in ``src/sorter.py``; the
editable install exposes that directory on ``sys.path``.

Prefer ``import sorter`` in tests and local code.
"""

from sorter import main, sort_files_by_extension

__all__ = ["main", "sort_files_by_extension"]
