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

    # Light gray band = the pre-specified TOST equivalence region.  Label it
    # directly so the background encoding is understandable without relying on
    # the caption.
    ax.axvspan(-margin, margin, color="#E5E7EB", alpha=0.55, zorder=0)
    ax.axvline(0.0, color="#555555", linewidth=0.7, zorder=1)
    ax.axvline(-margin, color="#9CA3AF", linewidth=0.6, linestyle="--", zorder=1)
    ax.axvline(+margin, color="#9CA3AF", linewidth=0.6, linestyle="--", zorder=1)
    ax.text(
        0.0, 0.96, "pre-specified\nequivalence region",
        transform=ax.get_xaxis_transform(),
        ha="center", va="top", fontsize=5.5, color="#6B7280",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.82, pad=0.8),
        zorder=4,
    )

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

    # As in Figure 6, panel headings get dedicated rows.  This keeps panel
    # letters and long titles aligned to the same left edge and removes the
    # large vertical gaps caused by negative axes coordinates.
    fig = plt.figure(figsize=(7.15, 4.15))
    outer = fig.add_gridspec(
        5,
        1,
        height_ratios=[0.18, 1.18, 0.18, 0.22, 0.82],
        hspace=0.20,
        left=0.13,
        right=0.99,
        top=0.975,
        bottom=0.12,
    )

    header_a = fig.add_subplot(outer[0])
    header_a.axis("off")
    header_a.text(
        0.0, 0.50, "a", fontweight="bold", fontsize=9.0,
        ha="left", va="center", fontstretch="normal",
    )
    header_a.text(
        0.035, 0.50, "Spatial-structure effect reverses with downstream architecture",
        fontsize=8.0, ha="left", va="center", fontstretch="normal",
    )

    top = outer[1].subgridspec(1, 2, wspace=0.20)
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
    top_axes[0].tick_params(axis="y", labelsize=6.0)

    top_xlabel = fig.add_subplot(outer[2])
    top_xlabel.axis("off")
    top_xlabel.text(
        0.5, 0.50, "Structured - pixel-permuted",
        fontsize=8.0, ha="center", va="center",
    )

    header_b = fig.add_subplot(outer[3])
    header_b.axis("off")
    header_b.text(
        0.0, 0.50, "b", fontweight="bold", fontsize=9.0,
        ha="left", va="center", fontstretch="normal",
    )
    header_b.text(
        0.035, 0.50, "Selected-channel specificity versus random-channel specificity",
        fontsize=8.0, ha="left", va="center", fontstretch="normal",
    )

    bottom = outer[4].subgridspec(1, 2, wspace=0.24)
    for i, (metric, label, color) in enumerate(METRICS):
        ax = fig.add_subplot(bottom[0, i])
        draw_equivalence_panel(ax, primary, random_rows, metric, label, color)

    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
