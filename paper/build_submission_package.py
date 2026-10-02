#!/usr/bin/env python3
"""Create an allowlisted SN submission/reproducibility ZIP.

The archive is deliberately limited to the main/supplement PDFs plus the code,
protocols, and compact block-level/aggregate tables needed to verify the paper.
Raw checkpoints and per-model JSON outputs are excluded.
"""

from __future__ import annotations

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = PAPER / "dist"
OUT = DIST / "sn_submission_package.zip"

REQUIRED_PDFS = (
    PAPER / "sn_submission.pdf",
    PAPER / "sn_supplement.pdf",
)

FILES = [
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


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED_PDFS if not p.is_file()]
    missing += [p for p in FILES if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit(
            "Missing required submission-package files:\n- " + "\n- ".join(missing)
        )

    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()

    with zipfile.ZipFile(
        OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for pdf in REQUIRED_PDFS:
            archive.write(pdf, arcname=pdf.name)
        for rel in FILES:
            archive.write(ROOT / rel, arcname=f"reproducibility/{rel}")

    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Built {OUT.relative_to(ROOT)} ({size_mb:.1f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
