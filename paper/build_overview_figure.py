#!/usr/bin/env python3
"""Build the manuscript overview figure from the frozen renderer and template definitions.

This figure is presentation-only. It reproduces the same procedural renderer
and 16-filter template-bank formulas used by the experiments and does not read
or alter any experimental outcome.
"""
from __future__ import annotations
from plot_style import apply_paper_style, save_pdf
from PIL import Image, ImageDraw
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

import matplotlib
matplotlib.use("Agg")


PAPER = Path(__file__).resolve().parent
OUT = PAPER / "figures" / "fig00_overview.pdf"
MASTER = 2026090617
TASKS = ("single_shape", "two_concepts")


def seed(*keys: int) -> int:
    return int(np.random.SeedSequence([MASTER, *map(int, keys)]).generate_state(1)[0])


def rng(*keys: int):
    return np.random.default_rng(np.random.SeedSequence([MASTER, *map(int, keys)]))


def normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    x = x - x.mean(axis=(-2, -1), keepdims=True)
    return x / np.sqrt((x * x).sum(axis=(-2, -1), keepdims=True))


def template_bank() -> np.ndarray:
    ax = np.arange(-4, 5)
    x, y = np.meshgrid(ax, ax)
    g = np.exp(-(x * x + y * y) / 8)
    out = []
    for i in range(8):
        a = i * np.pi / 8
        out.append((x * np.cos(a) + y * np.sin(a)) * g)
    for i in range(4):
        a = i * np.pi / 2
        u = x * np.cos(a) + y * np.sin(a)
        v = -x * np.sin(a) + y * np.cos(a)
        d1 = v * v + np.minimum(u, 0) ** 2
        d2 = u * u + np.minimum(v, 0) ** 2
        out.append(np.exp(-np.minimum(d1, d2) / (2 * 0.65**2)) * g)
    rad = np.sqrt(x * x + y * y)
    for radius in (1.5, 2.0, 2.5, 3.0):
        out.append(
            np.exp(-(rad - radius) ** 2 / 2)
            - np.exp(-(rad - radius - 1) ** 2 / 2)
        )
    return normalize(np.stack(out)).astype(np.float32)


def render_object(shape: str, cx: float, cy: float, radius: float, theta: float, width: float, aa: int = 3):
    im = Image.new("L", (32 * aa, 32 * aa), 0)
    draw = ImageDraw.Draw(im)
    cx *= aa
    cy *= aa
    radius *= aa
    line_width = max(1, round(width * aa))
    if shape == "line":
        dx = radius * np.cos(theta)
        dy = radius * np.sin(theta)
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)],
                  fill=255, width=line_width)
    elif shape == "circle":
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=255,
            width=line_width,
        )
    else:
        n = 3 if shape == "triangle" else 4
        pts = [
            (
                cx + radius * np.cos(theta + j * 2 * np.pi / n),
                cy + radius * np.sin(theta + j * 2 * np.pi / n),
            )
            for j in range(n)
        ]
        draw.line(pts + [pts[0]], fill=255, width=line_width, joint="curve")
    return np.asarray(
        im.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32
    ) / 255


def representative_states(task: str, block: int = 4000, split: int = 2) -> np.ndarray:
    """Generate the first deterministic test context for a frozen renderer block."""
    task_index = TASKS.index(task)
    stream = rng(10, block, task_index, split)
    theta = float(stream.uniform(0, np.pi / 4))
    width = float(stream.uniform(0.8, 1.6))
    scale = float(stream.uniform(0.85, 1.15))
    tx, ty = stream.uniform(-2, 2, 2)
    noise_sd = float(stream.uniform(0, 0.05))
    noise = stream.normal(0, noise_sd, (32, 32)).astype(np.float32)
    occluded = bool(stream.random() < 0.1)
    ox, oy = stream.integers(0, 27, 2)
    swapped = bool(stream.integers(2))

    states = []
    for state in range(4):
        if task == "single_shape":
            shape = ("line", "circle", "triangle", "square")[state]
            image = render_object(shape, 16 + tx, 16 + ty,
                                  10 * scale, theta, width)
        else:
            locations = [(8 + tx / 2, 15 + ty), (24 + tx / 2, 17 + ty)]
            if swapped:
                locations = locations[::-1]
            a = render_object(
                "circle" if state & 1 else "square",
                *locations[0],
                4.5 * scale,
                theta,
                width,
            )
            b = render_object(
                "triangle" if state & 2 else "line",
                *locations[1],
                4.5 * scale,
                theta,
                width,
            )
            image = np.maximum(a, b)
        if occluded:
            image[oy: oy + 5, ox: ox + 5] = 0
        states.append(np.clip(image + noise, 0, 1))
    return np.stack(states)


def build_figure() -> Path:
    apply_paper_style()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    single = representative_states("single_shape")
    two = representative_states("two_concepts")
    templates = template_bank()

    fig = plt.figure(figsize=(7.15, 3.95))
    # Panel (c) is an explanatory flow rather than a small data panel.  It gets
    # a majority of the width so the retained and copied channels remain
    # readable at the manuscript's final scale.
    grid = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.05, 1.95], wspace=0.22)

    ax_data = fig.add_subplot(grid[0, 0])
    ax_data.axis("off")
    ax_data.text(0.00, 1.02, "a", transform=ax_data.transAxes,
                 fontweight="bold")
    ax_data.text(0.08, 1.02, "Rendered inputs", transform=ax_data.transAxes)

    rows = (
        (single, ("line", "circle", "triangle", "square"), "single_shape"),
        (two, ("00", "01", "10", "11"), "two_concepts"),
    )
    for row, (images, labels, title) in enumerate(rows):
        ax_data.text(0.02, 0.88 - row * 0.47, title,
                     transform=ax_data.transAxes, fontsize=7.2)
        for j, image in enumerate(images):
            inset = ax_data.inset_axes(
                [0.02 + j * 0.245, 0.54 - row * 0.47, 0.21, 0.28])
            inset.imshow(image, cmap="gray", vmin=0,
                         vmax=1, interpolation="nearest")
            inset.set_xticks([])
            inset.set_yticks([])
            inset.set_title(labels[j], fontsize=6.0, pad=1.0)
            for spine in inset.spines.values():
                spine.set_linewidth(0.45)

    ax_bank = fig.add_subplot(grid[0, 1])
    ax_bank.axis("off")
    ax_bank.text(0.00, 1.02, "b", transform=ax_bank.transAxes,
                 fontweight="bold")
    ax_bank.text(0.08, 1.02, "Template bank", transform=ax_bank.transAxes)
    limit = float(np.max(np.abs(templates)))
    for i, kernel in enumerate(templates):
        row, col = divmod(i, 4)
        inset = ax_bank.inset_axes(
            [0.02 + col * 0.245, 0.74 - row * 0.235, 0.21, 0.20])
        inset.imshow(kernel, cmap="RdBu_r", vmin=-limit,
                     vmax=limit, interpolation="nearest")
        inset.set_xticks([])
        inset.set_yticks([])
        family = "edge" if i < 8 else "corner" if i < 12 else "ring"
        index = i if i < 8 else i - 8 if i < 12 else i - 12
        inset.set_title(f"{family} {index}", fontsize=5.6, pad=0.8)

    ax_patch = fig.add_subplot(grid[0, 2])
    ax_patch.set_xlim(0, 1)
    ax_patch.set_ylim(0, 1)
    ax_patch.axis("off")
    ax_patch.text(0.00, 1.02, "c", transform=ax_patch.transAxes,
                  fontweight="bold")
    ax_patch.text(
        0.08, 1.02, "First-layer patching",
        transform=ax_patch.transAxes, fontstretch="normal"
    )

    # Two explicit lanes feed a hybrid activation. Gray denotes channels kept
    # from the base state; blue denotes selected channels copied from the
    # matched counterfactual.
    retained_color = "#6B7280"
    copied_color = "#0072B2"
    lane_y = {"base": 0.69, "counterfactual": 0.27}
    lane_images = {"base": two[0], "counterfactual": two[1]}
    for name in ("base", "counterfactual"):
        y = lane_y[name]
        inset = ax_patch.inset_axes([0.00, y, 0.120, 0.150])
        inset.imshow(lane_images[name], cmap="gray",
                     vmin=0, vmax=1, interpolation="nearest")
        inset.axis("off")
        ax_patch.text(0.060, y - 0.018, name,
                      ha="center", va="top", fontsize=6.0)

        conv = FancyBboxPatch(
            (0.190, y + 0.045), 0.160, 0.065,
            boxstyle="round,pad=0.012",
            facecolor="0.96", edgecolor="0.35", linewidth=0.7,
        )
        ax_patch.add_patch(conv)
        ax_patch.text(
            0.270, y + 0.0775, "conv1 + ReLU\n16 feature maps",
            ha="center", va="center", fontsize=4.3,
        )
        ax_patch.add_patch(
            FancyArrowPatch(
                (0.125, y + 0.075), (0.185, y + 0.075),
                arrowstyle="-|>", mutation_scale=8, linewidth=0.75, color="0.3",
            )
        )

    def draw_state_stack(
        x: float,
        y: float,
        label: str,
        *,
        copied_channels: bool = False,
    ) -> None:
        for depth in range(4):
            ax_patch.add_patch(
                Rectangle(
                    (x + depth * 0.011, y + depth * 0.008),
                    0.080, 0.085,
                    facecolor=copied_color if copied_channels and depth < 2 else "0.95",
                    edgecolor="0.42", linewidth=0.5,
                )
            )
        ax_patch.text(x + 0.053, y - 0.018, label,
                      ha="center", va="top", fontsize=6.6)

    draw_state_stack(0.420, 0.735, r"$H_0$")
    draw_state_stack(0.420, 0.315, r"$H_1$", copied_channels=True)
    for y in (0.7775, 0.3575):
        ax_patch.add_patch(
            FancyArrowPatch(
                (0.355, y), (0.415, y),
                arrowstyle="-|>", mutation_scale=7, linewidth=0.7, color="0.3",
            )
        )

    # Each arrow states its contribution to the hybrid state. Matching colors
    # make the copied layers in H_1 and H_S unambiguous.
    draw_state_stack(0.61, 0.53, r"$H_S$", copied_channels=True)
    ax_patch.add_patch(
        FancyArrowPatch(
            (0.535, 0.7775), (0.6, 0.58),
            arrowstyle="-|>", mutation_scale=8, linewidth=0.85, color=retained_color,
        )
    )
    ax_patch.add_patch(
        FancyArrowPatch(
            (0.535, 0.3575), (0.6, 0.58),
            arrowstyle="-|>", mutation_scale=8, linewidth=1.05, color=copied_color,
        )
    )
    ax_patch.text(
        0.580, 0.775, "retain $16-k$\nchannels from $H_0$",
        ha="left", va="center", fontsize=5.6,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
    )
    ax_patch.text(
        0.580, 0.380, "copy $k$ selected\nchannels from $H_1$",
        ha="left", va="center", fontsize=5.6, color=copied_color,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
    )

    downstream = FancyBboxPatch(
        (0.81, 0.55), 0.16, 0.077, boxstyle="round,pad=0.01",
        facecolor="0.96", edgecolor="0.35", linewidth=0.7,
    )
    ax_patch.add_patch(downstream)
    ax_patch.text(
        0.89, 0.59, "downstream\nnetwork",
        ha="center", va="center", fontsize=4.6,
    )
    ax_patch.add_patch(
        FancyArrowPatch(
            (0.73, 0.58), (0.8, 0.58),
            arrowstyle="-|>", mutation_scale=7, linewidth=0.7, color="0.3",
        )
    )
    ax_patch.text(
        0.8, 0.20, "Downstream parameters\nremain unchanged.",
        ha="center", va="center", fontsize=5.7,
    )

    fig.subplots_adjust(left=0.025, right=0.995, top=0.91, bottom=0.05)
    path = save_pdf(fig, OUT)
    plt.close(fig)
    return path


def main() -> None:
    path = build_figure()
    print(path.relative_to(PAPER.parent))


if __name__ == "__main__":
    main()
