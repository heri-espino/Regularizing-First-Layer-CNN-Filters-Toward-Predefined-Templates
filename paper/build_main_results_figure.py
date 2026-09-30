#!/usr/bin/env python3
"""Build the two central result figures for the restructured manuscript.

Figure 2 shows retention and release curves separately, then their paired
difference, for the pre-specified intervention-size experiment.

Figure 4 shows the complete 16-architecture map of the intervention-size
contrast B under the two primary metrics.

This script is presentation-only: it reads versioned aggregate/model-level
analysis tables and does not retrain models or redefine any scientific test.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from plot_style import apply_paper_style, save_pdf

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent

OUT_INTERVENTION = PAPER / "figures" / "fig02_intervention_size.pdf"
OUT_ARCHITECTURE = PAPER / "figures" / "fig04_architecture.pdf"

CONTRAST_TABLE = (
    ROOT / "analysis" / "metric_sensitivity_001" / "stage_d_treatment_contrasts.csv"
)
MODEL_TABLE = (
    ROOT / "analysis" / "metric_sensitivity_001" / "stage_d_model_metric_rows.csv"
)
ARCH_TABLE = (
    ROOT / "analysis" / "architecture_robustness_001" / "architecture_B_summary.csv"
)

METRICS = (
    ("prob_fidelity", r"$F_{\mathrm{prob}}$"),
    ("centered_logit_fidelity", r"$F_{\mathrm{clogit}}$"),
    ("prob_error_reduction", r"$R_{\mathrm{prob}}$"),
)

ARCH_METRICS = (
    ("centered_logit_fidelity", r"$B_{\mathrm{clogit}}$"),
    ("prob_error_reduction", r"$B_{R_{\mathrm{prob}}}$"),
)

CONDITIONS = (
    ("template_retention_1", "Retention", "o", "-"),
    ("template_release", "Release", "s", "--"),
)

ARCH_ORDER = (
    "tiny_gmp",
    "tiny_gap",
    "plain2_w16_gmp",
    "plain2_w16_gap",
    "plain4_w16_gmp",
    "plain4_w16_gap",
    "plain2_w64_gmp",
    "plain2_w64_gap",
    "plain4_w64_gmp",
    "plain4_w64_gap",
    "res4_w16_gmp",
    "res4_w16_gap",
    "bn2_w16_gmp",
    "bn2_w16_gap",
    "bn4_w16_gmp",
    "bn4_w16_gap",
)

ARCH_LABELS = {
    "tiny_gmp": "Tiny · GMP",
    "tiny_gap": "Tiny · GAP",
    "plain2_w16_gmp": "Plain-2 w16 · GMP",
    "plain2_w16_gap": "Plain-2 w16 · GAP",
    "plain4_w16_gmp": "Plain-4 w16 · GMP",
    "plain4_w16_gap": "Plain-4 w16 · GAP",
    "plain2_w64_gmp": "Plain-2 w64 · GMP",
    "plain2_w64_gap": "Plain-2 w64 · GAP",
    "plain4_w64_gmp": "Plain-4 w64 · GMP",
    "plain4_w64_gap": "Plain-4 w64 · GAP",
    "res4_w16_gmp": "Residual-4 w16 · GMP",
    "res4_w16_gap": "Residual-4 w16 · GAP",
    "bn2_w16_gmp": "BN-2 w16 · GMP",
    "bn2_w16_gap": "BN-2 w16 · GAP",
    "bn4_w16_gmp": "BN-4 w16 · GMP",
    "bn4_w16_gap": "BN-4 w16 · GAP",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def contrast_rows(rows: list[dict[str, str]], metric: str) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if row["architecture"] == "TinyCNN"
        and row["method"] == "contrast"
        and row["metric"] == metric
        and int(row["k"]) in (1, 2, 4, 8)
    ]
    selected.sort(key=lambda row: int(row["k"]))
    if [int(row["k"]) for row in selected] != [1, 2, 4, 8]:
        raise ValueError(f"Unexpected contrast rows for {metric}")
    return selected


def treatment_curve(
    rows: list[dict[str, str]],
    metric: str,
    condition: str,
) -> tuple[np.ndarray, np.ndarray]:
    selected = [
        row
        for row in rows
        if row["stage"] == "D"
        and row["task"] == "two_concepts"
        and row["architecture"] == "TinyCNN"
        and row["condition"] == condition
        and row["method"] == "contrast"
        and int(row["k"]) in (1, 2, 4, 8)
    ]
    by_k: dict[int, list[float]] = {k: [] for k in (1, 2, 4, 8)}
    for row in selected:
        by_k[int(row["k"])].append(float(row[metric]))

    if any(len(by_k[k]) != 20 for k in by_k):
        counts = {k: len(v) for k, v in by_k.items()}
        raise ValueError(f"Unexpected Stage-D counts for {condition}/{metric}: {counts}")

    x = np.array([1, 2, 4, 8], dtype=float)
    y = np.array([np.mean(by_k[k]) for k in (1, 2, 4, 8)], dtype=float)
    return x, y


def architecture_rows(
    rows: list[dict[str, str]], metric: str
) -> dict[str, dict[str, str]]:
    selected = {
        row["architecture"]: row
        for row in rows
        if row["task"] == "two_concepts" and row["metric"] == metric
    }
    missing = [arch for arch in ARCH_ORDER if arch not in selected]
    if missing:
        raise ValueError(f"Missing architecture rows for {metric}: {missing}")
    return selected


def draw_treatment_panel(
    ax: plt.Axes,
    model_rows: list[dict[str, str]],
    metric: str,
    title: str,
) -> None:
    for condition, label, marker, linestyle in CONDITIONS:
        x, y = treatment_curve(model_rows, metric, condition)
        ax.plot(
            x,
            y,
            marker=marker,
            linestyle=linestyle,
            linewidth=1.35,
            markersize=3.7,
            label=label,
        )
    ax.set_title(title, pad=3)
    ax.set_xticks([1, 2, 4, 8])
    ax.grid(axis="x", visible=False)


def draw_difference_panel(
    ax: plt.Axes,
    rows: list[dict[str, str]],
) -> None:
    x = np.array([int(row["k"]) for row in rows], dtype=float)
    mean = np.array([float(row["mean"]) for row in rows])
    low = np.array([float(row["ci_low"]) for row in rows])
    high = np.array([float(row["ci_high"]) for row in rows])
    yerr = np.vstack([mean - low, high - mean])

    ax.axhline(0, linewidth=0.7, zorder=0)
    ax.errorbar(
        x,
        mean,
        yerr=yerr,
        marker="o",
        markersize=3.6,
        linewidth=1.35,
        capsize=2.0,
        capthick=0.7,
        zorder=3,
    )
    ax.set_xticks([1, 2, 4, 8])
    ax.grid(axis="x", visible=False)


def build_intervention_figure(
    contrast_table: list[dict[str, str]],
    model_table: list[dict[str, str]],
) -> Path:
    fig, axes = plt.subplots(
        2,
        3,
        figsize=(7.15, 4.45),
        sharex="col",
        constrained_layout=False,
    )
    fig.subplots_adjust(left=0.10, right=0.99, top=0.92, bottom=0.12, wspace=0.30, hspace=0.30)

    for col, (metric, label) in enumerate(METRICS):
        draw_treatment_panel(axes[0, col], model_table, metric, label)
        draw_difference_panel(axes[1, col], contrast_rows(contrast_table, metric))

    axes[0, 0].set_ylabel("Patching metric")
    axes[1, 0].set_ylabel(r"Release $-$ retention, $\Delta^M(k)$")
    for ax in axes[1, :]:
        ax.set_xlabel(r"Patched channels, $k$")

    axes[0, 0].legend(
        loc="best",
        frameon=False,
        fontsize=7.0,
        handlelength=2.3,
    )

    fig.text(0.01, 0.965, "a", fontweight="bold", fontsize=9.0, ha="left", va="top")
    fig.text(
        0.035,
        0.965,
        "Retention and release curves",
        fontsize=8.1,
        ha="left",
        va="top",
    )
    fig.text(0.01, 0.49, "b", fontweight="bold", fontsize=9.0, ha="left", va="top")
    fig.text(
        0.035,
        0.49,
        "Paired release-minus-retention differences",
        fontsize=8.1,
        ha="left",
        va="top",
    )
    return save_pdf(fig, OUT_INTERVENTION)


def draw_forest(
    ax: plt.Axes,
    rows_by_arch: dict[str, dict[str, str]],
    title: str,
    show_labels: bool,
) -> None:
    y = np.arange(len(ARCH_ORDER))[::-1]
    mean = np.array([float(rows_by_arch[a]["mean"]) for a in ARCH_ORDER])
    low = np.array([float(rows_by_arch[a]["ci_low"]) for a in ARCH_ORDER])
    high = np.array([float(rows_by_arch[a]["ci_high"]) for a in ARCH_ORDER])
    xerr = np.vstack([mean - low, high - mean])

    ax.axvline(0, linewidth=0.7, zorder=0)
    ax.errorbar(
        mean,
        y,
        xerr=xerr,
        fmt="o",
        markersize=3.0,
        linewidth=0.8,
        capsize=1.7,
        capthick=0.6,
        zorder=3,
    )
    ax.set_title(title, pad=3)
    ax.set_yticks(y)
    if show_labels:
        ax.set_yticklabels([ARCH_LABELS[a] for a in ARCH_ORDER], fontsize=6.1)
    else:
        ax.set_yticklabels([])
    ax.set_ylim(-0.8, len(ARCH_ORDER) - 0.2)
    ax.set_xlabel(r"Intervention-size contrast, $B$")
    ax.grid(axis="y", visible=False)

    for after in (2, 6, 10, 12, 14):
        ypos = len(ARCH_ORDER) - after - 0.5
        ax.axhline(ypos, linewidth=0.5, zorder=0)


def build_architecture_figure(rows: list[dict[str, str]]) -> Path:
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.15, 4.55),
        gridspec_kw={"width_ratios": [1.08, 0.92]},
    )
    fig.subplots_adjust(left=0.24, right=0.99, top=0.91, bottom=0.12, wspace=0.17)

    for i, (metric, label) in enumerate(ARCH_METRICS):
        draw_forest(
            axes[i],
            architecture_rows(rows, metric),
            label,
            show_labels=(i == 0),
        )

    fig.text(
        0.01,
        0.965,
        "Architecture dependence on 100 independent renderer blocks",
        fontsize=8.1,
        ha="left",
        va="top",
    )
    return save_pdf(fig, OUT_ARCHITECTURE)


def build_figure() -> tuple[Path, Path]:
    apply_paper_style()
    OUT_INTERVENTION.parent.mkdir(parents=True, exist_ok=True)

    contrast_table = read_csv(CONTRAST_TABLE)
    model_table = read_csv(MODEL_TABLE)
    arch_table = read_csv(ARCH_TABLE)

    intervention = build_intervention_figure(contrast_table, model_table)
    architecture = build_architecture_figure(arch_table)
    return intervention, architecture


def main() -> None:
    paths = build_figure()
    plt.close("all")
    for path in paths:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
