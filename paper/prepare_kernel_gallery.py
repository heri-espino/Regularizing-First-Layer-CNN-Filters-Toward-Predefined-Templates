#!/usr/bin/env python3
"""Export the frozen representative kernel gallery to a small, torch-free NPZ.

The selected example is the historical two_concepts/TinyCNN/block2000
at epochs 0 and 200 for the five Stage-B conditions. No training occurs.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import hashlib
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/kernel_similarity/results/similarity_matrices.npz"
OUTPUT = ROOT / "analysis/kernel_similarity/results/kernel_gallery.npz"
TASK = "two_concepts"
ARCHITECTURE = "TinyCNN"
BLOCK = 2000
CONDITIONS = (
    "random", "random_unitnorm", "template_init",
    "template_retention_1", "template_release",
)
EPOCHS = (0, 200)


def _checkpoint(condition: str, epoch: int) -> Path:
    return (
        ROOT / "results/retention_release_001/runs" / TASK / ARCHITECTURE
        / f"block{BLOCK:04d}" / condition / f"epoch_{epoch:04d}.pt"
    )


def build(output: Path = OUTPUT, *, overwrite: bool = False) -> Path:
    if output.is_file() and not overwrite:
        # Validate an existing compact export without importing torch.
        with np.load(output, allow_pickle=False) as bundle:
            for key in ("templates", "kernels", "conditions", "epochs", "task", "architecture", "block", "provenance_json"):
                if key not in bundle:
                    raise ValueError(f"Existing gallery NPZ missing {key}: {output}")
            if bundle["kernels"].shape != (5, 2, 16, 9, 9):
                raise ValueError(f"Unexpected saved gallery shape: {bundle['kernels'].shape}")
        return output

    missing = [p for condition in CONDITIONS for epoch in EPOCHS
               if not (p := _checkpoint(condition, epoch)).is_file()]
    if missing:
        raise FileNotFoundError(
            "Cannot export gallery: required saved checkpoints are missing:\n"
            + "\n".join(str(p.relative_to(ROOT)) for p in missing)
        )
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Missing original template source: {SOURCE}")
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "The one-time gallery export requires PyTorch to read checkpoints. "
            "Install the experiments extra, then run this script. "
            "Regenerating the figures from the exported NPZ does not require PyTorch."
        ) from exc

    with np.load(SOURCE, allow_pickle=False) as source:
        templates = np.asarray(source["templates"], dtype=np.float32)
    if templates.shape != (16, 9, 9):
        raise ValueError(f"Unexpected original template shape {templates.shape}")
    kernels = np.empty((len(CONDITIONS), len(EPOCHS), 16, 9, 9), dtype=np.float32)
    originals = []
    for i, condition in enumerate(CONDITIONS):
        for j, epoch in enumerate(EPOCHS):
            checkpoint = _checkpoint(condition, epoch)
            saved = torch.load(checkpoint, map_location="cpu", weights_only=True)
            weights = saved["model"]["conv.weight"].detach().cpu().numpy()
            if weights.shape != (16, 1, 9, 9):
                raise ValueError(f"Unexpected conv.weight shape in {checkpoint}: {weights.shape}")
            kernels[i, j] = weights[:, 0]
            originals.append({
                "task": TASK,
                "architecture": ARCHITECTURE,
                "block": BLOCK,
                "condition": condition,
                "epoch": epoch,
                "source_path": checkpoint.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            })
    metadata = {
        "task": TASK, "architecture": ARCHITECTURE, "block": BLOCK,
        "source_templates": SOURCE.relative_to(ROOT).as_posix(),
        "templates_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "matching": "centered unit-L2-normalized signed cosine; maximum-similarity Hungarian one-to-one assignment",
        "gallery_order": "ascending assigned template column",
        "normalization": "all displayed kernels individually mean-centered and unit-L2-normalized; shared symmetric color limit",
        "checkpoints": originals,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        templates=templates,
        kernels=kernels,
        conditions=np.asarray(CONDITIONS),
        epochs=np.asarray(EPOCHS, dtype=np.int64),
        task=np.asarray(TASK),
        architecture=np.asarray(ARCHITECTURE),
        block=np.asarray(BLOCK),
        provenance_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )
    with np.load(output, allow_pickle=False) as check:
        assert np.array_equal(check["kernels"], kernels)
    print(f"Exported torch-independent gallery: {output.relative_to(ROOT)}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="Regenerate from original checkpoints.")
    args = parser.parse_args()
    build(overwrite=args.overwrite)


if __name__ == "__main__":
    main()
