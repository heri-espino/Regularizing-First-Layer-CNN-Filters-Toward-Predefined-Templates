#!/usr/bin/env python3
"""Build the standalone supplementary manuscript after the main paper.

The supplement reuses build/main.aux through xr-hyper so references to main-text
equations and figures remain resolvable. It preserves the exhaustive result
tables without placing them in the main manuscript.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

PAPER_DIR = Path(__file__).resolve().parent
ROOT = PAPER_DIR.parent
BUILD_DIR = PAPER_DIR / "build"
STYLE_DIR = PAPER_DIR / "tmlr"
SOURCE = PAPER_DIR / "supplement.tex"
OUTPUT = PAPER_DIR / "supplement.pdf"


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(f"Missing required executable: {name}")
    return executable


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def build() -> Path:
    main_aux = BUILD_DIR / "main.aux"
    if not main_aux.exists():
        raise SystemExit(
            "paper/build/main.aux is missing. Build the main manuscript first "
            "with python paper/build.py."
        )

    pdflatex = require_tool("pdflatex")
    bibtex = require_tool("bibtex")

    env = os.environ.copy()
    sep = os.pathsep
    env["TEXINPUTS"] = f".{sep}{STYLE_DIR}{sep}{env.get('TEXINPUTS', '')}"
    env["BSTINPUTS"] = f"{STYLE_DIR}{sep}{env.get('BSTINPUTS', '')}"

    command = [
        pdflatex,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build",
        SOURCE.name,
    ]

    run(command, cwd=PAPER_DIR, env=env)

    aux = BUILD_DIR / "supplement.aux"
    bib_aux = BUILD_DIR / "supplement_bibliography.aux"
    aux_text = aux.read_text(encoding="utf-8").replace(
        "../literature/references", "../../literature/references"
    )
    bib_aux.write_text(aux_text, encoding="utf-8")

    run([bibtex, "supplement_bibliography"], cwd=BUILD_DIR, env=env)
    shutil.copy2(
        BUILD_DIR / "supplement_bibliography.bbl",
        BUILD_DIR / "supplement.bbl",
    )

    run(command, cwd=PAPER_DIR, env=env)
    run(command, cwd=PAPER_DIR, env=env)

    built = BUILD_DIR / "supplement.pdf"
    if not built.exists():
        raise SystemExit("Supplement build finished without a PDF")
    shutil.copy2(built, OUTPUT)
    print(f"Built supplement: {OUTPUT.relative_to(ROOT)}")
    return OUTPUT


def main() -> int:
    try:
        build()
    except subprocess.CalledProcessError as exc:
        print(f"Supplement build failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
