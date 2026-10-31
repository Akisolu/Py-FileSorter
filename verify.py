"""Run ruff, mypy and pytest with visual separation and a final summary.

Usage: python scripts/verificar.py  (uv must be installed)
"""

import subprocess
import sys

CHECKS = [
    ("RUFF CHECK", ["uv", "run", "ruff", "check", "."]),
    ("RUFF FORMAT", ["uv", "run", "ruff", "format", "--check", "."]),
    ("MYPY", ["uv", "run", "mypy", "."]),
    ("TESTS", ["uv", "run", "pytest", "-q"]),
]

WIDTH = 60


def banner(title: str) -> None:
    print()
    print("=" * WIDTH)
    print(f" {title}".center(WIDTH))
    print("=" * WIDTH, flush=True)


def run(title: str, cmd: list[str]) -> bool:
    banner(title)
    result = subprocess.run(cmd)  # inherits the terminal's stdout/stderr
    status = "PASSED" if result.returncode == 0 else "FAILED"
    print(f"--- {title}: {status}")
    return result.returncode == 0


def main() -> int:
    results = [(title, run(title, cmd)) for title, cmd in CHECKS]

    banner("SUMMARY")
    for title, ok in results:
        print(f"  [{'OK' if ok else 'FAIL'}] {title}")

    failed = sum(1 for _, ok in results if not ok)
    print(f"\n  {failed}/{len(results)} checks failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
