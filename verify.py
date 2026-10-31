"""Run ruff, mypy and pytest with visual separation and a final summary.

Usage: uv run python verify.py  (colorama + uv come from the repo deps)
"""

import os
import subprocess
import sys

from colorama import Fore, Style, init

CHECKS = [
    ("RUFF CHECK", ["uv", "run", "ruff", "check", "."]),
    ("RUFF FORMAT", ["uv", "run", "ruff", "format", "--check", "."]),
    ("MYPY", ["uv", "run", "mypy", "."]),
    ("TESTS", ["uv", "run", "pytest", "-q"]),
]

WIDTH = 60

GREEN, RED, YELLOW, CYAN = Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.CYAN
DIM, BOLD, RESET = Style.DIM, Style.BRIGHT, Style.RESET_ALL


def use_colors() -> bool:
    """Color output only stays on for interactive terminals that want it."""
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


if not use_colors():  # No codes get embedded in pipes, files or CI logs.
    GREEN = RED = YELLOW = CYAN = DIM = BOLD = RESET = ""


def banner(title: str) -> None:
    print()
    print(f"{CYAN}{'=' * WIDTH}{RESET}")
    print(f"{f' {title} '.center(WIDTH, '.')}", flush=True)
    print(f"{CYAN}{'=' * WIDTH}{RESET}", flush=True)


def run(title: str, cmd: list[str]) -> bool:
    banner(title)
    result = subprocess.run(cmd)  # inherits the terminal's stdout/stderr
    status = (
        f"{GREEN}PASSED{RESET}"
        if result.returncode == 0
        else f"{BOLD}{RED}FAILED{RESET}"
    )
    print(f"{DIM}--- {title}:{RESET} {status}", flush=True)
    return result.returncode == 0


def main() -> int:
    init()
    results = [(title, run(title, cmd)) for title, cmd in CHECKS]

    banner("SUMMARY")
    for title, ok in results:
        mark = f"{GREEN}[OK]{RESET}" if ok else f"{BOLD}{RED}[FAIL]{RESET}"
        print(f"  {mark} {title}")

    failed = sum(1 for _, ok in results if not ok)
    failed_line = f"{failed}/{len(results)} checks failed"
    print(
        f"\n  {GREEN}{failed_line}{RESET}"
        if not failed
        else f"\n  {BOLD}{YELLOW}{failed_line}{RESET}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
