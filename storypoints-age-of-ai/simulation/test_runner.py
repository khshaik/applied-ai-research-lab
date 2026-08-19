"""Run every project test suite with one stable command.

Use ``python3 -m simulation.test_runner`` from the repository root.  Keeping
the two discovery roots explicit prevents a passing partial discovery from
being mistaken for the complete verification suite.  Pytest is the canonical
collector because the repository contains both unittest classes and
function-style pytest tests.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_ROOTS = (ROOT / "tests", ROOT / "simulation" / "tests")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="show only failures and the final count")
    args = parser.parse_args(argv)
    for start_dir in DISCOVERY_ROOTS:
        if not start_dir.is_dir():
            raise RuntimeError(f"required test root is missing: {start_dir.relative_to(ROOT)}")
    command = [sys.executable, "-m", "pytest"]
    command.append("-q" if args.quiet else "-vv")
    command.extend(str(path) for path in DISCOVERY_ROOTS)
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
