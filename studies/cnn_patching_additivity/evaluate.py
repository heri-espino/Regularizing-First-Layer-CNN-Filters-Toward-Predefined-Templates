"""Post-hoc activation-patching additivity evaluator for frozen Stage-F/G checkpoints.

This file never trains a model. It reads the completed architecture-robustness or
anchor-specificity run, reuses validation-only rankings, evaluates all singleton
first-layer channel interventions, reconstructs joint interventions additively,
and measures the residual from that reconstruction.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from math_core import DEN_EPS, decompose_set, metrics_from_logits, singleton_geometry  # noqa: E402

CORE_ARCHS = ("tiny_gmp", "tiny_gap", "plain2_w16_gmp", "plain2_w16_gap")
PRIMARY_ANCHORS = ("structured_template", "pixel_permuted_template")
TREATMENTS = ("retention_1", "release_default")
PATCH_ATOL = 2e-5
PATCH_RTOL = 1e-4
LEGACY_TOL = 5e-6
IDENTITY_TOL = 5e-9
TINY_RESIDUAL_TOL = 5e-5
MATCH_KS = (1, 2, 4, 8)
N_CONTROLS = 8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    """Read JSON written by either Python or Windows PowerShell.

    Windows PowerShell 5.1 writes a UTF-8 BOM for `Set-Content -Encoding utf8`.
    `utf-8-sig` transparently strips that BOM while remaining compatible with
    ordinary BOM-free UTF-8 JSON files.
    """
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


def git(*args: str) -> str | None:
    try:
        p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    except Exception:
        return None
    return p.stdout.strip()


def current_provenance() -> dict[str, Any]:
    return {
        "repo_head": git("rev-parse", "HEAD"),
        "git_status_porcelain": git("status", "--porcelain"),
        "python": sys.version,
        "torch": torch.__version__,
        "numpy": np.__version__,
        "platform": platform.platform(),
    }


def load_core(source: str):
    if source == "architecture":
        d = ROOT / "studies" / "cnn_architecture_robustness"
        sys.path.insert(0, str(d))
        import architecture_core as core  # type: ignore
        return core
    if source == "anchor":
        d = ROOT / "studies" / "cnn_anchor_specificity"
        sys.path.insert(0, str(d))
        import anchor_core as core  # type: ignore
        return core
    raise ValueError(source)


def frozen_files(source: str) -> dict[str, Path]:
    if source == "architecture":
        return {
            "protocol": ROOT / "studies/cnn_architecture_robustness/PROTOCOL.md",
            "core": ROOT / "studies/cnn_architecture_robustness/architecture_core.py",
            "evaluator": ROOT / "studies/cnn_architecture_robustness/evaluate_grid.py",
            "legacy_core": ROOT / "studies/cnn_release_experiment/core.py",
        }
    return {
        "protocol": ROOT / "studies/cnn_anchor_specificity/PROTOCOL.md",
        "core": ROOT / "studies/cnn_anchor_specificity/anchor_core.py",
        "architecture_core": ROOT / "studies/cnn_architecture_robustness/architecture_core.py",
        "evaluator": ROOT / "studies/cnn_anchor_specificity/evaluate_grid.py",
        "legacy_core": ROOT / "studies/cnn_release_experiment/core.py",
    }


def source_paths(root: Path) -> tuple[Path, Path, Path]:
    training = root / "training"
    evaluation = root / "evaluation"
    manifest = root / "execution_manifest.json"
    for p in (training / "design.json", evaluation / "design.json", manifest):
        if not p.exists():
            raise SystemExit(f"Missing source artifact: {p}")
    return training, evaluation, manifest


def checkpoint_glob(source: str, training: Path) -> list[Path]:
    pattern = "*/*/block*/init*/*/epoch_0200.pt" if source == "architecture" else "*/*/*/block*/init*/*/epoch_0200.pt"
    return sorted((training / "runs").glob(pattern))


def parse_checkpoint(source: str, cp: Path) -> dict[str, Any]:
    if source == "architecture":
        treatment = cp.parent.name
        init_rep = int(cp.parent.parent.name.removeprefix("init"))
        block = int(cp.parent.parent.parent.name.removeprefix("block"))
        architecture = cp.parent.parent.parent.parent.name
        task = cp.parent.parent.parent.parent.parent.name
        return dict(task=task, architecture=architecture, block=block, init_rep=init_rep, treatment=treatment)
    treatment = cp.parent.name
    init_rep = int(cp.parent.parent.name.removeprefix("init"))
    block = int(cp.parent.parent.parent.name.removeprefix("block"))
    anchor_family = cp.parent.parent.parent.parent.name
    architecture = cp.parent.parent.parent.parent.parent.name
    task = cp.parent.parent.parent.parent.parent.parent.name
    return dict(task=task, architecture=architecture, anchor_family=anchor_family, block=block, init_rep=init_rep, treatment=treatment)


def evaluation_file(source: str, training: Path, evaluation: Path, cp: Path) -> Path:
    rel = cp.relative_to(training / "runs").with_suffix(".json")
    return evaluation / "runs" / rel


def load_npz(path: Path, keys=("x", "y", "concepts")) -> dict[str, np.ndarray]:
    with np.load(path) as z:
        return {k: z[k] for k in keys}


def source_code_checks(source: str, source_manifest: dict[str, Any]) -> dict[str, Any]:
    files = frozen_files(source)
    actual_sha = {name: sha256(path) for name, path in files.items()}
    actual_blob = {name: git("rev-parse", f"HEAD:{path.relative_to(ROOT).as_posix()}") for name, path in files.items()}
    expected_blob = source_manifest.get("source_git_blobs", {})
    blob_match = {}
    aliases = {"core": "architecture_core" if source == "architecture" else "anchor_core"}
    for name, blob in actual_blob.items():
        manifest_name = aliases.get(name, name)
        expected = expected_blob.get(manifest_name)
        blob_match[name] = None if expected is None or blob is None else bool(blob == expected)
    return {"sha256": actual_sha, "git_blob": actual_blob, "source_manifest_blob_match": blob_match}


def inventory(source: str, root: Path, sample_loads: int = 4) -> dict[str, Any]:
    training, evaluation, manifest_path = source_paths(root)
    training_design = read_json(training / "design.json")
    evaluation_design = read_json(evaluation / "design.json")
    source_manifest = read_json(manifest_path)
    cps = checkpoint_glob(source, training)
    records = [parse_checkpoint(source, p) for p in cps]
    evals = [evaluation_file(source, training, evaluation, p) for p in cps]
    missing_evals = [str(p) for p in evals if not p.exists()]
    complete = training / "GRID_COMPLETE.json"
    eval_complete = evaluation / "GRID_COMPLETE.json"

    expected = int(evaluation_design["expected_models"])
    counts: dict[str, dict[str, int]] = {}
    for field in ("task", "architecture", "anchor_family", "treatment", "block", "init_rep"):
        vals = Counter(str(r[field]) for r in records if field in r)
        if vals:
            counts[field] = dict(sorted(vals.items()))

    samples = []
    if cps:
        ix = np.linspace(0, len(cps) - 1, num=min(sample_loads, len(cps)), dtype=int)
        for i in np.unique(ix):
            cp = cps[int(i)]
            saved = torch.load(cp, map_location="cpu", weights_only=True)
            meta = saved.get("metadata", {})
            if "model" not in saved:
                raise AssertionError(f"Checkpoint has no model state_dict: {cp}")
            rec = parse_checkpoint(source, cp)
            for key, val in rec.items():
                if key in meta and meta[key] != val:
                    raise AssertionError(f"Checkpoint metadata mismatch {key}: {cp}")
            samples.append({
                "path": str(cp), "sha256": sha256(cp), "epoch": int(saved.get("epoch", -1)),
                "state_keys": len(saved["model"]), "metadata": meta,
            })

    return {
        "source": source,
        "root": str(root),
        "training_design_sha256": sha256(training / "design.json"),
        "evaluation_design_sha256": sha256(evaluation / "design.json"),
        "execution_manifest_sha256": sha256(manifest_path),
        "training_grid_complete": complete.exists(),
        "evaluation_grid_complete": eval_complete.exists(),
        "expected_models": expected,
        "checkpoints_found": len(cps),
        "evaluations_found": len(cps) - len(missing_evals),
        "missing_evaluations": missing_evals[:100],
        "missing_evaluation_count": len(missing_evals),
        "counts": counts,
        "sample_checkpoints": samples,
        "training_design": training_design,
        "evaluation_design": evaluation_design,
        "source_code_checks": source_code_checks(source, source_manifest),
    }


def pair_tensors(core, task: str, n: int, device: torch.device):
    return tuple(torch.as_tensor(v, device=device) for v in core.legacy_core.pairs(task, n // 4))


@torch.inference_mode()
def collect(model, x: np.ndarray, batch: int, device: torch.device):
    hs, logits = [], []
    for st in range(0, len(x), batch):
        h = model.features(torch.from_numpy(x[st:st + batch]).to(device))
        hs.append(h)
        logits.append(model.tail(h))
    return torch.cat(hs), torch.cat(logits)


@torch.inference_mode()
def patch_logits(model, H, order: np.ndarray, k: int, pair, batch: int):
    b, c, g = pair
    order_t = torch.as_tensor(order, device=H.device)
    out = []
    for st in range(0, len(b), batch):
        bs, cs, gs = b[st:st + batch], c[st:st + batch], g[st:st + batch]
        h = H[bs].clone()
        if k:
            ix = order_t[gs, :k]
            bi = torch.arange(len(bs), device=H.device)[:, None]
            h[bi, ix] = H[cs][bi, ix]
        out.append(model.tail(h))
    return torch.cat(out)


@torch.inference_mode()
def singleton_logits(model, H, pair, n_concepts: int, batch: int) -> torch.Tensor:
    outs = []
    rest = np.arange(16)
    for ch in range(16):
        tail = rest[rest != ch]
        order = np.tile(np.r_[ch, tail], (n_concepts, 1))
        outs.append(patch_logits(model, H, order, 1, pair, batch).cpu())
    return torch.stack(outs, dim=1)


def replacement_energy(H, pair, n_concepts: int) -> np.ndarray:
    b, c, g = pair
    out = np.zeros((n_concepts, H.shape[1]), dtype=np.float64)
    for concept in range(n_concepts):
        d = H[c[g == concept]] - H[b[g == concept]]
        out[concept] = d.square().sum((0, 2, 3)).detach().cpu().numpy().astype(np.float64)
    return out


def subset_table(k: int):
    combos = np.array(list(itertools.combinations(range(16), k)), dtype=np.int64)
    mask = np.zeros((len(combos), 16), dtype=np.float64)
    mask[np.arange(len(combos))[:, None], combos] = 1.0
    return combos, mask


def energy_matched_orders(ranking: np.ndarray, energy: np.ndarray, k: int):
    combos, combo_mask = subset_table(k)
    controls = [np.empty_like(ranking) for _ in range(N_CONTROLS)]
    eps = 1e-12
    diagnostics = []
    for concept in range(ranking.shape[0]):
        selected = np.sort(ranking[concept, :k])
        smask = np.zeros(16, dtype=np.float64)
        smask[selected] = 1.0
        target = float(smask @ energy[concept])
        values = combo_mask @ energy[concept]
        rel = np.abs(values - target) / (target + eps)
        same = np.all(combos == selected[None, :], axis=1)
        rel[same] = np.inf
        chosen = np.argsort(rel, kind="stable")[:N_CONTROLS]
        for j, idx in enumerate(chosen):
            combo = combos[idx]
            remaining = np.array([ch for ch in range(16) if ch not in set(combo.tolist())], dtype=np.int64)
            controls[j][concept] = np.r_[combo, remaining]
            diagnostics.append({
                "concept": int(concept), "control": int(j), "k": int(k),
                "selected_energy": target, "control_energy": float(values[idx]),
                "relative_energy_error": float(rel[idx]),
            })
    return controls, diagnostics


def random_orders(source: str, core, meta: dict[str, Any], n_concepts: int):
    if source == "architecture":
        rr = core.control_rng(meta["block"], meta["task"], meta["architecture"], meta["init_rep"])
    else:
        rr = np.random.default_rng(core.control_seed(meta["block"], meta["task"], meta["architecture"], meta["init_rep"]))
    return [np.stack([rr.permutation(16) for _ in range(n_concepts)]) for _ in range(N_CONTROLS)]


def channel_sets_for_pairs(order: np.ndarray, k: int, g_cpu: torch.Tensor) -> torch.Tensor:
    if k == 0:
        return torch.empty((len(g_cpu), 0), dtype=torch.long)
    order_t = torch.as_tensor(order, dtype=torch.long)
    return order_t[g_cpu, :k]


def original_metric_row(source_eval: dict[str, Any], k: int) -> dict[str, Any]:
    for row in source_eval["rows"]:
        if int(row["k"]) == int(k):
            return row
    raise KeyError(k)


def diff_or_none(a, b):
    return None if a is None or b is None else float(a) - float(b)


def verify_selected_against_source(row: dict[str, Any], original: dict[str, Any], tol: float = LEGACY_TOL):
    fields = ("prob_fidelity", "centered_logit_fidelity", "prob_error_reduction")
    diffs = {}
    for field in fields:
        new = row.get(f"observed_{field}")
        old = original.get(field)
        d = diff_or_none(new, old)
        diffs[field] = d
        if d is not None and abs(d) > tol:
            raise AssertionError(f"Source metric reproduction failed for {field}: {d:+.3g} > {tol}")
    return diffs


def aggregate_control_reproduction(rows: list[dict[str, Any]], original: dict[str, Any], prefix: str):
    out = {}
    for metric in ("prob_fidelity", "centered_logit_fidelity", "prob_error_reduction"):
        vals = [r[f"observed_{metric}"] for r in rows if r[f"observed_{metric}"] is not None]
        mean = None if not vals else float(np.mean(vals))
        old = original.get(f"{prefix}_{metric}")
        d = diff_or_none(mean, old)
        out[metric] = {"new_mean": mean, "source_mean": old, "difference": d}
        if d is not None and abs(d) > LEGACY_TOL:
            raise AssertionError(f"{prefix} source metric reproduction failed for {metric}: {d:+.3g}")
    return out


def model_output_path(output: Path, source: str, meta: dict[str, Any]) -> Path:
    p = output / "runs" / meta["task"] / meta["architecture"]
    if source == "anchor":
        p = p / meta["anchor_family"]
    return p / f"block{meta['block']:04d}" / f"init{meta['init_rep']:02d}" / meta["treatment"] / "epoch_0200.json"


def pair_output_path(summary_path: Path) -> Path:
    return summary_path.with_name("pair_arrays.npz")


def model_matches(meta: dict[str, Any], args, earliest_blocks: set[int] | None) -> bool:
    if args.tasks and meta["task"] not in args.tasks:
        return False
    if args.architectures and meta["architecture"] not in args.architectures:
        return False
    if args.source == "anchor" and args.anchor_families and meta["anchor_family"] not in args.anchor_families:
        return False
    if args.treatments and meta["treatment"] not in args.treatments:
        return False
    if earliest_blocks is not None and meta["block"] not in earliest_blocks:
        return False
    return True


def configure_determinism(device_name: str):
    torch.set_num_threads(2)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    if device_name == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but unavailable; no silent CPU fallback is used.")


def build_manifest(args, source_root: Path, jobs: list[Path], inv: dict[str, Any]) -> dict[str, Any]:
    return {
        "study": "cnn_patching_additivity_001",
        "status": "post_hoc_saved_checkpoint_analysis",
        "source": args.source,
        "source_root": str(source_root),
        "source_training_design_sha256": inv["training_design_sha256"],
        "source_evaluation_design_sha256": inv["evaluation_design_sha256"],
        "source_execution_manifest_sha256": inv["execution_manifest_sha256"],
        "source_code_checks": inv["source_code_checks"],
        "evaluator_sha256": sha256(Path(__file__)),
        "math_core_sha256": sha256(HERE / "math_core.py"),
        "protocol_sha256": sha256(HERE / "PROTOCOL.md") if (HERE / "PROTOCOL.md").exists() else None,
        "device": args.device,
        "batch_size": args.batch_size,
        "set_families": args.set_families,
        "save_pair_arrays": bool(args.save_pair_arrays),
        "tasks": args.tasks,
        "architectures": args.architectures,
        "anchor_families": args.anchor_families if args.source == "anchor" else None,
        "treatments": args.treatments,
        "max_blocks": args.max_blocks,
        "jobs": len(jobs),
        "patch_atol": PATCH_ATOL,
        "patch_rtol": PATCH_RTOL,
        "legacy_metric_tolerance": LEGACY_TOL,
        "identity_tolerance": IDENTITY_TOL,
        "tiny_residual_tolerance": TINY_RESIDUAL_TOL,
        "trains_models": False,
        **current_provenance(),
    }


def evaluate_checkpoint(source: str, core, source_root: Path, cp: Path, output: Path, args) -> dict[str, Any]:
    training, evaluation, _ = source_paths(source_root)
    meta = parse_checkpoint(source, cp)
    src_eval_path = evaluation_file(source, training, evaluation, cp)
    if not src_eval_path.exists():
        raise SystemExit(f"Missing original evaluation: {src_eval_path}")
    source_eval = read_json(src_eval_path)

    model = core.ArchitectureNet(meta["architecture"])
    saved = torch.load(cp, map_location="cpu", weights_only=True)
    model.load_state_dict(saved["model"])
    device = torch.device(args.device)
    model.to(device).eval()

    data = {}
    data_paths = {}
    for split in ("val", "test"):
        p = training / "data" / meta["task"] / f"block{meta['block']:02d}" / f"{split}.npz"
        data_paths[split] = p
        data[split] = load_npz(p)

    hv, _ = collect(model, data["val"]["x"], args.batch_size, device)
    ht, lt = collect(model, data["test"]["x"], args.batch_size, device)
    zv = hv.amax((2, 3)).cpu()
    recomputed_ranking, signs, effects = core.legacy_core.concept_orders(zv, data["val"]["concepts"])
    ranking = np.asarray(source_eval["ranking"], dtype=np.int64)
    if not np.array_equal(ranking, recomputed_ranking):
        raise AssertionError(f"Stored and recomputed validation ranking differ: {src_eval_path}")
    if source_eval.get("ranking_signs") is not None and not np.array_equal(np.asarray(source_eval["ranking_signs"]), signs):
        raise AssertionError(f"Stored and recomputed ranking signs differ: {src_eval_path}")

    pair = pair_tensors(core, meta["task"], len(ht), device)
    b, c, g = pair
    g_cpu = g.cpu()
    l0, l1 = lt[b].cpu(), lt[c].cpu()
    n_concepts = ranking.shape[0]

    # H must remain unchanged throughout patching.
    h_checksum_before = float(ht.to(torch.float64).sum().item())

    full = patch_logits(model, ht, ranking, 16, pair, args.batch_size).cpu()
    noop = patch_logits(model, ht, ranking, 0, pair, args.batch_size).cpu()
    full_err = float((full - l1).abs().max())
    noop_err = float((noop - l0).abs().max())
    if not torch.allclose(full, l1, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError(f"Full patch identity failed: {cp}")
    if not torch.allclose(noop, l0, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError(f"No-op identity failed: {cp}")

    singles = singleton_logits(model, ht, pair, n_concepts, args.batch_size)
    singleton_diag = singleton_geometry(l0, l1, singles)
    energy = replacement_energy(hv, pair_tensors(core, meta["task"], len(hv), device), n_concepts)
    rows: list[dict[str, Any]] = []
    pair_arrays: dict[str, np.ndarray] = {}
    reproduction: dict[str, Any] = {"selected": {}, "random": {}, "energy": {}}

    # k=0 explicit control.
    channels0 = channel_sets_for_pairs(ranking, 0, g_cpu)
    d0 = decompose_set(l0, l1, singles, l0, channels0, keep_pair_arrays=args.save_pair_arrays)
    row0 = {"set_family": "selected", "control_id": None, "k": 0, **d0.summary}
    rows.append(row0)
    if args.save_pair_arrays:
        for key, value in d0.pair_arrays.items():
            if key.startswith("singleton_") or key == "v_norm":
                pair_arrays[key] = value
            elif key in ("cancellation", "residual_norm", "g_obs", "g_add", "g_cross_term", "g_nonadditive_correction"):
                pair_arrays[f"selected_k00_{key}"] = value

    for k in range(1, 17):
        joint = patch_logits(model, ht, ranking, k, pair, args.batch_size).cpu()
        channels = channel_sets_for_pairs(ranking, k, g_cpu)
        dec = decompose_set(l0, l1, singles, joint, channels, keep_pair_arrays=args.save_pair_arrays)
        row = {"set_family": "selected", "control_id": None, "k": k, **dec.summary}
        original = original_metric_row(source_eval, k)
        reproduction["selected"][str(k)] = verify_selected_against_source(row, original)
        rows.append(row)
        if args.save_pair_arrays:
            for key in ("additive_change_norm", "selected_singleton_norm_sum", "cancellation", "residual_norm", "raw_residual_norm", "raw_residual_common_mode", "g_obs", "g_add", "g_individual_sum", "g_cross_term", "g_nonadditive_correction"):
                pair_arrays[f"selected_k{k:02d}_{key}"] = dec.pair_arrays[key]

    # Technical identities that must hold independent of the scientific outcome.
    k1 = next(r for r in rows if r["set_family"] == "selected" and r["k"] == 1)
    if k1["residual_max_abs_component"] > TINY_RESIDUAL_TOL:
        raise AssertionError(f"k=1 residual is not numerically zero: {k1['residual_max_abs_component']}")
    for row in rows:
        for key in ("identity_additive_direct_max_abs_error", "identity_additive_expanded_max_abs_error", "identity_nonadditive_correction_max_abs_error"):
            if row[key] > IDENTITY_TOL:
                raise AssertionError(f"Algebraic identity failed {key}: {row[key]}")
    if meta["architecture"] in ("tiny_gmp", "tiny_gap"):
        max_tiny = max(r["residual_max_abs_component"] for r in rows if r["set_family"] == "selected")
        if max_tiny > TINY_RESIDUAL_TOL:
            raise AssertionError(f"Analytic tiny additivity control failed: residual={max_tiny}")

    if "random" in args.set_families:
        ro = random_orders(source, core, meta, n_concepts)
        for k in range(1, 17):
            control_rows = []
            for j, order in enumerate(ro):
                joint = patch_logits(model, ht, order, k, pair, args.batch_size).cpu()
                channels = channel_sets_for_pairs(order, k, g_cpu)
                dec = decompose_set(l0, l1, singles, joint, channels, keep_pair_arrays=False)
                rr = {"set_family": "random", "control_id": j, "k": k, **dec.summary}
                rows.append(rr)
                control_rows.append(rr)
            reproduction["random"][str(k)] = aggregate_control_reproduction(control_rows, original_metric_row(source_eval, k), "random")

    matching_diagnostics = []
    if "energy" in args.set_families:
        for k in MATCH_KS:
            controls, diag = energy_matched_orders(ranking, energy, k)
            matching_diagnostics.extend(diag)
            control_rows = []
            for j, order in enumerate(controls):
                joint = patch_logits(model, ht, order, k, pair, args.batch_size).cpu()
                channels = channel_sets_for_pairs(order, k, g_cpu)
                dec = decompose_set(l0, l1, singles, joint, channels, keep_pair_arrays=False)
                rr = {"set_family": "energy", "control_id": j, "k": k, **dec.summary}
                rows.append(rr)
                control_rows.append(rr)
            reproduction["energy"][str(k)] = aggregate_control_reproduction(control_rows, original_metric_row(source_eval, k), "energy")

    h_checksum_after = float(ht.to(torch.float64).sum().item())
    if h_checksum_after != h_checksum_before:
        raise AssertionError("Cached first-layer activations were modified in-place")

    result = {
        **meta,
        "epoch": int(saved.get("epoch", 200)),
        "checkpoint_sha256": sha256(cp),
        "source_evaluation_sha256": sha256(src_eval_path),
        "val_data_sha256": sha256(data_paths["val"]),
        "test_data_sha256": sha256(data_paths["test"]),
        "pair_count": int(len(b)),
        "ranking": ranking.tolist(),
        "ranking_signs": np.asarray(signs).tolist(),
        "ranking_effects": np.asarray(effects).tolist(),
        "validation_channel_replacement_energy": energy.tolist(),
        "singleton_geometry": singleton_diag,
        "rows": rows,
        "source_metric_reproduction": reproduction,
        "matching_diagnostics": matching_diagnostics,
        "full_patch_max_logit_error": full_err,
        "noop_max_logit_error": noop_err,
        "cached_activation_checksum": h_checksum_before,
    }
    if source == "anchor":
        result["anchor_diagnostics"] = core.verify_anchor(meta["anchor_family"], meta["block"], meta["init_rep"])

    del model, saved, hv, ht, lt
    if args.device == "cuda":
        torch.cuda.empty_cache()
    return result, pair_arrays


def run(args):
    configure_determinism(args.device)
    source_root = Path(args.input).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    core = load_core(args.source)
    training, _, _ = source_paths(source_root)
    core.legacy_core.ROOT = training

    inv = inventory(args.source, source_root)
    if inv["checkpoints_found"] != inv["expected_models"] or inv["missing_evaluation_count"]:
        raise SystemExit(
            f"Source incomplete: checkpoints {inv['checkpoints_found']}/{inv['expected_models']}, "
            f"missing evaluations={inv['missing_evaluation_count']}"
        )
    bad_blob = {k: v for k, v in inv["source_code_checks"]["source_manifest_blob_match"].items() if v is False}
    if bad_blob:
        raise SystemExit(f"Frozen source Git blobs differ from the source execution manifest: {bad_blob}")

    cps = checkpoint_glob(args.source, training)
    metas = [parse_checkpoint(args.source, p) for p in cps]
    earliest_blocks = None
    if args.max_blocks:
        blocks = sorted({m["block"] for m in metas})[: args.max_blocks]
        earliest_blocks = set(blocks)
    jobs = [p for p, m in zip(cps, metas) if model_matches(m, args, earliest_blocks)]
    if not jobs:
        raise SystemExit("No checkpoints match the requested scope")

    manifest = build_manifest(args, source_root, jobs, inv)
    manifest_path = output / "design.json"
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        # Ignore transient worktree status but require all scientific/run choices to match.
        for volatile in ("git_status_porcelain",):
            old.pop(volatile, None); manifest.pop(volatile, None)
        if old != manifest:
            raise SystemExit("Existing additivity design differs. Use a new --output root.")
    else:
        atomic_json(manifest_path, manifest)
        atomic_json(output / "inventory.json", inv)

    start = time.perf_counter()
    done_now = 0
    for i, cp in enumerate(jobs, 1):
        meta = parse_checkpoint(args.source, cp)
        target = model_output_path(output, args.source, meta)
        if target.exists():
            print(f"SKIP [{i}/{len(jobs)}] {meta}", flush=True)
            continue
        t0 = time.perf_counter()
        result, arrays = evaluate_checkpoint(args.source, core, source_root, cp, output, args)
        result["evaluation_seconds"] = time.perf_counter() - t0
        if args.save_pair_arrays and arrays:
            pp = pair_output_path(target)
            atomic_npz(pp, arrays)
            result["pair_arrays"] = str(pp.relative_to(output))
            result["pair_arrays_bytes"] = pp.stat().st_size
        atomic_json(target, result)
        done_now += 1
        print(
            f"DONE [{i}/{len(jobs)}] {meta['task']} {meta['architecture']} "
            + (f"{meta.get('anchor_family')} " if args.source == 'anchor' else "")
            + f"block={meta['block']} init={meta['init_rep']} {meta['treatment']} "
            + f"({result['evaluation_seconds']:.2f}s)", flush=True,
        )

    found = list((output / "runs").rglob("epoch_0200.json"))
    complete = len(found) == len(jobs)
    status = {
        "planned": len(jobs), "complete": len(found), "completed_this_invocation": done_now,
        "complete_grid_for_requested_scope": complete,
        "elapsed_seconds_this_invocation": time.perf_counter() - start,
        "training_invoked": False,
    }
    atomic_json(output / "RUN_STATUS.json", status)
    if complete:
        atomic_json(output / "GRID_COMPLETE.json", status)
    print(json.dumps(status, indent=2), flush=True)


def cmd_inventory(args):
    result = inventory(args.source, Path(args.input).resolve(), sample_loads=args.sample_loads)
    if args.output:
        atomic_json(Path(args.output).resolve(), result)
    print(json.dumps({
        "source": result["source"], "root": result["root"], "expected_models": result["expected_models"],
        "checkpoints_found": result["checkpoints_found"], "evaluations_found": result["evaluations_found"],
        "training_grid_complete": result["training_grid_complete"], "evaluation_grid_complete": result["evaluation_grid_complete"],
        "source_manifest_blob_match": result["source_code_checks"]["source_manifest_blob_match"],
    }, indent=2))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("inventory", help="Read-only inventory and provenance validation")
    q.add_argument("--source", choices=("architecture", "anchor"), required=True)
    q.add_argument("--input", required=True, help="Source study root containing training/ and evaluation/")
    q.add_argument("--output")
    q.add_argument("--sample-loads", type=int, default=4)

    q = sub.add_parser("run", help="Evaluate additivity on saved checkpoints; never trains")
    q.add_argument("--source", choices=("architecture", "anchor"), required=True)
    q.add_argument("--input", required=True)
    q.add_argument("--output", required=True)
    q.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    q.add_argument("--batch-size", type=int, default=256)
    q.add_argument("--tasks", nargs="+", default=["single_shape", "two_concepts"])
    q.add_argument("--architectures", nargs="+", default=None)
    q.add_argument("--anchor-families", nargs="+", default=None)
    q.add_argument("--treatments", nargs="+", default=list(TREATMENTS))
    q.add_argument("--set-families", nargs="+", choices=("selected", "random", "energy"), default=["selected"])
    q.add_argument("--max-blocks", type=int, default=None, help="Use earliest block IDs only; validation/benchmark scope")
    q.add_argument("--save-pair-arrays", action="store_true", help="Save compressed per-pair selected-set geometry; expensive in storage")
    return p


def main():
    p = parser()
    args = p.parse_args()
    if args.command == "inventory":
        cmd_inventory(args); return
    if args.batch_size < 1:
        p.error("--batch-size must be positive")
    if args.max_blocks is not None and args.max_blocks < 1:
        p.error("--max-blocks must be positive")
    if args.architectures is None:
        args.architectures = list(CORE_ARCHS) if args.max_blocks else None
    if args.source == "anchor" and args.anchor_families is None:
        args.anchor_families = list(PRIMARY_ANCHORS)
    run(args)


if __name__ == "__main__":
    main()