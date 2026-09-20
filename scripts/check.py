#! /usr/bin/python3
"""Run the same quality checks locally as CI."""

# standard imports
import subprocess
import sys

CHECKS: tuple[tuple[str, ...], ...] = (
    ("ruff", "check", "."),
    ("ruff", "format", "--check", "."),
    ("mypy", "src", "tests"),
    (
        "pytest",
        "--cov=ryujinx_save_manager",
        "--cov-report=term-missing",
        "--cov-fail-under=80",
    ),
)


def main() -> int:
    for command in CHECKS:
        print(f"Running {' '.join(command)}", flush=True)
        try:
            result = subprocess.run(command, check=False)
        except FileNotFoundError:
            print(
                f"Missing tool: {command[0]}. Install with python -m pip install -e '.[dev]'",
                file=sys.stderr,
            )
            return 127
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
