#!/usr/bin/env python3
"""Build the manuscript's central robustness figure from archived analysis tables.

Panel (a) shows the annealed-minus-constant treatment difference as a function
of patched first-layer channel count in the prospective two_concepts/TinyCNN
experiment under the historical probability metric and the two frozen
alternative metrics.

Panel (b) shows the architecture-specific channel-count contrast B for the 16
architectures in the prospective architecture-robustness experiment under the
two primary metrics.

This script is presentation-only. It reads versioned aggregate CSVs and does
not retrain models or recompute inferential statistics.
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
OUT = PAPER / "figures" / "fig06_main_results.pdf"

METRIC_TABLE = ROOT / "analysis" / "metric_sensitivity_001" / "stage_d_treatment_contrasts.csv"
ARCH_TABLE = ROOT / "analysis" / "architecture_robustness_001" / "architecture_B_summary.csv"

TOP_METRICS = (
    ("prob_fidelity", r"$F_{\mathrm{prob}}$", "#6B7280"),
    ("centered_logit_fidelity", r"$F_{\mathrm{clogit}}$", "#0072B2"),
    ("prob_error_reduction", r"$R_{\mathrm{prob}}$", "#D55E00"),
)

ARCH_METRICS = (
    ("centered_logit_fidelity", r"$B_{\mathrm{clogit}}$", "#0072B2"),
    ("prob_error_reduction", r"$B_{R_{\mathrm{prob}}}$", "#D55E00"),
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


def prospective_rows(rows: list[dict[str, str]], metric: str) -> list[dict[str, str]]:
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
        raise ValueError(f"Unexpected prospective rows for {metric}")
    return selected


def architecture_rows(rows: list[dict[str, str]], metric: str) -> dict[str, dict[str, str]]:
    selected = {
        row["architecture"]: row
        for row in rows
        if row["task"] == "two_concepts" and row["metric"] == metric
    }
    missing = [arch for arch in ARCH_ORDER if arch not in selected]
    if missing:
        raise ValueError(f"Missing architecture rows for {metric}: {missing}")
    return selected


def draw_top_metric(ax, rows, title: str, color: str) -> None:
    x = np.array([int(row["k"]) for row in rows], dtype=float)
    mean = np.array([float(row["mean"]) for row in rows])
    low = np.array([float(row["ci_low"]) for row in rows])
    high = np.array([float(row["ci_high"]) for row in rows])
    yerr = np.vstack([mean - low, high - mean])

    ax.axhline(0, color="#555555", linewidth=0.7, zorder=0)
    ax.errorbar(
        x,
        mean,
        yerr=yerr,
        color=color,
        marker="o",
        markersize=3.6,
        linewidth=1.45,
        capsize=2.0,
        capthick=0.7,
        zorder=3,
    )
    ax.set_title(title, pad=3)
    ax.set_xticks([1, 2, 4, 8])
    ax.set_xlabel(r"Patched channels, $k$")
    ax.grid(axis="x", visible=False)


def draw_forest(ax, rows_by_arch, title: str, color: str, show_labels: bool) -> None:
    y = np.arange(len(ARCH_ORDER))[::-1]
    mean = np.array([float(rows_by_arch[a]["mean"]) for a in ARCH_ORDER])
    low = np.array([float(rows_by_arch[a]["ci_low"]) for a in ARCH_ORDER])
    high = np.array([float(rows_by_arch[a]["ci_high"]) for a in ARCH_ORDER])
    xerr = np.vstack([mean - low, high - mean])

    ax.axvline(0, color="#555555", linewidth=0.7, zorder=0)
    ax.errorbar(
        mean,
        y,
        xerr=xerr,
        fmt="o",
        color=color,
        markersize=3.0,
        linewidth=0.8,
        capsize=1.7,
        capthick=0.6,
        zorder=3,
    )
    ax.set_title(title, pad=3)
    ax.set_yticks(y)
    if show_labels:
        ax.set_yticklabels([ARCH_LABELS[a] for a in ARCH_ORDER], fontsize=6.2)
    else:
        ax.set_yticklabels([])
    ax.set_ylim(-0.8, len(ARCH_ORDER) - 0.2)
    ax.set_xlabel(r"Channel-count contrast, $B$")
    ax.grid(axis="y", visible=False)

    # Visual separators preserve the prespecified architecture-family ordering
    # without assigning inferential meaning to the groups.
    for after in (2, 6, 10, 12, 14):
        ypos = len(ARCH_ORDER) - after - 0.5
        ax.axhline(ypos, color="#D9D9D9", linewidth=0.5, zorder=0)


def build_figure() -> Path:
    apply_paper_style()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    metric_rows = read_csv(METRIC_TABLE)
    arch_rows = read_csv(ARCH_TABLE)

    fig = plt.figure(figsize=(7.15, 6.05))
    outer = fig.add_gridspec(
        2,
        1,
        height_ratios=[1.0, 2.15],
        hspace=0.44,
        left=0.075,
        right=0.99,
        top=0.96,
        bottom=0.075,
    )

    top = outer[0].subgridspec(1, 3, wspace=0.34)
    top_axes = []
    for i, (metric, label, color) in enumerate(TOP_METRICS):
        ax = fig.add_subplot(top[0, i])
        draw_top_metric(ax, prospective_rows(metric_rows, metric), label, color)
        top_axes.append(ax)

    # Give normalized fidelities comparable visual headroom while retaining
    # their actual numerical scales. The unnormalized metric keeps its own scale.
    top_axes[0].set_ylabel(r"Annealed $-$ constant, $\Delta^M(k)$")
    top_axes[1].set_ylabel("")
    top_axes[2].set_ylabel("")
    top_axes[0].text(
        -0.38, 1.13, "a", transform=top_axes[0].transAxes,
        fontweight="bold", fontsize=9.0, va="top"
    )
    top_axes[0].text(
        -0.25, 1.13, "Prospective channel-count pattern and metric robustness",
        transform=top_axes[0].transAxes, fontsize=8.3, va="top"
    )

    bottom = outer[1].subgridspec(1, 2, width_ratios=[1.06, 0.94], wspace=0.16)
    bottom_axes = []
    for i, (metric, label, color) in enumerate(ARCH_METRICS):
        ax = fig.add_subplot(bottom[0, i])
        draw_forest(
            ax,
            architecture_rows(arch_rows, metric),
            label,
            color,
            show_labels=(i == 0),
        )
        bottom_axes.append(ax)

    bottom_axes[0].text(
        -0.38, 1.065, "b", transform=bottom_axes[0].transAxes,
        fontweight="bold", fontsize=9.0, va="top"
    )
    bottom_axes[0].text(
        -0.25, 1.065, "Architecture dependence on 100 fresh renderer blocks",
        transform=bottom_axes[0].transAxes, fontsize=8.3, va="top"
    )

    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
