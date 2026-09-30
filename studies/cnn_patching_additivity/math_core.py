"""Pure algebra for the post-hoc first-layer patching additivity study."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

DEN_EPS = 1e-12


def center_logits(x: torch.Tensor) -> torch.Tensor:
    return x - x.mean(dim=-1, keepdim=True)


def _sqnorm(x: torch.Tensor) -> torch.Tensor:
    return x.square().sum(dim=-1)


def _softmax64(x: torch.Tensor) -> torch.Tensor:
    return torch.softmax(x.to(torch.float64), dim=-1)


def _fidelity(error: torch.Tensor, base_error: torch.Tensor, eps: float = DEN_EPS) -> float | None:
    den = float(base_error.sum())
    if den < eps:
        return None
    return float(1.0 - float(error.sum()) / den)


def _error_reduction(error: torch.Tensor, base_error: torch.Tensor) -> float:
    return float((base_error - error).mean())


def metrics_from_logits(
    logits_s: torch.Tensor,
    logits_0: torch.Tensor,
    logits_1: torch.Tensor,
    eps: float = DEN_EPS,
) -> dict[str, float | None]:
    """Metrics used in the source studies, accumulated across pairs before ratios."""
    s = logits_s.to(torch.float64)
    l0 = logits_0.to(torch.float64)
    l1 = logits_1.to(torch.float64)
    cs, c0, c1 = center_logits(s), center_logits(l0), center_logits(l1)
    ps, p0, p1 = _softmax64(s), _softmax64(l0), _softmax64(l1)

    prob_base = _sqnorm(p0 - p1)
    prob_err = _sqnorm(ps - p1)
    centered_base = _sqnorm(c0 - c1)
    centered_err = _sqnorm(cs - c1)
    raw_base = _sqnorm(l0 - l1)
    raw_err = _sqnorm(s - l1)
    return {
        "prob_fidelity": _fidelity(prob_err, prob_base, eps),
        "centered_logit_fidelity": _fidelity(centered_err, centered_base, eps),
        "raw_logit_fidelity": _fidelity(raw_err, raw_base, eps),
        "prob_error_reduction": _error_reduction(prob_err, prob_base),
        "centered_logit_error_reduction": _error_reduction(centered_err, centered_base),
        "raw_logit_error_reduction": _error_reduction(raw_err, raw_base),
        "prob_patch_error_mpp": float(prob_err.mean()),
        "centered_logit_patch_error_mpp": float(centered_err.mean()),
        "raw_logit_patch_error_mpp": float(raw_err.mean()),
        "prob_input_effect_mpp": float(prob_base.mean()),
        "centered_logit_input_effect_mpp": float(centered_base.mean()),
        "raw_logit_input_effect_mpp": float(raw_base.mean()),
    }


def gather_changes(singleton_changes: torch.Tensor, channels: torch.Tensor) -> torch.Tensor:
    """Sum singleton changes for per-pair channel sets.

    singleton_changes: [N, J, C]
    channels: [N, K] integer indices; K may be zero.
    """
    if singleton_changes.ndim != 3:
        raise ValueError(f"singleton_changes must be [N,J,C], got {tuple(singleton_changes.shape)}")
    n, _, c = singleton_changes.shape
    if channels.ndim != 2 or channels.shape[0] != n:
        raise ValueError(f"channels must be [N,K], got {tuple(channels.shape)} for N={n}")
    if channels.shape[1] == 0:
        return torch.zeros((n, c), dtype=singleton_changes.dtype, device=singleton_changes.device)
    ix = channels[..., None].expand(-1, -1, c)
    return singleton_changes.gather(1, ix).sum(dim=1)


def selected_singleton_terms(
    v: torch.Tensor,
    singleton_changes: torch.Tensor,
    channels: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return individual sum, cross term and additive gain per pair.

    G_add = individual_sum + cross_term where
    cross_term = -2 sum_{i<j} d_i^T d_j.
    """
    n, _, c = singleton_changes.shape
    if channels.shape[1] == 0:
        z = torch.zeros(n, dtype=torch.float64, device=singleton_changes.device)
        return z, z, z
    ix = channels[..., None].expand(-1, -1, c)
    ds = singleton_changes.gather(1, ix).to(torch.float64)
    vv = v.to(torch.float64)[:, None, :]
    individual = (2.0 * (vv * ds).sum(-1) - ds.square().sum(-1)).sum(-1)
    a = ds.sum(1)
    g_add = 2.0 * (v.to(torch.float64) * a).sum(-1) - a.square().sum(-1)
    cross = g_add - individual
    return individual, cross, g_add


@dataclass(frozen=True)
class Decomposition:
    summary: dict[str, Any]
    pair_arrays: dict[str, np.ndarray]


def decompose_set(
    logits_0: torch.Tensor,
    logits_1: torch.Tensor,
    singleton_logits: torch.Tensor,
    joint_logits: torch.Tensor,
    channels: torch.Tensor,
    eps: float = DEN_EPS,
    keep_pair_arrays: bool = False,
) -> Decomposition:
    """Decompose one intervention set family/budget across matched pairs.

    All identities are evaluated in float64. The primary decomposition uses
    centered logits; a raw-logit decomposition is also returned for common-mode
    diagnostics.
    """
    l0 = logits_0.to(torch.float64)
    l1 = logits_1.to(torch.float64)
    sj = singleton_logits.to(torch.float64)
    ls = joint_logits.to(torch.float64)

    if sj.ndim != 3 or sj.shape[0] != l0.shape[0] or sj.shape[2] != l0.shape[1]:
        raise ValueError("singleton_logits must be [pairs, channels, classes]")

    c0, c1 = center_logits(l0), center_logits(l1)
    csj, cs = center_logits(sj), center_logits(ls)
    v = c1 - c0
    d = csj - c0[:, None, :]
    a = gather_changes(d, channels)
    zhat = c0 + a
    r = cs - zhat

    v_raw = l1 - l0
    d_raw = sj - l0[:, None, :]
    a_raw = gather_changes(d_raw, channels)
    lhat = l0 + a_raw
    r_raw = ls - lhat

    g_obs = _sqnorm(v) - _sqnorm(v - a - r)
    g_add_direct = _sqnorm(v) - _sqnorm(v - a)
    individual, cross, g_add_identity = selected_singleton_terms(v, d, channels)
    nonadd = 2.0 * ((v - a) * r).sum(-1) - _sqnorm(r)

    id_add_1 = (g_add_direct - (2.0 * (v * a).sum(-1) - _sqnorm(a))).abs()
    id_add_2 = (g_add_direct - g_add_identity).abs()
    id_obs = ((g_obs - g_add_direct) - nonadd).abs()

    selected_norm_sum = torch.zeros(len(v), dtype=torch.float64, device=v.device)
    if channels.shape[1]:
        ix = channels[..., None].expand(-1, -1, d.shape[-1])
        selected_d = d.gather(1, ix)
        selected_norm_sum = torch.linalg.vector_norm(selected_d, dim=-1).sum(-1)
    a_norm = torch.linalg.vector_norm(a, dim=-1)
    cancellation = torch.full_like(a_norm, torch.nan)
    defined_k = selected_norm_sum > eps
    cancellation[defined_k] = 1.0 - a_norm[defined_k] / selected_norm_sum[defined_k]

    v_norm = torch.linalg.vector_norm(v, dim=-1)
    d_norm = torch.linalg.vector_norm(d, dim=-1)
    q = torch.full((d.shape[0], d.shape[1]), torch.nan, dtype=torch.float64, device=d.device)
    defined_v = v_norm > eps
    q[defined_v] = (d[defined_v] * v[defined_v, None, :]).sum(-1) / v_norm[defined_v, None]
    ortho_sq = torch.clamp(d_norm.square() - torch.nan_to_num(q, nan=0.0).square(), min=0.0)
    orthogonal_norm = torch.sqrt(ortho_sq)
    orthogonal_norm[~defined_v] = torch.nan

    obs_metrics = metrics_from_logits(ls, l0, l1, eps)
    # Centered reconstructed logits are sufficient for both centered-logit and
    # probability metrics because softmax is invariant to a common logit shift.
    add_centered_metrics = metrics_from_logits(zhat, c0, c1, eps)
    add_raw_metrics = metrics_from_logits(lhat, l0, l1, eps)
    add_metrics = dict(add_raw_metrics)
    add_metrics["centered_logit_fidelity"] = add_centered_metrics["centered_logit_fidelity"]
    add_metrics["centered_logit_error_reduction"] = add_centered_metrics["centered_logit_error_reduction"]
    add_metrics["centered_logit_patch_error_mpp"] = add_centered_metrics["centered_logit_patch_error_mpp"]
    add_metrics["centered_logit_input_effect_mpp"] = add_centered_metrics["centered_logit_input_effect_mpp"]

    v_energy = float(_sqnorm(v).sum())
    r_energy = float(_sqnorm(r).sum())
    raw_r_energy = float(_sqnorm(r_raw).sum())
    common_mode = r_raw.mean(-1)

    summary: dict[str, Any] = {
        **{f"observed_{k}": val for k, val in obs_metrics.items()},
        **{f"additive_{k}": val for k, val in add_metrics.items()},
        "pairs": int(len(v)),
        "centered_v_energy_sum": v_energy,
        "centered_residual_energy_sum": r_energy,
        "centered_residual_energy_ratio": None if v_energy < eps else r_energy / v_energy,
        "centered_residual_norm_mpp": float(torch.sqrt(_sqnorm(r)).mean()),
        "raw_residual_energy_sum": raw_r_energy,
        "raw_residual_norm_mpp": float(torch.sqrt(_sqnorm(r_raw)).mean()),
        "raw_residual_common_mode_rms": float(torch.sqrt((common_mode.square()).mean())),
        "g_obs_mpp": float(g_obs.mean()),
        "g_add_mpp": float(g_add_direct.mean()),
        "g_individual_sum_mpp": float(individual.mean()),
        "g_cross_term_mpp": float(cross.mean()),
        "g_nonadditive_correction_mpp": float(nonadd.mean()),
        "cancellation_mean": None if not bool(defined_k.any()) else float(cancellation[defined_k].mean()),
        "cancellation_undefined_pairs": int((~defined_k).sum()),
        "q_undefined_pairs": int((~defined_v).sum()),
        "identity_additive_direct_max_abs_error": float(id_add_1.max()) if len(id_add_1) else 0.0,
        "identity_additive_expanded_max_abs_error": float(id_add_2.max()) if len(id_add_2) else 0.0,
        "identity_nonadditive_correction_max_abs_error": float(id_obs.max()) if len(id_obs) else 0.0,
        "residual_max_abs_component": float(r.abs().max()) if r.numel() else 0.0,
        "raw_residual_max_abs_component": float(r_raw.abs().max()) if r_raw.numel() else 0.0,
        "selected_singleton_norm_sum_mpp": float(selected_norm_sum.mean()),
        "additive_change_norm_mpp": float(a_norm.mean()),
        "singleton_norm_mpp": float(d_norm.mean()),
        "singleton_parallel_mpp": None if not bool(defined_v.any()) else float(q[defined_v].mean()),
        "singleton_orthogonal_norm_mpp": None if not bool(defined_v.any()) else float(orthogonal_norm[defined_v].mean()),
    }

    arrays: dict[str, np.ndarray] = {}
    if keep_pair_arrays:
        def cpu32(x: torch.Tensor) -> np.ndarray:
            return x.detach().cpu().to(torch.float32).numpy()
        arrays = {
            "v_norm": cpu32(v_norm),
            "singleton_norm": cpu32(d_norm),
            "singleton_parallel": cpu32(q),
            "singleton_orthogonal_norm": cpu32(orthogonal_norm),
            "additive_change_norm": cpu32(a_norm),
            "selected_singleton_norm_sum": cpu32(selected_norm_sum),
            "cancellation": cpu32(cancellation),
            "residual_norm": cpu32(torch.linalg.vector_norm(r, dim=-1)),
            "raw_residual_norm": cpu32(torch.linalg.vector_norm(r_raw, dim=-1)),
            "raw_residual_common_mode": cpu32(common_mode),
            "g_obs": cpu32(g_obs),
            "g_add": cpu32(g_add_direct),
            "g_individual_sum": cpu32(individual),
            "g_cross_term": cpu32(cross),
            "g_nonadditive_correction": cpu32(nonadd),
        }
    return Decomposition(summary=summary, pair_arrays=arrays)


def singleton_geometry(
    logits_0: torch.Tensor,
    logits_1: torch.Tensor,
    singleton_logits: torch.Tensor,
    eps: float = DEN_EPS,
) -> dict[str, Any]:
    """Aggregate singleton direction/magnitude diagnostics after per-pair computation."""
    l0 = logits_0.to(torch.float64)
    l1 = logits_1.to(torch.float64)
    sj = singleton_logits.to(torch.float64)
    c0, c1, csj = center_logits(l0), center_logits(l1), center_logits(sj)
    v = c1 - c0
    d = csj - c0[:, None, :]
    vn = torch.linalg.vector_norm(v, dim=-1)
    dn = torch.linalg.vector_norm(d, dim=-1)
    defined = vn > eps
    q = torch.full_like(dn, torch.nan)
    q[defined] = (d[defined] * v[defined, None, :]).sum(-1) / vn[defined, None]
    ortho = torch.full_like(dn, torch.nan)
    ortho[defined] = torch.sqrt(torch.clamp(dn[defined].square() - q[defined].square(), min=0.0))
    common = (sj - l0[:, None, :]).mean(-1)
    # Pairwise singleton geometry is computed within each counterfactual pair
    # before aggregation. Entry (i,j) is E_n[d_{n,i}^T d_{n,j}], so it cannot
    # conflate channel cancellation with cancellation across examples.
    cross_dot = torch.einsum("njc,nkc->njk", d, d)

    def means(x: torch.Tensor) -> list[float | None]:
        out: list[float | None] = []
        for j in range(x.shape[1]):
            vals = x[:, j]
            ok = torch.isfinite(vals)
            out.append(None if not bool(ok.any()) else float(vals[ok].mean()))
        return out

    neg_by_ch: list[float | None] = []
    for j in range(q.shape[1]):
        vals = q[:, j]
        ok = torch.isfinite(vals)
        neg_by_ch.append(None if not bool(ok.any()) else float((vals[ok] < 0).to(torch.float64).mean()))

    return {
        "q_mean_by_channel": means(q),
        "q_negative_fraction_by_channel": neg_by_ch,
        "centered_singleton_norm_mean_by_channel": means(dn),
        "centered_singleton_orthogonal_norm_mean_by_channel": means(ortho),
        "raw_singleton_common_mode_mean_by_channel": means(common),
        "centered_singleton_cross_dot_mean_matrix": cross_dot.mean(dim=0).detach().cpu().tolist(),
        "v_small_pair_count": int((~defined).sum()),
        "pair_count": int(len(v)),
    }
