#!/usr/bin/env python3
"""Build the standalone SN Computer Science Supplementary Information PDF."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

PAPER_DIR = Path(__file__).resolve().parent
ROOT = PAPER_DIR.parent
STYLE_DIR = PAPER_DIR / "sn-article-template"
BUILD_DIR = PAPER_DIR / "supplement_build"
SOURCE = PAPER_DIR / "sn_supplement.tex"
DEFAULT_OUTPUT = PAPER_DIR / "sn_supplement.pdf"


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(
            f"Missing required executable: {name}. Install a TeX distribution and try again."
        )
    return executable


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def clean(output: Path) -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if output.exists():
        output.unlink()


def build(output: Path, *, clean_first: bool = False) -> Path:
    if clean_first:
        clean(output)

    pdflatex = require_tool("pdflatex")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    sep = os.pathsep
    env["TEXINPUTS"] = f".{sep}{STYLE_DIR}{sep}{env.get('TEXINPUTS', '')}"

    command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=supplement_build",
        SOURCE.name,
    ]
    for _ in range(3):
        run(command, cwd=PAPER_DIR, env=env)

    built = BUILD_DIR / "sn_supplement.pdf"
    if not built.exists():
        raise SystemExit(
            "Build finished without producing paper/supplement_build/sn_supplement.pdf"
        )

    shutil.copy2(built, output)
    print(f"\nBuilt supplement: {output.relative_to(ROOT)}")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the standalone supplementary PDF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--clean-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output

    if args.clean_only:
        clean(output)
        print("Removed generated supplement files.")
        return 0

    try:
        build(output, clean_first=args.clean)
    except subprocess.CalledProcessError as exc:
        print(f"Supplement build failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
