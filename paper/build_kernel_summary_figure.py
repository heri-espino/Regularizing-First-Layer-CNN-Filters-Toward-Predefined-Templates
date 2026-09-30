#!/usr/bin/env python3
"""Build a compact first-layer kernel summary for the main manuscript.

The figure uses actual saved TinyCNN checkpoints from the original
retention/release study. It shows a fixed representative subset of eight
channels at epoch 200 under retention and release, together with their
corresponding predefined templates. The complete 16-channel multi-condition
gallery remains a supplementary diagnostic.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from build_overview_figure import template_bank
from plot_style import apply_paper_style, save_pdf

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
OUT = PAPER / "figures" / "fig01_kernel_summary.pdf"

TASK = "two_concepts"
ARCH = "TinyCNN"
BLOCK = 2000
CHANNELS = (0, 2, 4, 6, 8, 10, 12, 14)


def load_conv(path: Path) -> np.ndarray:
    try:
        import torch
    except ImportError as exc:
        raise SystemExit(
            "The compact kernel summary requires PyTorch because it reads saved checkpoints."
        ) from exc

    saved = torch.load(path, map_location="cpu", weights_only=True)
    return saved["model"]["conv.weight"].detach().cpu().numpy()[:, 0]


def normalize_for_display(kernels: np.ndarray) -> np.ndarray:
    kernels = np.asarray(kernels, dtype=np.float64)
    centered = kernels - kernels.mean(axis=(1, 2), keepdims=True)
    norm = np.sqrt((centered * centered).sum(axis=(1, 2), keepdims=True))
    if np.any(norm < 1e-12):
        raise ValueError("Degenerate kernel in compact summary")
    return centered / norm


def checkpoint(condition: str) -> Path:
    return (
        ROOT
        / "results"
        / "retention_release_001"
        / "runs"
        / TASK
        / ARCH
        / f"block{BLOCK:04d}"
        / condition
        / "epoch_0200.pt"
    )


def build_figure() -> Path:
    apply_paper_style()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    templates = template_bank()[list(CHANNELS)]
    retention = load_conv(checkpoint("template_retention_1"))[list(CHANNELS)]
    release = load_conv(checkpoint("template_release"))[list(CHANNELS)]

    rows = (
        ("Predefined", normalize_for_display(templates)),
        ("Retention", normalize_for_display(retention)),
        ("Release", normalize_for_display(release)),
    )
    limit = max(float(np.abs(kernels).max()) for _, kernels in rows)

    fig, axes = plt.subplots(3, len(CHANNELS), figsize=(7.15, 2.05))
    for i, (label, kernels) in enumerate(rows):
        for j, kernel in enumerate(kernels):
            ax = axes[i, j]
            ax.imshow(
                kernel,
                cmap="RdBu_r",
                vmin=-limit,
                vmax=limit,
                interpolation="nearest",
                rasterized=True,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)
            for spine in ax.spines.values():
                spine.set_visible(False)
            if i == 0:
                ax.set_title(f"ch. {CHANNELS[j]}", fontsize=6.2, pad=1.5)
        axes[i, 0].set_ylabel(
            label,
            rotation=0,
            ha="right",
            va="center",
            fontsize=7.0,
            labelpad=10,
        )

    fig.subplots_adjust(
        left=0.13,
        right=0.995,
        top=0.91,
        bottom=0.03,
        wspace=0.045,
        hspace=0.10,
    )
    return save_pdf(fig, OUT)


def main() -> None:
    path = build_figure()
    plt.close("all")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
