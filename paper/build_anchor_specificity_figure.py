#!/usr/bin/env python3
"""Build the matched-anchor specificity figure from archived Stage-G outputs.

Panel (a) shows the architecture-specific selected-channel difference between
structured and pixel-permuted anchors on the primary task.
Panel (b) compares architecture-averaged selected- and random-channel effects
against the equivalence margins frozen before the full run.

Presentation-only: this script reads versioned aggregate CSVs and does not
recompute scientific statistics.
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
OUT = PAPER / "figures" / "fig07_anchor_specificity.pdf"

ANALYSIS = ROOT / "analysis" / "anchor_specificity_001"
SECONDARY = ANALYSIS / "secondary_anchor_contrasts.csv"
PRIMARY = ANALYSIS / "primary_spatial_specificity.csv"
RANDOM = ANALYSIS / "random_channel_spatial_specificity.csv"

METRICS = (
    ("centered_logit_fidelity", r"$B_{\mathrm{clogit}}$", "#0072B2"),
    ("prob_error_reduction", r"$B_{R_{\mathrm{prob}}}$", "#D55E00"),
)

ARCH_ORDER = (
    "tiny_gmp",
    "tiny_gap",
    "plain2_w16_gmp",
    "plain2_w16_gap",
)
ARCH_LABELS = {
    "tiny_gmp": "Tiny · GMP",
    "tiny_gap": "Tiny · GAP",
    "plain2_w16_gmp": "Plain-2 · GMP",
    "plain2_w16_gap": "Plain-2 · GAP",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def architecture_effects(rows: list[dict[str, str]], metric: str) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if row["task"] == "two_concepts"
        and row["metric"] == metric
        and row["contrast"] == "structured - pixel_permuted"
        and row["architecture"] in ARCH_ORDER
    ]
    by_arch = {row["architecture"]: row for row in selected}
    missing = [a for a in ARCH_ORDER if a not in by_arch]
    if missing:
        raise ValueError(f"Missing architecture specificity rows for {metric}: {missing}")
    return [by_arch[a] for a in ARCH_ORDER]


def draw_architecture_panel(ax, rows: list[dict[str, str]], title: str, color: str, show_labels: bool) -> None:
    y = np.arange(len(ARCH_ORDER))[::-1]
    mean = np.array([float(r["mean"]) for r in rows])
    low = np.array([float(r["ci_low"]) for r in rows])
    high = np.array([float(r["ci_high"]) for r in rows])
    xerr = np.vstack([mean - low, high - mean])

    ax.axvline(0.0, color="#555555", linewidth=0.7, zorder=0)
    ax.errorbar(
        mean, y, xerr=xerr, fmt="o", color=color,
        markersize=3.5, linewidth=0.9, capsize=2.0, capthick=0.7, zorder=3
    )
    ax.set_title(title, pad=3)
    ax.set_yticks(y)
    ax.set_yticklabels([ARCH_LABELS[a] for a in ARCH_ORDER] if show_labels else [])
    ax.set_xlabel("Structured − pixel-permuted")
    ax.grid(axis="y", visible=False)


def draw_equivalence_panel(ax, primary_rows, random_rows, metric: str, title: str, color: str) -> None:
    p = next(r for r in primary_rows if r["metric"] == metric)
    q = next(r for r in random_rows if r["metric"] == metric)
    margin = float(p["equivalence_margin"])

    # Equivalence is assessed with 90% CIs under the frozen TOST rule.
    means = [float(p["mean"]), float(q["mean"])]
    lows = [float(p["equivalence_ci90_low"]), float(q["equivalence_ci90_low"])]
    highs = [float(p["equivalence_ci90_high"]), float(q["equivalence_ci90_high"])]
    y = np.array([1.0, 0.0])

    ax.axvspan(-margin, margin, color="#E5E7EB", alpha=0.65, zorder=0)
    ax.axvline(0.0, color="#555555", linewidth=0.7, zorder=1)
    ax.axvline(-margin, color="#9CA3AF", linewidth=0.6, linestyle="--", zorder=1)
    ax.axvline(+margin, color="#9CA3AF", linewidth=0.6, linestyle="--", zorder=1)

    xerr = np.vstack([np.array(means) - np.array(lows), np.array(highs) - np.array(means)])
    ax.errorbar(
        means, y, xerr=xerr, fmt="o", color=color,
        markersize=3.6, linewidth=0.9, capsize=2.0, capthick=0.7, zorder=3
    )
    ax.set_yticks(y)
    ax.set_yticklabels(["Selected", "Random"])
    ax.set_title(title, pad=3)
    ax.set_xlabel("Architecture-averaged difference")
    ax.set_ylim(-0.6, 1.6)
    ax.grid(axis="y", visible=False)


def build_figure() -> Path:
    apply_paper_style()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    secondary = read_csv(SECONDARY)
    primary = read_csv(PRIMARY)
    random_rows = read_csv(RANDOM)

    fig = plt.figure(figsize=(7.15, 4.15))
    outer = fig.add_gridspec(
        2, 1, height_ratios=[1.35, 1.0],
        hspace=0.52, left=0.10, right=0.99, top=0.94, bottom=0.12
    )

    top = outer[0].subgridspec(1, 2, wspace=0.20)
    top_axes = []
    for i, (metric, label, color) in enumerate(METRICS):
        ax = fig.add_subplot(top[0, i])
        draw_architecture_panel(
            ax,
            architecture_effects(secondary, metric),
            label,
            color,
            show_labels=(i == 0),
        )
        top_axes.append(ax)
    top_axes[0].text(
        -0.27, 1.13, "a", transform=top_axes[0].transAxes,
        fontweight="bold", fontsize=9.0, va="top"
    )
    top_axes[0].text(
        -0.16, 1.13, "Spatial-structure effect reverses with downstream architecture",
        transform=top_axes[0].transAxes, fontsize=8.2, va="top"
    )

    bottom = outer[1].subgridspec(1, 2, wspace=0.24)
    bottom_axes = []
    for i, (metric, label, color) in enumerate(METRICS):
        ax = fig.add_subplot(bottom[0, i])
        draw_equivalence_panel(ax, primary, random_rows, metric, label, color)
        bottom_axes.append(ax)
    bottom_axes[0].text(
        -0.27, 1.18, "b", transform=bottom_axes[0].transAxes,
        fontweight="bold", fontsize=9.0, va="top"
    )
    bottom_axes[0].text(
        -0.16, 1.18, "Selected-channel specificity is stronger than random-channel specificity",
        transform=bottom_axes[0].transAxes, fontsize=8.2, va="top"
    )

    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
