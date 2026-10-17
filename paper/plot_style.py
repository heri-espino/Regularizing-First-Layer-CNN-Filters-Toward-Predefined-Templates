"""Shared visual style for publication figures.

This module affects presentation only. It does not recompute experimental outcomes.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import matplotlib as mpl
from matplotlib import font_manager
import seaborn as sns

# Color-blind-friendly palette; manuscript-facing regularization labels are defined below and reused across figures.
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
    "template_init": "Initialization only",
    "template_retention_1": "Constant reg.",
    "template_release": "Annealed reg.",
    "retention_0p1": r"Constant $\lambda=0.1$",
    "retention_1": r"Constant $\lambda=1$",
    "release_early": "Early annealing",
    "release_default": "Default annealing",
    "release_late": "Late annealing",
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

# A visual role keeps the same encoding wherever observed joint interventions
# are compared with a reconstruction from individual interventions.
ROLE_STYLES = {
    "observed": {
        "color": "#0072B2",
        "linestyle": "-",
        "marker": "o",
        "label": "Observed joint patch",
    },
    "additive": {
        "color": "#D55E00",
        "linestyle": "--",
        "marker": "s",
        "label": "Additive reconstruction",
    },
}


def _register_latin_modern() -> bool:
    """Register the same OpenType text face that the TMLR style loads."""

    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich is None:
        return False
    try:
        result = subprocess.run(
            [kpsewhich, "lmroman10-regular.otf"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False

    regular = Path(result.stdout.strip())
    if not regular.is_file():
        return False
    for name in (
        "lmroman10-regular.otf",
        "lmroman10-bold.otf",
        "lmroman10-italic.otf",
        "lmroman10-bolditalic.otf",
    ):
        candidate = regular.with_name(name)
        if candidate.is_file():
            font_manager.fontManager.addfont(candidate)
    return True


def apply_paper_style() -> None:
    """Apply a restrained white-grid style compatible with the TMLR manuscript."""

    latin_modern_available = _register_latin_modern()
    sns.set_theme(style="whitegrid", context="paper")
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": (
                ["Latin Modern Roman", "DejaVu Serif"]
                if latin_modern_available
                else ["DejaVu Serif"]
            ),
            "mathtext.fontset": "cm",
            "font.size": 8.0,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8.0,
            "legend.fontsize": 7.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.edgecolor": "#444444",
            "axes.linewidth": 0.75,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": True,
            "axes.spines.bottom": True,
            "axes.axisbelow": True,
            "grid.color": "#D5D9DE",
            "grid.linewidth": 0.45,
            "grid.alpha": 0.62,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.bottom": True,
            "ytick.left": True,
            "xtick.top": False,
            "ytick.right": False,
            "xtick.color": "#444444",
            "ytick.color": "#444444",
            "xtick.major.size": 4.2,
            "ytick.major.size": 4.2,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.minor.visible": False,
            "ytick.minor.visible": False,
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


def synchronize_tick_visibility(fig) -> None:
    """Show tick marks only on axes that also show the corresponding labels."""

    fig.canvas.draw()
    for ax in fig.axes:
        has_xlabels = any(
            label.get_visible() and label.get_text().strip()
            for label in ax.get_xticklabels()
        )
        has_ylabels = any(
            label.get_visible() and label.get_text().strip()
            for label in ax.get_yticklabels()
        )
        ax.tick_params(axis="x", bottom=has_xlabels)
        ax.tick_params(axis="y", left=has_ylabels)


def save_pdf(fig, path: str | Path) -> Path:
    """Save a publication figure as PDF with vector text/lines.

    Dense image artists can opt into ``rasterized=True``; those layers are then
    rasterized inside the PDF while typography, axes, and annotations remain vector.
    """

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    synchronize_tick_visibility(fig)
    fig.savefig(target, format="pdf")
    return target
