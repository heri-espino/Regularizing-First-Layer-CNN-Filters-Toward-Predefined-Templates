#!/usr/bin/env python3
"""Build separate reader-facing SN submission artifacts, with verified provenance.

Raw experiment outputs remain excluded. Repacking never mutates study results
or historical analysis scripts; the export renames paths with a manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = PAPER / "dist"

PDFS = {
    "manuscript.pdf": "paper/sn_submission.pdf",
    "supplementary_information.pdf": "paper/sn_supplement.pdf",
}
SOURCE_ARCHIVE = "manuscript_sources.zip"
REPRO_ARCHIVE = "activation_patching_reproducibility.zip"
FIGURE_SCRIPTS = (
    "build_overview_figure.py",
    "build_additivity_curves_figure.py",
    "build_main_results_figure.py",
    "build_anchor_specificity_figure.py",
    "build_additivity_figure.py",
)
FIGURE_PDFS = (
    "fig00_overview.pdf",
    "fig09_additivity_curves.pdf",
    "fig06_main_results.pdf",
    "fig07_anchor_specificity.pdf",
    "fig08_additivity.pdf",
)
# These inputs allow manuscript_sources.zip to build from scratch, even
# though the build.py script always regenerates manuscript figures.
FIGURE_DATA = (
    "analysis/patching_additivity_001/architecture_analysis/curve_summary.csv",
    "analysis/metric_sensitivity_001/stage_d_treatment_contrasts.csv",
    "analysis/architecture_robustness_001/architecture_B_summary.csv",
    "analysis/anchor_specificity_001/secondary_anchor_contrasts.csv",
    "analysis/anchor_specificity_001/primary_spatial_specificity.csv",
    "analysis/anchor_specificity_001/random_channel_spatial_specificity.csv",
    "analysis/patching_additivity_001/architecture_analysis/B_summary.csv",
    "analysis/patching_additivity_001/anchor_analysis/structured_vs_pixel_permuted_B_averaged_architectures.csv",
)

# This list is the former checked-in allowlist, preserved as the export
# selection boundary. Source paths remain immutable. New labels are
# presentation-only and recorded in manifest.json.

ALLOWLIST = [
    "paper/main.tex",
    "paper/sn_supplement.tex",
    "paper/README.md",
    "paper/SUBMISSION_CHECKLIST.md",
    "paper/SUPPLEMENT_REPRODUCIBILITY.md",
    "paper/build.py",
    "paper/build_submission_package.py",
    "paper/build_supplement.py",
    "paper/build_overview_figure.py",
    "paper/build_main_results_figure.py",
    "paper/build_anchor_specificity_figure.py",
    "paper/build_additivity_curves_figure.py",
    "paper/build_additivity_figure.py",
    "paper/plot_style.py",
    "paper/sn-article-template/sn-jnl.cls",
    "paper/sn-article-template/bst/sn-basic.bst",
    "literature/references.bib",
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CITATION.cff",
    ".zenodo.json",

    "studies/cnn_release_experiment/core.py",
    "studies/cnn_budget_confirmation/PROTOCOL.md",
    "studies/cnn_budget_confirmation/analyze.py",
    "studies/cnn_exhaustive_robustness/PROTOCOL.md",
    "studies/cnn_exhaustive_robustness/analyze_grid.py",
    "studies/cnn_exhaustive_robustness/evaluate_grid.py",
    "studies/cnn_exhaustive_robustness/train_grid.py",
    "studies/cnn_metric_sensitivity/PROTOCOL.md",
    "studies/cnn_metric_sensitivity/analyze_metrics.py",
    "studies/cnn_metric_sensitivity/evaluate_metrics.py",
    "studies/cnn_architecture_robustness/PROTOCOL.md",
    "studies/cnn_architecture_robustness/architecture_core.py",
    "studies/cnn_architecture_robustness/train_grid.py",
    "studies/cnn_architecture_robustness/evaluate_grid.py",
    "studies/cnn_architecture_robustness/analyze.py",
    "studies/cnn_architecture_posthoc/PROTOCOL.md",
    "studies/cnn_architecture_posthoc/analyze.py",
    "studies/cnn_anchor_specificity/PROTOCOL.md",
    "studies/cnn_anchor_specificity/anchor_core.py",
    "studies/cnn_anchor_specificity/train_grid.py",
    "studies/cnn_anchor_specificity/evaluate_grid.py",
    "studies/cnn_anchor_specificity/analyze.py",
    "studies/cnn_patching_additivity/PROTOCOL.md",
    "studies/cnn_patching_additivity/IMPLEMENTATION_MANIFEST.json",
    "studies/cnn_patching_additivity/math_core.py",
    "studies/cnn_patching_additivity/evaluate.py",
    "studies/cnn_patching_additivity/analyze.py",
    "studies/cnn_patching_additivity/validate.py",
    "studies/cnn_patching_additivity/test_math.py",
    "studies/cnn_checkpoint_audit/AUDIT_PROTOCOL.md",

    "analysis/retention_release_001/endpoints.csv",
    "analysis/exhaustive_robustness_001/REPORT.md",
    "analysis/exhaustive_robustness_001/model_endpoint_summary.csv",
    "analysis/exhaustive_robustness_001/model_endpoints.csv",
    "analysis/exhaustive_robustness_001/execution_manifest.json",
    "analysis/checkpoint_audit/AUDIT_REPORT.md",

    "analysis/budget_confirmation_001/REPORT.md",
    "analysis/budget_confirmation_001/primary_curve.csv",
    "analysis/budget_confirmation_001/treatment_contrasts.csv",
    "analysis/budget_confirmation_001/budget_contrasts.csv",
    "analysis/budget_confirmation_001/budget_contrasts_per_block.csv",
    "analysis/budget_confirmation_001/integrity_checks.csv",
    "analysis/budget_confirmation_001/execution_manifest.json",

    "analysis/metric_sensitivity_001/REPORT.md",
    "analysis/metric_sensitivity_001/stage_d_design.json",
    "analysis/metric_sensitivity_001/stage_d_treatment_contrasts.csv",
    "analysis/metric_sensitivity_001/stage_d_treatment_contrasts_per_block.csv",
    "analysis/metric_sensitivity_001/stage_d_budget_contrasts_B.csv",
    "analysis/metric_sensitivity_001/stage_d_budget_contrasts_B_per_block.csv",
    "analysis/metric_sensitivity_001/stage_d_input_effect_scale_contrasts.csv",
    "analysis/metric_sensitivity_001/stage_d_input_effect_scale_contrasts_per_block.csv",
    "analysis/metric_sensitivity_001/stage_d_model_integrity.csv",
    "analysis/metric_sensitivity_001/execution_manifest.json",

    "analysis/architecture_robustness_001/REPORT.md",
    "analysis/architecture_robustness_001/training_design.json",
    "analysis/architecture_robustness_001/evaluation_design.json",
    "analysis/architecture_robustness_001/training_environment.json",
    "analysis/architecture_robustness_001/architecture_B_summary.csv",
    "analysis/architecture_robustness_001/treatment_delta_curves.csv",
    "analysis/architecture_robustness_001/primary_architecture_omnibus.csv",
    "analysis/architecture_robustness_001/primary_bridge_contrast.csv",
    "analysis/architecture_robustness_001/primary_bridge_contrast_per_block.csv",
    "analysis/architecture_robustness_001/architecture_factor_contrasts.csv",
    "analysis/architecture_robustness_001/input_effect_scale_contrasts.csv",
    "analysis/architecture_robustness_001/execution_manifest.json",

    "analysis/architecture_posthoc_diagnostics_001/REPORT.md",
    "analysis/architecture_posthoc_diagnostics_001/architecture_definitions.csv",
    "analysis/architecture_posthoc_diagnostics_001/omnibus_robustness.csv",
    "analysis/architecture_posthoc_diagnostics_001/random_B_per_block.csv",
    "analysis/architecture_posthoc_diagnostics_001/selected_B_per_block.csv",
    "analysis/architecture_posthoc_diagnostics_001/selected_random_architecture_correlations.csv",
    "analysis/architecture_posthoc_diagnostics_001/selected_random_summary.csv",
    "analysis/architecture_posthoc_diagnostics_001/random_bridge_contrast.csv",
    "analysis/architecture_posthoc_diagnostics_001/alignment_B_architecture_summary.csv",
    "analysis/architecture_posthoc_diagnostics_001/alignment_B_correlations.csv",
    "analysis/architecture_posthoc_diagnostics_001/alignment_B_per_block.csv",
    "analysis/architecture_posthoc_diagnostics_001/alignment_B_architecture_mean_correlations.csv",
    "analysis/architecture_posthoc_diagnostics_001/execution_manifest.json",
    "analysis/architecture_posthoc_diagnostics_001/launch_manifest.json",

    "analysis/anchor_specificity_001/REPORT.md",
    "analysis/anchor_specificity_001/training_design.json",
    "analysis/anchor_specificity_001/evaluation_design.json",
    "analysis/anchor_specificity_001/primary_spatial_specificity.csv",
    "analysis/anchor_specificity_001/primary_spatial_specificity_per_block.csv",
    "analysis/anchor_specificity_001/random_channel_spatial_specificity.csv",
    "analysis/anchor_specificity_001/random_channel_spatial_specificity_per_block.csv",
    "analysis/anchor_specificity_001/secondary_anchor_contrasts.csv",
    "analysis/anchor_specificity_001/secondary_anchor_contrasts_per_block.csv",
    "analysis/anchor_specificity_001/anchor_architecture_B_summary.csv",
    "analysis/anchor_specificity_001/primary_spatial_architecture_interaction.csv",
    "analysis/anchor_specificity_001/random_channel_spatial_architecture_interaction.csv",
    "analysis/anchor_specificity_001/anchor_integrity.csv",
    "analysis/anchor_specificity_001/execution_manifest.json",

    "analysis/patching_additivity_001/architecture_analysis/REPORT.md",
    "analysis/patching_additivity_001/architecture_analysis/B_summary.csv",
    "analysis/patching_additivity_001/architecture_analysis/B_per_block.csv",
    "analysis/patching_additivity_001/architecture_analysis/curve_summary.csv",
    "analysis/patching_additivity_001/architecture_analysis/reconstruction_gap_summary.csv",
    "analysis/patching_additivity_001/architecture_analysis/model_integrity.csv",
    "analysis/patching_additivity_001/architecture_analysis/summary.json",

    "analysis/patching_additivity_001/anchor_analysis/REPORT.md",
    "analysis/patching_additivity_001/anchor_analysis/B_summary.csv",
    "analysis/patching_additivity_001/anchor_analysis/B_per_block.csv",
    "analysis/patching_additivity_001/anchor_analysis/curve_summary.csv",
    "analysis/patching_additivity_001/anchor_analysis/reconstruction_gap_summary.csv",
    "analysis/patching_additivity_001/anchor_analysis/model_integrity.csv",
    "analysis/patching_additivity_001/anchor_analysis/structured_vs_pixel_permuted_B_by_architecture.csv",
    "analysis/patching_additivity_001/anchor_analysis/structured_vs_pixel_permuted_B_averaged_architectures.csv",
    "analysis/patching_additivity_001/anchor_analysis/summary.json",
]

EXTRA_FILES = (
    "paper/reproducibility/README.md",
    "paper/reproducibility/MANUSCRIPT_SOURCES_README.md",
    "paper/reproducibility/requirements.txt",
    "paper/reproducibility/reproduce.py",
)
DATA_PREFIXES = {
    "analysis/patching_additivity_001/architecture_analysis/": "data/additivity/architecture_comparison/",
    "analysis/patching_additivity_001/anchor_analysis/": "data/additivity/spatial_controls/",
    "analysis/retention_release_001/": "data/retention_release/",
    "analysis/exhaustive_robustness_001/": "data/robustness/",
    "analysis/checkpoint_audit/": "data/checkpoint_audit/",
    "analysis/budget_confirmation_001/": "data/intervention_budget/",
    "analysis/metric_sensitivity_001/": "data/metric_sensitivity/",
    "analysis/architecture_robustness_001/": "data/architecture/",
    "analysis/architecture_posthoc_diagnostics_001/": "data/architecture_posthoc/",
    "analysis/anchor_specificity_001/": "data/spatial_specificity/",
}
PROTOCOL_NAMES = {
    "cnn_budget_confirmation": "intervention_budget.md",
    "cnn_exhaustive_robustness": "robustness_grid.md",
    "cnn_metric_sensitivity": "metric_sensitivity.md",
    "cnn_architecture_robustness": "architecture_comparison.md",
    "cnn_architecture_posthoc": "architecture_posthoc.md",
    "cnn_anchor_specificity": "spatial_specificity.md",
    "cnn_patching_additivity": "additivity.md",
    "cnn_checkpoint_audit": "checkpoint_audit.md",
}
STUDY_NAMES = {
    "cnn_release_experiment": "renderer_and_models",
    "cnn_budget_confirmation": "intervention_budget",
    "cnn_exhaustive_robustness": "robustness_grid",
    "cnn_metric_sensitivity": "metric_sensitivity",
    "cnn_architecture_robustness": "architecture_comparison",
    "cnn_architecture_posthoc": "architecture_posthoc",
    "cnn_anchor_specificity": "spatial_specificity",
    "cnn_patching_additivity": "additivity",
    "cnn_checkpoint_audit": "checkpoint_audit",
}


def source_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True, timeout=5
        )
        value = result.stdout.strip()
        if len(value) == 40 and all(c in "0123456789abcdef" for c in value.lower()):
            return value
    except (FileNotFoundError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    value = os.environ.get("GITHUB_SHA", "")
    return value if len(value) == 40 else None


def source_mapping() -> dict[str, str]:
    files = {
        "paper/reproducibility/MANUSCRIPT_SOURCES_README.md": "README.md",
        "paper/main.tex": "paper/main.tex",
        "paper/sn_supplement.tex": "paper/sn_supplement.tex",
        "paper/build.py": "paper/build.py",
        "paper/build_supplement.py": "paper/build_supplement.py",
        "paper/plot_style.py": "paper/plot_style.py",
        "paper/sn-article-template/sn-jnl.cls": "paper/sn-article-template/sn-jnl.cls",
        "paper/sn-article-template/bst/sn-basic.bst": "paper/sn-article-template/bst/sn-basic.bst",
        "literature/references.bib": "literature/references.bib",
        "pyproject.toml": "pyproject.toml",
        "LICENSE": "LICENSE",
    }
    for name in FIGURE_SCRIPTS:
        files[f"paper/{name}"] = f"paper/{name}"
    for name in FIGURE_PDFS:
        files[f"paper/figures/{name}"] = f"paper/figures/{name}"
    for original in FIGURE_DATA:
        files[original] = original
    return files


def repro_mapping() -> dict[str, str]:
    files = {
        "paper/reproducibility/README.md": "README.md",
        "paper/reproducibility/requirements.txt": "requirements.txt",
        "paper/reproducibility/reproduce.py": "reproduce.py",
        "LICENSE": "LICENSE",
    }
    for original in ALLOWLIST:
        if original.startswith("analysis/"):
            for prefix, friendly in DATA_PREFIXES.items():
                if original.startswith(prefix):
                    files[original] = friendly + original[len(prefix):]
                    break
            else:
                raise ValueError(f"Unknown analysis export prefix: {original}")
        elif original.startswith("studies/"):
            parts = Path(original).parts
            study = parts[1]
            if len(parts) != 3:
                raise ValueError(f"Unexpected study depth: {original}")
            if parts[-1] in ("PROTOCOL.md", "AUDIT_PROTOCOL.md"):
                files[original] = f"protocols/{PROTOCOL_NAMES[study]}"
            else:
                files[original] = f"code/experiments/{STUDY_NAMES[study]}/{parts[-1]}"
        elif original in {"paper/plot_style.py", *(f"paper/{name}" for name in FIGURE_SCRIPTS)}:
            files[original] = f"code/figures/{Path(original).name}"
    return files


def validate_mapping(mapping: dict[str, str]) -> None:
    original_paths = set(mapping)
    if len(original_paths) != len(mapping):
        raise ValueError("Duplicate source paths")
    target_paths = list(mapping.values())
    if len(target_paths) != len(set(target_paths)):
        raise ValueError("Duplicate archive paths")
    for archive_path in target_paths:
        pure = PurePosixPath(archive_path)
        if not archive_path or pure.is_absolute() or ".." in pure.parts or "\\" in archive_path:
            raise ValueError(f"Unsafe archive path: {archive_path}")
    missing = [src for src in mapping if not (ROOT / src).is_file()]
    if missing:
        raise FileNotFoundError("Required submission files not found:\n- " + "\n- ".join(missing))


def _add(archive: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def make_archive(path: Path, mapping: dict[str, str], *, manifest: bool) -> None:
    validate_mapping(mapping)
    inventory = []
    with zipfile.ZipFile(path, "w") as archive:
        for source, exported in sorted(mapping.items(), key=lambda p: p[1]):
            data = (ROOT / source).read_bytes()
            _add(archive, exported, data)
            inventory.append({
                "source_path": source,
                "exported_path": exported,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        if manifest:
            metadata = {
                "schema_version": 1,
                "paper": "When Do Activation-Patching Effects Add Up? Evidence from Controlled CNNs",
                "source_repository": "heri-espino/Regularizing-First-Layer-CNN-Filters-Toward-Predefined-Templates",
                "source_commit": source_commit(),
                "description": "Renaming-only export of allowlisted original research artifacts",
                "excluded": [
                    "raw training checkpoints",
                    "per-model evaluator JSON outputs",
                    "raw model training and evaluation run directories",
                    "Git history and machine-specific temporary files",
                ],
                "files": inventory,
            }
            _add(archive, "manifest.json", (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode())


def _extract_and_check(archive_path: Path, target: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"ZIP CRC failure in {archive_path.name}")
        for name in archive.namelist():
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts:
                raise RuntimeError(f"Unsafe archive member: {name}")
        archive.extractall(target)


def verify_outputs(*, run_full: bool) -> None:
    """Verify independent extraction, manifest checks, and optional execution."""
    with tempfile.TemporaryDirectory(prefix="cnn-package-verify-") as temporary:
        root = Path(temporary)
        sources = root / "sources"
        repro = root / "repro"
        sources.mkdir()
        repro.mkdir()
        _extract_and_check(DIST / SOURCE_ARCHIVE, sources)
        _extract_and_check(DIST / REPRO_ARCHIVE, repro)
        for src in source_mapping().values():
            if not (sources / src).is_file():
                raise RuntimeError(f"Manuscript source missing after extraction: {src}")
        command = [sys.executable, str(repro / "reproduce.py"), "--all" if run_full else "--check"]
        subprocess.run(command, cwd=repro, check=True)
        if run_full:
            for figure in FIGURE_PDFS:
                output = repro / "outputs" / "figures" / figure
                if not output.is_file() or output.stat().st_size == 0:
                    raise RuntimeError(f"Missing independently reproduced figure: {figure}")
        print("Independent ZIP extraction / integrity checks: PASS")


def build(verify: bool) -> None:
    source_files = source_mapping()
    reproducibility_files = repro_mapping()
    validate_mapping(source_files)
    validate_mapping(reproducibility_files)
    missing_pdfs = [src for src in PDFS.values() if not (ROOT / src).is_file()]
    if missing_pdfs:
        raise FileNotFoundError("Missing compiled PDFs: " + ", ".join(missing_pdfs))
    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cnn-export-", dir=DIST) as temporary:
        tmp = Path(temporary)
        make_archive(tmp / SOURCE_ARCHIVE, source_files, manifest=False)
        make_archive(tmp / REPRO_ARCHIVE, reproducibility_files, manifest=True)
        for exported, source in PDFS.items():
            shutil.copy2(ROOT / source, tmp / exported)
        for exported in [*PDFS, SOURCE_ARCHIVE, REPRO_ARCHIVE]:
            (tmp / exported).replace(DIST / exported)
    verify_outputs(run_full=verify)
    # The former mixed manuscript/code ZIP is obsolete. Avoid leaving a stale
    # upload candidate next to the four newly verified deliverables.
    legacy = DIST / "sn_submission_package.zip"
    if legacy.is_file():
        legacy.unlink()
        print(f"Removed obsolete {legacy.relative_to(ROOT)}")
    for name in [*PDFS, SOURCE_ARCHIVE, REPRO_ARCHIVE]:
        output = DIST / name
        print(f"Built {output.relative_to(ROOT)} ({output.stat().st_size / (1024 * 1024):.2f} MiB)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify", action="store_true",
        help="Also extract the result into an empty directory, regenerate all five figures, "
             "and recompute supported numerical checks (requires figure dependencies)."
    )
    args = parser.parse_args()
    build(verify=args.verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
