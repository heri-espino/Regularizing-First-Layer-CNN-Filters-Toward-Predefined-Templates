"""Frozen Stage-G anchor families, seeds, and architecture subset."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
STAGE_F = ROOT / "studies" / "cnn_architecture_robustness"
sys.path.append(str(STAGE_F))
import architecture_core as stage_f_core  # noqa: E402

legacy_core = stage_f_core.legacy_core
ArchitectureNet = stage_f_core.ArchitectureNet
MASTER = legacy_core.MASTER
TASKS = tuple(legacy_core.TASKS)
ARCHS = ("tiny_gmp", "tiny_gap", "plain2_w16_gmp", "plain2_w16_gap")
TREATMENTS = ("retention_1", "release_default")
RANK_TOL = 1e-6

ANCHORS = (
    "structured_template",
    "pixel_permuted_template",
    "random_rank10",
    "random_fullrank",
)


def _seed(namespace: int, block: int, init_rep: int, task: str | None = None, arch: str | None = None) -> int:
    values = [MASTER, int(namespace), int(block), int(init_rep)]
    if task is not None:
        values.append(TASKS.index(task))
    if arch is not None:
        values.append(ARCHS.index(arch))
    return int(np.random.SeedSequence(values).generate_state(1)[0])


def model_seed(block: int, task: str, arch: str, init_rep: int) -> int:
    # Anchor family intentionally omitted so downstream initialization is paired.
    return _seed(70, block, init_rep, task=task, arch=arch)


def shuffle_seed(block: int, task: str, arch: str, init_rep: int) -> int:
    # Treatment and anchor family intentionally omitted.
    return _seed(71, block, init_rep, task=task, arch=arch)


def control_seed(block: int, task: str, arch: str, init_rep: int) -> int:
    # Shared random channel orders across anchor families for paired diagnostics.
    return _seed(72, block, init_rep, task=task, arch=arch)


def anchor_seed(block: int, init_rep: int, anchor_family: str) -> int:
    if anchor_family not in ANCHORS:
        raise ValueError(anchor_family)
    # Shared across task/architecture/treatment; family gets a deterministic namespace.
    return _seed(80 + ANCHORS.index(anchor_family), block, init_rep)


def _center_normalize_rows(bank: np.ndarray) -> np.ndarray:
    x = np.asarray(bank, dtype=np.float64).reshape(16, 81)
    x = x - x.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    if np.any(norm < 1e-12):
        raise ValueError("Degenerate anchor row")
    x = x / norm
    return x.reshape(16, 9, 9).astype(np.float32)


def structured_bank() -> np.ndarray:
    return np.asarray(legacy_core.bank(), dtype=np.float32).copy()


def pixel_permuted_bank(block: int, init_rep: int) -> np.ndarray:
    base = structured_bank().reshape(16, 81)
    rng = np.random.default_rng(anchor_seed(block, init_rep, "pixel_permuted_template"))
    permutation = rng.permutation(81)
    return base[:, permutation].reshape(16, 9, 9).astype(np.float32)


def random_rank10_bank(block: int, init_rep: int) -> np.ndarray:
    rng = np.random.default_rng(anchor_seed(block, init_rep, "random_rank10"))
    # Build an orthonormal random basis in the 80-D zero-mean pixel subspace.
    basis_raw = rng.standard_normal((81, 10))
    basis_raw -= basis_raw.mean(axis=0, keepdims=True)
    q, _ = np.linalg.qr(basis_raw)
    basis = q[:, :10]
    coeff = rng.standard_normal((16, 10))
    bank = coeff @ basis.T
    out = _center_normalize_rows(bank.reshape(16, 9, 9))
    rank = np.linalg.matrix_rank(out.reshape(16, 81), tol=RANK_TOL)
    if rank != 10:
        raise AssertionError(f"Expected random rank-10 bank, got rank={rank}")
    return out


def random_fullrank_bank(block: int, init_rep: int) -> np.ndarray:
    rng = np.random.default_rng(anchor_seed(block, init_rep, "random_fullrank"))
    out = _center_normalize_rows(rng.standard_normal((16, 9, 9)))
    rank = np.linalg.matrix_rank(out.reshape(16, 81), tol=RANK_TOL)
    if rank != 16:
        raise AssertionError(f"Expected full-rank random bank, got rank={rank}")
    return out


def anchor_bank(anchor_family: str, block: int, init_rep: int) -> np.ndarray:
    if anchor_family == "structured_template":
        return structured_bank()
    if anchor_family == "pixel_permuted_template":
        return pixel_permuted_bank(block, init_rep)
    if anchor_family == "random_rank10":
        return random_rank10_bank(block, init_rep)
    if anchor_family == "random_fullrank":
        return random_fullrank_bank(block, init_rep)
    raise ValueError(anchor_family)


def bank_diagnostics(bank: np.ndarray) -> dict:
    matrix = np.asarray(bank, dtype=np.float64).reshape(16, 81)
    centered = matrix - matrix.mean(axis=1, keepdims=True)
    singular = np.linalg.svd(centered, compute_uv=False)
    gram = centered @ centered.T
    return {
        "rank": int(np.linalg.matrix_rank(centered, tol=RANK_TOL)),
        "max_abs_row_mean": float(np.abs(matrix.mean(axis=1)).max()),
        "max_abs_row_norm_error": float(np.abs(np.linalg.norm(matrix, axis=1) - 1.0).max()),
        "singular_values": [float(x) for x in singular],
        "gram_sha256": hashlib.sha256(np.ascontiguousarray(gram).tobytes()).hexdigest(),
        "bank_sha256": hashlib.sha256(np.ascontiguousarray(matrix).tobytes()).hexdigest(),
    }


def verify_anchor(anchor_family: str, block: int, init_rep: int, atol: float = 2e-6) -> dict:
    bank = anchor_bank(anchor_family, block, init_rep)
    diag = bank_diagnostics(bank)
    if diag["max_abs_row_mean"] > atol:
        raise AssertionError((anchor_family, "row mean", diag["max_abs_row_mean"]))
    if diag["max_abs_row_norm_error"] > atol:
        raise AssertionError((anchor_family, "row norm", diag["max_abs_row_norm_error"]))

    if anchor_family in ("structured_template", "pixel_permuted_template", "random_rank10"):
        expected_rank = 10
    else:
        expected_rank = 16
    if diag["rank"] != expected_rank:
        raise AssertionError((anchor_family, "rank", diag["rank"], expected_rank))

    if anchor_family == "pixel_permuted_template":
        base = structured_bank().reshape(16, 81).astype(np.float64)
        candidate = bank.reshape(16, 81).astype(np.float64)
        gram_error = float(np.abs(base @ base.T - candidate @ candidate.T).max())
        if gram_error > 5e-6:
            raise AssertionError(("pixel_permuted_template", "gram", gram_error))
        diag["max_abs_gram_error_vs_structured"] = gram_error
    return diag


def setup_model(arch: str, anchor_family: str, block: int, task: str, init_rep: int):
    if arch not in ARCHS:
        raise ValueError(arch)
    torch.manual_seed(model_seed(block, task, arch, init_rep))
    model = ArchitectureNet(arch)
    bank = anchor_bank(anchor_family, block, init_rep)
    anchor = torch.from_numpy(bank[:, None].copy())
    with torch.no_grad():
        model.conv.weight.copy_(anchor)
    return model, anchor


def retention_strength(treatment: str, epoch: int) -> float:
    if treatment == "retention_1":
        return 1.0
    if treatment == "release_default":
        return float(np.clip((80 - epoch) / 70.0, 0.0, 1.0))
    raise ValueError(treatment)


def alignment_to(weights: np.ndarray, bank: np.ndarray) -> float:
    return float(legacy_core.alignment(weights, bank))


def architecture_manifest() -> dict:
    return {name: stage_f_core.architecture_manifest()[name] for name in ARCHS}


def anchor_manifest(block: int = 7000, init_rep: int = 0) -> dict:
    return {
        family: verify_anchor(family, block, init_rep)
        for family in ANCHORS
    }
