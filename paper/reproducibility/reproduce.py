#!/usr/bin/env python3
"""Independent verification and figure regeneration for the journal archive.

Run from any extracted directory. Original study outputs are NOT required for
the five manuscript figures or the supported checks on archived tables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
FIGURES = (
    "build_overview_figure.py",
    "build_additivity_curves_figure.py",
    "build_main_results_figure.py",
    "build_anchor_specificity_figure.py",
    "build_additivity_figure.py",
)
EXPECTED_PDFS = (
    "fig00_overview.pdf",
    "fig09_additivity_curves.pdf",
    "fig06_main_results.pdf",
    "fig07_anchor_specificity.pdf",
    "fig08_additivity.pdf",
)


def _manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise ValueError("Unsupported or malformed reproducibility manifest")
    return manifest


def verify_inventory() -> dict:
    """Check the extracted inventory, checksums, and README local links."""
    entries = _manifest()["files"]
    seen = set()
    for entry in entries:
        rel = entry["exported_path"]
        candidate = ROOT / rel
        if (
            not rel
            or rel in seen
            or Path(rel).is_absolute()
            or ".." in Path(rel).parts
            or not candidate.is_file()
        ):
            raise ValueError(f"Missing, duplicated, or unsafe inventory path: {rel}")
        seen.add(rel)
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Checksum mismatch: {rel}")
        if candidate.stat().st_size != entry["size_bytes"]:
            raise ValueError(f"Size mismatch: {rel}")
    for match in re.findall(r"\[[^]]+\]\(([^)]+)\)", (ROOT / "README.md").read_text(encoding="utf-8")):
        path = match.split("#", 1)[0].strip()
        if not path or "://" in path or path.startswith("mailto:"):
            continue
        if Path(path).is_absolute() or ".." in Path(path).parts or not (ROOT / path).exists():
            raise ValueError(f"Broken README link: {match}")
    return {"manifest_files_verified": len(entries), "readme_links": "PASS"}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_numbers() -> dict:
    """Recompute selected published statistics, not the original model training.

    No bootstrap re-estimation is claimed. This checks table arithmetic against
    stored results and an independently recorded paired Student-t interval.
    """
    from math import isclose
    from statistics import mean, stdev
    from scipy.stats import t as student_t

    manifest = _manifest()
    locations = {
        e["source_path"]: ROOT / e["exported_path"] for e in manifest["files"]
    }
    def table(source: str) -> list[dict[str, str]]:
        if source not in locations:
            raise ValueError(f"Required numeric input absent: {source}")
        return _rows(locations[source])

    budget = table("analysis/budget_confirmation_001/budget_contrasts_per_block.csv")
    budget_summary = table("analysis/budget_confirmation_001/budget_contrasts.csv")
    checks = 0
    for summary in budget_summary:
        values = [
            float(r["B"]) for r in budget
            if r["architecture"] == summary["architecture"]
            and r["method"] == summary["method"]
        ]
        if len(values) != int(summary["n"]):
            raise ValueError(f"Unexpected sample size for budget {summary['architecture']}/{summary['method']}")
        actual = mean(values)
        if not isclose(actual, float(summary["mean"]), abs_tol=1e-10, rel_tol=1e-10):
            raise ValueError(f"Budget mean mismatch: {summary['architecture']}/{summary['method']}")
        checks += 1

    patching = table("analysis/patching_additivity_001/architecture_analysis/B_per_block.csv")
    filtered = [
        row for row in patching
        if row["task"] == "two_concepts"
        and row["architecture"] == "bn2_w16_gap"
        and row["anchor_family"] == "not_applicable"
        and row["set_family"] == "selected"
        and row["metric"] == "centered_logit_fidelity"
    ]
    grouped: dict[str, dict[str, float]] = {}
    for row in filtered:
        key = row["block"]
        grouped.setdefault(key, {})[row["curve"]] = float(row["B"])
    if len(grouped) != 100 or any(set(x) != {"observed", "additive"} for x in grouped.values()):
        raise ValueError("The BN2-GAP paired comparison does not contain 100 complete blocks")
    differences = [x["observed"] - x["additive"] for x in grouped.values()]
    n = len(differences)
    estimate = mean(differences)
    radius = student_t.ppf(0.975, df=n - 1) * stdev(differences) / (n ** 0.5)
    low, high = estimate - radius, estimate + radius
    expected = (-0.1799415521, -0.2008225633, -0.1590605409)
    if any(not isclose(a, b, abs_tol=2e-7) for a, b in zip((estimate, low, high), expected)):
        raise ValueError("BN2-GAP observed-minus-additive paired estimate/interval mismatch")
    checks += 1

    return {
        "status": "PASS",
        "comparisons_verified": checks,
        "bn2_gap_paired": {
            "n_blocks": n,
            "mean_observed_minus_additive": estimate,
            "student_t_ci95": [low, high],
        },
        "scope": "Archived-table arithmetic only; no raw model training or bootstrap re-estimation",
    }


def regenerate_figures() -> list[str]:
    """Create an isolated, repository-compatible workspace from the manifest."""
    manifest = _manifest()
    with tempfile.TemporaryDirectory(prefix="cnn-submission-repro-") as tmp:
        workspace = Path(tmp)
        for entry in manifest["files"]:
            original = entry["source_path"]
            # Copy only the files needed by the frozen manuscript figure scripts.
            if original.startswith("analysis/") or original in {
                "paper/plot_style.py",
                *(f"paper/{name}" for name in FIGURES),
            }:
                destination = workspace / original
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / entry["exported_path"], destination)
        paper = workspace / "paper"
        for filename in FIGURES:
            subprocess.run([sys.executable, filename], cwd=paper, check=True)
        output = ROOT / "outputs" / "figures"
        output.mkdir(parents=True, exist_ok=True)
        for name in EXPECTED_PDFS:
            src = paper / "figures" / name
            if not src.is_file() or src.stat().st_size == 0:
                raise RuntimeError(f"Figure regeneration failed: {name}")
            shutil.copy2(src, output / name)
    return [f"outputs/figures/{name}" for name in EXPECTED_PDFS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Verify checksums and README links only")
    group.add_argument("--figures", action="store_true", help="Regenerate all five manuscript figures")
    group.add_argument("--numbers", action="store_true", help="Recompute supported numerical checks")
    group.add_argument("--all", action="store_true", help="Run all checks and regenerate the figures")
    args = parser.parse_args()

    report = {"inventory": verify_inventory()}
    if args.figures or args.all:
        report["figures"] = regenerate_figures()
    if args.numbers or args.all:
        report["numbers"] = verify_numbers()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.all:
        (ROOT / "outputs" / "verification_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
