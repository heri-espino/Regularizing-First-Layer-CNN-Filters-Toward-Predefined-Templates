#!/usr/bin/env python3
"""Build the compact additive-decomposition figure for the SN Computer Science paper.

Panel (a) compares the observed intervention-size contrast B with the singleton-additive
reconstruction across all 16 architectures on the primary two_concepts task.
Panel (b) shows that the structured-versus-pixel-permuted effect is largely preserved
by the additive reconstruction when averaged across the four spatial-control architectures.

Presentation-only: this script reads archived aggregate CSVs and does not recompute
scientific statistics.
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
OUT = PAPER / "figures" / "fig08_additivity.pdf"

ARCH_TABLE = ROOT / "analysis" / "patching_additivity_001" / "architecture_analysis" / "B_summary.csv"
ANCHOR_TABLE = (
    ROOT
    / "analysis"
    / "patching_additivity_001"
    / "anchor_analysis"
    / "structured_vs_pixel_permuted_B_averaged_architectures.csv"
)

METRICS = (
    ("centered_logit_fidelity", "Centered-logit fidelity", "#0072B2"),
    ("prob_error_reduction", "Probability-error reduction", "#D55E00"),
)

HIGHLIGHT_LABELS = {
    "tiny_gmp": "Tiny-GMP",
    "bn2_w16_gap": "BN2-GAP",
}

HIGHLIGHT_OFFSETS = {
    ("centered_logit_fidelity", "tiny_gmp"): (-7, 7),
    ("centered_logit_fidelity", "bn2_w16_gap"): (7, -12),
    ("prob_error_reduction", "tiny_gmp"): (-7, 7),
    ("prob_error_reduction", "bn2_w16_gap"): (7, -12),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def architecture_pairs(rows: list[dict[str, str]], metric: str) -> list[tuple[str, float, float]]:
    relevant = [
        row
        for row in rows
        if row["task"] == "two_concepts"
        and row["metric"] == metric
        and row["set_family"] == "selected"
        and row["anchor_family"] == "not_applicable"
    ]
    by_arch: dict[str, dict[str, float]] = {}
    for row in relevant:
        by_arch.setdefault(row["architecture"], {})[row["curve"]] = float(row["mean"])
    pairs = []
    for architecture, values in sorted(by_arch.items()):
        if "observed" in values and "additive" in values:
            pairs.append((architecture, values["additive"], values["observed"]))
    if len(pairs) != 16:
        raise ValueError(f"Expected 16 architecture pairs for {metric}, got {len(pairs)}")
    return pairs


def anchor_values(rows: list[dict[str, str]], metric: str) -> tuple[tuple[float, float], tuple[float, float]]:
    relevant = [r for r in rows if r["task"] == "two_concepts" and r["metric"] == metric]
    by_curve = {r["curve"]: r for r in relevant}
    observed = by_curve["observed"]
    additive = by_curve["additive"]
    return (
        (float(observed["mean"]), float(observed["ci_low"]), float(observed["ci_high"])),
        (float(additive["mean"]), float(additive["ci_low"]), float(additive["ci_high"])),
    )


def build_figure() -> Path:
    apply_paper_style()
    arch_rows = read_csv(ARCH_TABLE)
    anchor_rows = read_csv(ANCHOR_TABLE)

    fig = plt.figure(figsize=(7.15, 3.45))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.88], wspace=0.42)
    axes = [fig.add_subplot(grid[0, i]) for i in range(3)]

    for ax, (metric, title, color) in zip(axes[:2], METRICS):
        pairs = architecture_pairs(arch_rows, metric)
        x = np.array([p[1] for p in pairs])
        y = np.array([p[2] for p in pairs])
        lo = min(float(x.min()), float(y.min()))
        hi = max(float(x.max()), float(y.max()))
        pad = 0.08 * max(hi - lo, 1e-6)
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="#777777", linewidth=0.8, linestyle="--")
        ax.scatter(x, y, s=18, color=color, alpha=0.82, zorder=3)

        for architecture, additive, observed in pairs:
            if architecture in HIGHLIGHT_LABELS:
                ax.annotate(
                    HIGHLIGHT_LABELS[architecture],
                    (additive, observed),
                    xytext=HIGHLIGHT_OFFSETS[(metric, architecture)],
                    textcoords="offset points",
                    fontsize=6.2,
                    ha="right" if architecture == "tiny_gmp" else "left",
                    va="bottom" if architecture == "tiny_gmp" else "top",
                )

        ax.set_title(title, pad=4)
        ax.set_xlabel("Additive reconstruction, $B$")
        ax.set_ylabel("Observed, $B$")
        ax.grid(True, linewidth=0.4, alpha=0.55)

    ax = axes[2]
    y_positions = np.array([1.0, 0.0])
    offset = 0.10
    for i, (metric, title, color) in enumerate(METRICS):
        observed, additive = anchor_values(anchor_rows, metric)
        y = y_positions[i]
        for label, values, dy, marker in (
            ("Observed", observed, +offset, "o"),
            ("Additive", additive, -offset, "s"),
        ):
            mean, low, high = values
            ax.errorbar(
                mean,
                y + dy,
                xerr=np.array([[mean - low], [high - mean]]),
                fmt=marker,
                color=color,
                markersize=4.0,
                linewidth=0.9,
                capsize=2.0,
                label=label if i == 0 else None,
                zorder=3,
            )
    ax.axvline(0.0, color="#777777", linewidth=0.7)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    # Keep the metric labels inside the spatial panel so they do not crowd the
    # Tiny-GMP annotation or the separator between panels.
    ax.text(
        0.03, 0.88, "Centered logits",
        transform=ax.transAxes, ha="left", va="center", fontsize=6.4,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.82, pad=0.7),
        zorder=4,
    )
    ax.text(
        0.03, 0.18, "Probability error",
        transform=ax.transAxes, ha="left", va="center", fontsize=6.4,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.82, pad=0.7),
        zorder=4,
    )
    ax.set_xlabel("Structured $-$ pixel-permuted, $B$")
    ax.set_title("Spatial-bank effect", pad=4)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=6.2, frameon=False)

    fig.text(0.01, 0.98, "a", fontweight="bold", fontsize=9, va="top")
    fig.text(0.675, 0.98, "b", fontweight="bold", fontsize=9, va="top")
    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
