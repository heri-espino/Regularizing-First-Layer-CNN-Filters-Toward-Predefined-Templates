#!/usr/bin/env python3
"""Build direct observed-versus-additive curve diagnostics for the SN paper.

Panels (a) and (b) show the release-minus-retention centered-logit fidelity
curve on the primary two_concepts task for an analytically additive Tiny model
and a deeper architecture with a large reconstruction gap. Panel (c) shows the
centered-logit residual-energy ratio for the same architectures and treatments.

Presentation-only: this script reads archived aggregate CSVs. It does not
retrain models or recompute inferential statistics.
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
OUT = PAPER / "figures" / "fig09_additivity_curves.pdf"
CURVE_TABLE = (
    ROOT
    / "analysis"
    / "patching_additivity_001"
    / "architecture_analysis"
    / "curve_summary.csv"
)

TASK = "two_concepts"
ARCHITECTURES = (
    ("tiny_gmp", "Tiny · GMP"),
    ("bn2_w16_gap", "BN-2 w16 · GAP"),
)
TREATMENTS = (
    ("release_default", "Release", "-"),
    ("retention_1", "Retention", "--"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean_value(
    rows: list[dict[str, str]],
    architecture: str,
    treatment: str,
    k: int,
    quantity: str,
) -> float:
    matches = [
        row
        for row in rows
        if row["task"] == TASK
        and row["architecture"] == architecture
        and row["anchor_family"] == "not_applicable"
        and row["treatment"] == treatment
        and int(row["k"]) == k
        and row["quantity"] == quantity
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one row for {architecture}/{treatment}/k={k}/{quantity}; "
            f"found {len(matches)}"
        )
    return float(matches[0]["mean"])


def treatment_difference(
    rows: list[dict[str, str]],
    architecture: str,
    quantity: str,
) -> tuple[np.ndarray, np.ndarray]:
    ks = np.arange(0, 17, dtype=int)
    release = np.array(
        [mean_value(rows, architecture, "release_default", int(k), quantity) for k in ks]
    )
    retention = np.array(
        [mean_value(rows, architecture, "retention_1", int(k), quantity) for k in ks]
    )
    return ks, release - retention


def draw_delta_panel(
    ax,
    rows: list[dict[str, str]],
    architecture: str,
    title: str,
) -> None:
    for quantity, label, marker in (
        ("observed_centered_logit_fidelity", "Observed", "o"),
        ("additive_centered_logit_fidelity", "Additive", "s"),
    ):
        ks, delta = treatment_difference(rows, architecture, quantity)
        ax.plot(
            ks,
            delta,
            marker=marker,
            markersize=2.8,
            linewidth=1.15,
            label=label,
        )
    ax.axhline(0.0, linewidth=0.7, color="#666666")
    ax.set_title(title, pad=3)
    ax.set_xticks([0, 4, 8, 12, 16])
    ax.set_xlabel("Patched channels, $k$")
    ax.grid(axis="x", visible=False)


def draw_residual_panel(ax, rows: list[dict[str, str]]) -> None:
    # k=0 and k=1 are exactly zero by construction, so a logarithmic view starts
    # at k=2. This makes the floating-point Tiny residual visible next to the
    # much larger residual of the deeper model.
    ks = np.arange(2, 17, dtype=int)
    for architecture, arch_label in ARCHITECTURES:
        for treatment, treatment_label, linestyle in TREATMENTS:
            y = np.array(
                [
                    mean_value(
                        rows,
                        architecture,
                        treatment,
                        int(k),
                        "centered_residual_energy_ratio",
                    )
                    for k in ks
                ]
            )
            ax.plot(
                ks,
                y,
                linestyle=linestyle,
                linewidth=1.15,
                marker="o" if architecture == "tiny_gmp" else "s",
                markersize=2.5,
                label=f"{arch_label}, {treatment_label}",
            )
    ax.set_yscale("log")
    ax.set_title("Centered residual energy", pad=3)
    ax.set_xlabel("Patched channels, $k$")
    ax.set_ylabel(r"$\rho(S)$")
    ax.set_xticks([2, 4, 8, 12, 16])
    ax.grid(axis="x", visible=False)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=2,
        fontsize=6.3,
        frameon=False,
        columnspacing=1.0,
        handlelength=2.0,
    )


def build_figure() -> Path:
    apply_paper_style()
    rows = read_csv(CURVE_TABLE)

    fig = plt.figure(figsize=(7.15, 3.05))
    grid = fig.add_gridspec(
        1,
        3,
        width_ratios=[1.0, 1.0, 1.08],
        wspace=0.34,
        left=0.08,
        right=0.99,
        top=0.87,
        bottom=0.28,
    )
    axes = [fig.add_subplot(grid[0, i]) for i in range(3)]

    draw_delta_panel(axes[0], rows, "tiny_gmp", "Tiny · GMP")
    draw_delta_panel(axes[1], rows, "bn2_w16_gap", "BN-2 w16 · GAP")
    axes[0].set_ylabel(
        "Release $-$ retention\ncentered-logit fidelity"
    )
    axes[1].set_ylabel("")
    axes[0].legend(loc="lower right", fontsize=6.3, frameon=False)

    draw_residual_panel(axes[2], rows)

    for x, label in ((0.012, "a"), (0.338, "b"), (0.665, "c")):
        fig.text(x, 0.965, label, fontweight="bold", fontsize=9, va="top")

    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
