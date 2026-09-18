"""Shared visual style for publication figures.

This module affects presentation only. It does not recompute experimental outcomes.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import seaborn as sns

# Color-blind-friendly palette with stable semantics across the manuscript.
COLORS = {
    "random": "#6B7280",
    "random_unitnorm": "#A7ADB7",
    "template_init": "#0072B2",
    "template_retention_1": "#009E73",
    "template_release": "#D55E00",
    "retention_0p1": "#56B4E9",
    "retention_1": "#009E73",
    "release_early": "#E69F00",
    "release_default": "#D55E00",
    "release_late": "#CC79A7",
}

LABELS = {
    "random": "Random",
    "random_unitnorm": "Unit-norm random",
    "template_init": "Template init.",
    "template_retention_1": "Constant reg.",
    "template_release": "Annealed reg.",
    "retention_0p1": r"Constant $\lambda=0.1$",
    "retention_1": r"Constant $\lambda=1$",
    "release_early": "Early anneal",
    "release_default": "Default anneal",
    "release_late": "Late anneal",
}

LINESTYLES = {
    "random": (0, (3, 2)),
    "random_unitnorm": (0, (1, 1.5)),
    "template_init": "-.",
    "template_retention_1": "-",
    "template_release": "-",
    "retention_0p1": (0, (3, 2)),
    "retention_1": "-",
    "release_early": "-.",
    "release_default": "-",
    "release_late": (0, (1, 1.5)),
}


def apply_paper_style() -> None:
    """Apply a restrained white-grid style compatible with the TMLR manuscript."""

    sns.set_theme(style="whitegrid", context="paper")
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": [
                "Latin Modern Roman",
                "Computer Modern Roman",
                "CMU Serif",
                "DejaVu Serif",
            ],
            "mathtext.fontset": "cm",
            "font.size": 8.0,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8.0,
            "legend.fontsize": 7.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.edgecolor": "#444444",
            "axes.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": "#D5D9DE",
            "grid.linewidth": 0.45,
            "grid.alpha": 0.65,
            "lines.linewidth": 1.35,
            "lines.markersize": 3.0,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_pdf(fig, path: str | Path) -> Path:
    """Save a publication figure as PDF with vector text/lines.

    Dense image artists can opt into ``rasterized=True``; those layers are then
    rasterized inside the PDF while typography, axes, and annotations remain vector.
    """

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, format="pdf")
    return target
