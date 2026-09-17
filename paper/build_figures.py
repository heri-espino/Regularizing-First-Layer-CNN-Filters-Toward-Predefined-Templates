#!/usr/bin/env python3
"""Regenerate the five figures used by the manuscript from saved artifacts.

The script is presentation-only: it reads immutable/saved analysis outputs and
checkpoints, and does not train models or change any statistical result.

Usage from the repository root::

    python paper/build_figures.py

Requirements are provided by ``pyproject.toml``; PyTorch is needed only for the
kernel gallery (Figure 5).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from plot_style import COLORS, LABELS, LINESTYLES, apply_paper_style, save_pdf

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
OUT = PAPER / "figures"

TASKS = ("single_shape", "two_concepts")
ARCHS = ("TinyCNN", "TwoLayerCNN")
SETTINGS = tuple((task, arch) for task in TASKS for arch in ARCHS)
STAGE_B_CONDITIONS = (
    "random",
    "random_unitnorm",
    "template_init",
    "template_retention_1",
    "template_release",
)
STAGE_E_PROFILES = (
    "template_init",
    "retention_0p1",
    "retention_1",
    "release_early",
    "release_default",
    "release_late",
)


def pretty_task(task: str) -> str:
    return task.replace("_", " ")


def normalized(weights: np.ndarray) -> np.ndarray:
    w = np.asarray(weights, dtype=np.float64).reshape(len(weights), -1)
    centered = w - w.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    if np.any(norms < 1e-12):
        raise ValueError("Degenerate centered kernel")
    return centered / norms


def assignment_columns(weights: np.ndarray, templates: np.ndarray) -> np.ndarray:
    a = normalized(weights)
    b = normalized(templates)
    sim = np.clip(a @ b.T, -1.0, 1.0)
    rows, cols = linear_sum_assignment(-sim)
    if not np.array_equal(rows, np.arange(len(rows))):
        raise ValueError("Unexpected assignment row order")
    return cols


def fig1_learning() -> Path:
    data = pd.read_csv(ROOT / "results/retention_release_001/analysis/learning_curves.csv")
    metrics = (
        ("val_acc", "Validation accuracy"),
        ("val_ce", "Validation cross-entropy"),
        ("alignment", "Kernel-template similarity"),
    )

    fig, axes = plt.subplots(3, 4, figsize=(7.15, 5.15), sharex=True, sharey="row")
    for j, (task, arch) in enumerate(SETTINGS):
        subset = data[(data.task == task) & (data.architecture == arch)]
        for i, (metric, ylabel) in enumerate(metrics):
            ax = axes[i, j]
            for condition in STAGE_B_CONDITIONS:
                g = subset[subset.condition == condition].groupby("epoch")[metric]
                mean = g.mean()
                sd = g.std()
                width = 1.75 if condition in ("template_retention_1", "template_release") else 1.15
                alpha = 1.0 if condition in ("template_retention_1", "template_release") else 0.85
                ax.plot(
                    mean.index,
                    mean,
                    color=COLORS[condition],
                    linestyle=LINESTYLES[condition],
                    linewidth=width,
                    alpha=alpha,
                    label=LABELS[condition],
                )
                ax.fill_between(
                    mean.index,
                    mean - sd,
                    mean + sd,
                    color=COLORS[condition],
                    alpha=0.08,
                    linewidth=0,
                )
            ax.axvline(80, color="#7A7A7A", linestyle=(0, (2, 2)), linewidth=0.7, zorder=0)
            if j == 0:
                ax.set_ylabel(ylabel)
            if i == 0:
                ax.set_title(f"{pretty_task(task)}\n{arch}")
            if i == 2:
                ax.set_xlabel("Epoch")
            ax.set_xticks([0, 50, 100, 150, 200])

    axes[0, 0].set_ylim(0.20, 1.02)
    axes[2, 0].set_ylim(0.0, 1.02)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=5,
        columnspacing=1.1,
        handlelength=2.2,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1), h_pad=0.75, w_pad=0.55)
    return save_pdf(fig, OUT / "fig01_learning.pdf")


def fig2_patch_size() -> Path:
    curves = pd.read_csv(ROOT / "analysis/exhaustive_robustness_001/full_budget_curves.csv")
    curves = curves[(curves.method == "contrast") & (curves.metric == "fidelity")]

    fig, axes = plt.subplots(2, 2, figsize=(7.15, 4.75), sharex=True, sharey=True)
    for i, task in enumerate(TASKS):
        for j, arch in enumerate(ARCHS):
            ax = axes[i, j]
            subset = curves[(curves.task == task) & (curves.architecture == arch)]
            for profile in STAGE_E_PROFILES:
                q = subset[subset.profile == profile].sort_values("k")
                primary = profile in ("retention_1", "release_default")
                ax.plot(
                    q.k,
                    q["mean"],
                    color=COLORS[profile],
                    linestyle=LINESTYLES[profile],
                    linewidth=1.8 if primary else 1.15,
                    alpha=1.0 if primary else 0.88,
                    label=LABELS[profile],
                )
                ax.fill_between(
                    q.k,
                    q.ci_low,
                    q.ci_high,
                    color=COLORS[profile],
                    alpha=0.075 if primary else 0.045,
                    linewidth=0,
                )
            ax.axvline(16, color="#888888", linestyle=(0, (2, 2)), linewidth=0.65, zorder=0)
            ax.set_title(f"{pretty_task(task)} / {arch}")
            ax.set_xticks([1, 2, 4, 8, 12, 16])
            ax.set_xlim(1, 16)
            ax.set_ylim(0, 1.025)
            if j == 0:
                ax.set_ylabel("Selected-channel fidelity")
            if i == 1:
                ax.set_xlabel(r"Patched channels, $k$")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=3,
        columnspacing=1.35,
        handlelength=2.3,
    )
    fig.tight_layout(rect=(0, 0.13, 1, 1), h_pad=0.8, w_pad=0.8)
    return save_pdf(fig, OUT / "fig02_patch_size.pdf")


def fig3_matching_trajectories() -> Path:
    data = pd.read_csv(ROOT / "analysis/kernel_similarity/results/per_checkpoint.csv")
    metrics = (
        ("nearest_cosine", "Nearest-template cosine"),
        ("assignment_cosine", "One-to-one cosine"),
        ("matching_gap", "Matching gap"),
    )

    fig, axes = plt.subplots(3, 4, figsize=(7.15, 5.15), sharex=True, sharey="row")
    for j, (task, arch) in enumerate(SETTINGS):
        subset = data[(data.task == task) & (data.architecture == arch)]
        for i, (metric, ylabel) in enumerate(metrics):
            ax = axes[i, j]
            for condition in STAGE_B_CONDITIONS:
                g = subset[subset.condition == condition].groupby("epoch")[metric].agg(["mean", "std"])
                primary = condition in ("template_retention_1", "template_release")
                ax.plot(
                    g.index,
                    g["mean"],
                    color=COLORS[condition],
                    linestyle=LINESTYLES[condition],
                    linewidth=1.75 if primary else 1.1,
                    alpha=1.0 if primary else 0.85,
                    label=LABELS[condition],
                )
                ax.fill_between(
                    g.index,
                    g["mean"] - g["std"],
                    g["mean"] + g["std"],
                    color=COLORS[condition],
                    alpha=0.07,
                    linewidth=0,
                )
            if j == 0:
                ax.set_ylabel(ylabel)
            if i == 0:
                ax.set_title(f"{pretty_task(task)}\n{arch}")
            if i == 2:
                ax.set_xlabel("Epoch")
            ax.set_xticks([0, 50, 100, 150, 200])

    axes[0, 0].set_ylim(0.0, 1.025)
    axes[1, 0].set_ylim(0.0, 1.025)
    gap_max = max(0.01, float(data.matching_gap.max()) * 1.15)
    axes[2, 0].set_ylim(0, gap_max)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=5,
        columnspacing=1.1,
        handlelength=2.2,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1), h_pad=0.75, w_pad=0.55)
    return save_pdf(fig, OUT / "fig03_matching_trajectories.pdf")


def fig4_similarity_matrices() -> Path:
    table = pd.read_csv(ROOT / "analysis/kernel_similarity/results/per_checkpoint.csv")
    bundle = np.load(ROOT / "analysis/kernel_similarity/results/similarity_matrices.npz")
    matrices = bundle["cosine"]
    if len(table) != len(matrices):
        raise ValueError("per_checkpoint.csv and similarity_matrices.npz are misaligned")

    task, arch, block = "two_concepts", "TinyCNN", 2000
    fig, axes = plt.subplots(2, 5, figsize=(7.15, 3.25), sharex=True, sharey=True)
    image = None
    for j, condition in enumerate(STAGE_B_CONDITIONS):
        for i, epoch in enumerate((0, 200)):
            match = table[
                (table.task == task)
                & (table.architecture == arch)
                & (table.block == block)
                & (table.condition == condition)
                & (table.epoch == epoch)
            ]
            if len(match) != 1:
                raise ValueError(f"Expected one matrix row for {condition}, epoch {epoch}")
            matrix = matrices[int(match.index[0])]
            rows, cols = linear_sum_assignment(-matrix)
            ax = axes[i, j]
            image = ax.imshow(
                matrix,
                vmin=-1,
                vmax=1,
                cmap="RdBu_r",
                interpolation="nearest",
                rasterized=True,
                aspect="equal",
            )
            ax.scatter(cols, rows, s=9, c="#111111", marker="x", linewidths=0.65)
            if i == 0:
                ax.set_title(LABELS[condition], pad=3)
            if j == 0:
                ax.set_ylabel(f"Epoch {epoch}\nChannel index")
            if i == 1:
                ax.set_xlabel("Template index")
            ax.set_xticks([0, 5, 10, 15])
            ax.set_yticks([0, 5, 10, 15])
            ax.grid(False)

    cbar = fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.022, pad=0.025)
    cbar.set_label("Signed cosine")
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    fig.subplots_adjust(left=0.075, right=0.91, top=0.90, bottom=0.14, wspace=0.16, hspace=0.18)
    return save_pdf(fig, OUT / "fig04_similarity_matrices.pdf")


def _load_checkpoint_weight(path: Path) -> np.ndarray:
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment-dependent guidance
        raise SystemExit(
            "Figure 5 requires PyTorch. Install the experiment extra with "
            "`python -m pip install -e \".[experiments]\"`."
        ) from exc
    saved = torch.load(path, map_location="cpu", weights_only=True)
    return saved["model"]["conv.weight"].detach().cpu().numpy()


def fig5_kernel_gallery() -> Path:
    bundle = np.load(ROOT / "analysis/kernel_similarity/results/similarity_matrices.npz")
    templates = bundle["templates"]
    task, arch, block = "two_concepts", "TinyCNN", 2000

    rows: list[tuple[str, np.ndarray]] = [("Original templates", templates)]
    for condition in STAGE_B_CONDITIONS:
        for epoch in (0, 200):
            checkpoint = (
                ROOT
                / "results/retention_release_001/runs"
                / task
                / arch
                / f"block{block:04d}"
                / condition
                / f"epoch_{epoch:04d}.pt"
            )
            weights = _load_checkpoint_weight(checkpoint)
            cols = assignment_columns(weights, templates)
            rows.append((f"{LABELS[condition]} · ep. {epoch}", weights[np.argsort(cols)]))

    images = [normalized(w).reshape(16, 9, 9) for _, w in rows]
    limit = max(float(np.abs(x).max()) for x in images)
    fig, axes = plt.subplots(len(rows), 16, figsize=(7.15, 4.65))
    for i, ((label, _), kernels) in enumerate(zip(rows, images)):
        for j, image in enumerate(kernels):
            ax = axes[i, j]
            ax.imshow(
                image,
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
                ax.set_title(f"T{j}", fontsize=6.2, pad=2)
        axes[i, 0].set_ylabel(label, rotation=0, ha="right", va="center", fontsize=6.6, labelpad=8)

    fig.subplots_adjust(left=0.175, right=0.997, top=0.96, bottom=0.01, wspace=0.025, hspace=0.075)
    return save_pdf(fig, OUT / "fig05_kernel_gallery.pdf")


def main() -> None:
    apply_paper_style()
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = [
        fig1_learning(),
        fig2_patch_size(),
        fig3_matching_trajectories(),
        fig4_similarity_matrices(),
        fig5_kernel_gallery(),
    ]
    plt.close("all")
    for path in outputs:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
