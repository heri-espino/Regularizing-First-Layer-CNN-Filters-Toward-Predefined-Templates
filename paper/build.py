#!/usr/bin/env python3
"""Build the TMLR manuscript.

Default output:
    paper/espino_2026_template-priors.pdf

Requirements:
    - Python 3.10+
    - pdflatex and bibtex available on PATH
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

PAPER_DIR = Path(__file__).resolve().parent
ROOT = PAPER_DIR.parent
BUILD_DIR = PAPER_DIR / "build"
STYLE_DIR = PAPER_DIR / "tmlr"
SOURCE = PAPER_DIR / "main.tex"
DEFAULT_OUTPUT = PAPER_DIR / "espino_2026_template-priors.pdf"


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(
            f"Missing required executable: {name}. Install a TeX distribution "
            "that provides pdflatex and bibtex, then try again."
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
    bibtex = require_tool("bibtex")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    sep = os.pathsep
    env["TEXINPUTS"] = f".{sep}{STYLE_DIR}{sep}{env.get('TEXINPUTS', '')}"
    env["BSTINPUTS"] = f"{STYLE_DIR}{sep}{env.get('BSTINPUTS', '')}"

    latex_command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build",
        SOURCE.name,
    ]

    run(latex_command, cwd=PAPER_DIR, env=env)

    # BibTeX runs from paper/build. main.aux records the bibliography path
    # relative to paper/, so it must be shifted one level for the build dir.
    main_aux = BUILD_DIR / "main.aux"
    bibliography_aux = BUILD_DIR / "bibliography.aux"
    aux_text = main_aux.read_text(encoding="utf-8").replace(
        "../literature/references", "../../literature/references"
    )
    bibliography_aux.write_text(aux_text, encoding="utf-8")

    run([bibtex, "bibliography"], cwd=BUILD_DIR, env=env)
    shutil.copy2(BUILD_DIR / "bibliography.bbl", BUILD_DIR / "main.bbl")

    run(latex_command, cwd=PAPER_DIR, env=env)
    run(latex_command, cwd=PAPER_DIR, env=env)

    built_pdf = BUILD_DIR / "main.pdf"
    if not built_pdf.exists():
        raise SystemExit("Build finished without producing paper/build/main.pdf")

    shutil.copy2(built_pdf, output)
    try:
        shown = output.relative_to(ROOT)
    except ValueError:
        shown = output
    print(f"\nBuilt manuscript: {shown}")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the paper PDF.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output PDF path (default: paper/{DEFAULT_OUTPUT.name})",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the previous build directory and output before compiling.",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Remove generated files and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output
    if not output.is_absolute():
        output = ROOT / output

    if args.clean_only:
        clean(output)
        print("Removed generated manuscript files.")
        return 0

    try:
        build(output, clean_first=args.clean)
    except subprocess.CalledProcessError as exc:
        print(f"Build failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
