"""Re-evaluate saved Stage-D/E checkpoints under frozen alternative patching metrics.

No model is trained. Exact stored channel rankings are reused from the original
Stage-D/Stage-E evaluation artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "studies" / "cnn_release_experiment"))
import core  # noqa: E402

METHODS = ("contrast", "auroc", "validation_patch")
D_KS = (1, 2, 4, 8)
E_KS = tuple(range(1, 17))
DEN_EPS = 1e-10
LEGACY_TOL = 2e-5
PATCH_ATOL = 2e-5
PATCH_RTOL = 1e-4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    os.replace(tmp, path)


@torch.inference_mode()
def collect(model, x, batch, device):
    hs, logits = [], []
    for st in range(0, len(x), batch):
        h = model.features(torch.from_numpy(x[st : st + batch]).to(device))
        hs.append(h)
        logits.append(model.tail(h))
    return torch.cat(hs), torch.cat(logits)


@torch.inference_mode()
def patch_logits(model, H, orders, k, pair, batch):
    b, c, g = pair
    orders = torch.as_tensor(orders, device=H.device)
    out = []
    for st in range(0, len(b), batch):
        bs, cs, gs = b[st : st + batch], c[st : st + batch], g[st : st + batch]
        h = H[bs].clone()
        ix = orders[gs, :k]
        bi = torch.arange(len(bs), device=H.device)[:, None]
        h[bi, ix] = H[cs][bi, ix]
        out.append(model.tail(h))
    return torch.cat(out)


def pair_tensors(task, n, device):
    return tuple(torch.as_tensor(x, device=device) for x in core.pairs(task, n // 4))


def center_logits(x):
    return x - x.mean(dim=1, keepdim=True)


def squared_error_sum(x, y):
    return float((x - y).square().sum())


def squared_error_mean_per_pair(x, y):
    return float((x - y).square().sum(dim=1).mean())


def normalized_fidelity(patch_error_sum, base_error_sum):
    if base_error_sum < DEN_EPS:
        return None
    return 1.0 - patch_error_sum / base_error_sum


def measure(logits_s, logits_0, logits_1, labels):
    p_s = logits_s.softmax(1)
    p_0 = logits_0.softmax(1)
    p_1 = logits_1.softmax(1)

    c_s = center_logits(logits_s)
    c_0 = center_logits(logits_0)
    c_1 = center_logits(logits_1)

    prob_base_sum = squared_error_sum(p_0, p_1)
    prob_patch_sum = squared_error_sum(p_s, p_1)
    clogit_base_sum = squared_error_sum(c_0, c_1)
    clogit_patch_sum = squared_error_sum(c_s, c_1)
    raw_base_sum = squared_error_sum(logits_0, logits_1)
    raw_patch_sum = squared_error_sum(logits_s, logits_1)

    prob_base_mpp = squared_error_mean_per_pair(p_0, p_1)
    prob_patch_mpp = squared_error_mean_per_pair(p_s, p_1)
    clogit_base_mpp = squared_error_mean_per_pair(c_0, c_1)
    clogit_patch_mpp = squared_error_mean_per_pair(c_s, c_1)
    raw_base_mpp = squared_error_mean_per_pair(logits_0, logits_1)
    raw_patch_mpp = squared_error_mean_per_pair(logits_s, logits_1)

    pred = logits_s.argmax(1)
    return {
        "prob_fidelity": normalized_fidelity(prob_patch_sum, prob_base_sum),
        "centered_logit_fidelity": normalized_fidelity(clogit_patch_sum, clogit_base_sum),
        "raw_logit_fidelity": normalized_fidelity(raw_patch_sum, raw_base_sum),
        "prob_patch_error_mpp": prob_patch_mpp,
        "prob_error_reduction": prob_base_mpp - prob_patch_mpp,
        "centered_logit_patch_error_mpp": clogit_patch_mpp,
        "centered_logit_error_reduction": clogit_base_mpp - clogit_patch_mpp,
        "raw_logit_patch_error_mpp": raw_patch_mpp,
        "raw_logit_error_reduction": raw_base_mpp - raw_patch_mpp,
        "cf_accuracy": float((pred == labels).float().mean()),
        "agreement": float((pred == logits_1.argmax(1)).float().mean()),
    }


def stage_spec(stage: str, input_root: Path):
    training = input_root / "training"
    design = json.loads((training / "design.json").read_text())

    if stage == "d":
        assert design["start_block"] == 4000 and design["blocks"] == 20
        assert design["tasks"] == ["two_concepts"]
        assert set(design["architectures"]) == {"TinyCNN", "TwoLayerCNN"}
        assert set(design["conditions"]) == {"template_retention_1", "template_release"}
        return {
            "training": training,
            "rankings": input_root / "patch_eval",
            "id_key": "condition",
            "ids": tuple(design["conditions"]),
            "tasks": tuple(design["tasks"]),
            "architectures": tuple(design["architectures"]),
            "blocks": tuple(range(design["start_block"], design["start_block"] + design["blocks"])),
            "epoch": int(design["epochs"]),
            "ks": D_KS,
            "expected": 80,
            "design": design,
        }

    assert stage == "e"
    assert design["start_block"] == 5000 and design["blocks"] == 50
    assert set(design["tasks"]) == {"single_shape", "two_concepts"}
    assert set(design["architectures"]) == {"TinyCNN", "TwoLayerCNN"}
    expected_profiles = {
        "template_init",
        "retention_0p1",
        "retention_1",
        "release_early",
        "release_default",
        "release_late",
    }
    assert set(design["profiles"]) == expected_profiles
    return {
        "training": training,
        "rankings": input_root / "evaluation",
        "id_key": "profile",
        "ids": tuple(design["profiles"]),
        "tasks": tuple(design["tasks"]),
        "architectures": tuple(design["architectures"]),
        "blocks": tuple(range(design["start_block"], design["start_block"] + design["blocks"])),
        "epoch": int(design["epochs"]),
        "ks": E_KS,
        "expected": 1200,
        "design": design,
    }


def ranking_file(spec, task, arch, block, treatment):
    return (
        spec["rankings"]
        / "runs"
        / task
        / arch
        / f"block{block:04d}"
        / treatment
        / f"epoch_{spec['epoch']:04d}.json"
    )


def checkpoint_file(spec, task, arch, block, treatment):
    return (
        spec["training"]
        / "runs"
        / task
        / arch
        / f"block{block:04d}"
        / treatment
        / f"epoch_{spec['epoch']:04d}.pt"
    )


def load_test(spec, task, block):
    p = spec["training"] / "data" / task / f"block{block:02d}" / "test.npz"
    with np.load(p) as z:
        return {k: z[k] for k in ("x", "y")}, p


@torch.inference_mode()
def evaluate_one(spec, task, arch, block, treatment, batch, device):
    cp = checkpoint_file(spec, task, arch, block, treatment)
    rp = ranking_file(spec, task, arch, block, treatment)
    if not cp.exists():
        raise SystemExit(f"Missing checkpoint: {cp}")
    if not rp.exists():
        raise SystemExit(f"Missing stored ranking artifact: {rp}")

    source = json.loads(rp.read_text())
    if tuple(sorted(source["rankings"])) != tuple(sorted(METHODS)):
        raise AssertionError((rp, source["rankings"]))
    stored_rows = {(r["method"], int(r["k"])): r for r in source["rows"]}

    model = core.Network(arch)
    saved = torch.load(cp, map_location="cpu", weights_only=True)
    model.load_state_dict(saved["model"])
    model.to(device).eval()

    test, test_path = load_test(spec, task, block)
    H, logits = collect(model, test["x"], batch, device)
    pair = pair_tensors(task, len(H), device)
    b, c, _ = pair
    logits_0, logits_1 = logits[b], logits[c]
    labels = c % 4

    primary_order = np.asarray(source["rankings"]["contrast"], dtype=np.int64)
    full = patch_logits(model, H, primary_order, 16, pair, batch)
    noop = patch_logits(model, H, primary_order, 0, pair, batch)
    full_error = float((full - logits_1).abs().max())
    noop_error = float((noop - logits_0).abs().max())
    if not torch.allclose(full, logits_1, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError(f"Full patch identity failed: {cp}")
    if not torch.allclose(noop, logits_0, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError(f"No-op identity failed: {cp}")

    base = measure(logits_0, logits_0, logits_1, labels)
    rows = []
    max_legacy_diff = 0.0

    for method in METHODS:
        order = np.asarray(source["rankings"][method], dtype=np.int64)
        if order.ndim != 2 or order.shape[1] != 16:
            raise AssertionError((rp, method, order.shape))
        for k in spec["ks"]:
            patched = patch_logits(model, H, order, k, pair, batch)
            metrics = measure(patched, logits_0, logits_1, labels)
            stored = stored_rows.get((method, int(k)))
            if stored is None:
                raise AssertionError(f"Stored row missing for {method}, k={k}: {rp}")
            stored_f = stored.get("fidelity")
            recomputed_f = metrics["prob_fidelity"]
            if stored_f is None or recomputed_f is None:
                legacy_diff = None
            else:
                legacy_diff = abs(float(stored_f) - float(recomputed_f))
                max_legacy_diff = max(max_legacy_diff, legacy_diff)
                if legacy_diff > LEGACY_TOL:
                    raise AssertionError(
                        f"Legacy probability fidelity mismatch {legacy_diff:.6g} > {LEGACY_TOL}: {rp}, {method}, k={k}"
                    )
            rows.append(
                {
                    "method": method,
                    "k": int(k),
                    "selection_valid": bool(stored.get("selection_valid", True)),
                    "stored_prob_fidelity": stored_f,
                    "legacy_prob_fidelity_abs_diff": legacy_diff,
                    **metrics,
                }
            )

    result = {
        "stage": "D" if spec["expected"] == 80 else "E",
        "task": task,
        "architecture": arch,
        "block": int(block),
        spec["id_key"]: treatment,
        "epoch": int(spec["epoch"]),
        "pair_count": int(len(b)),
        "prob_input_effect_mpp": base["prob_patch_error_mpp"],
        "centered_logit_input_effect_mpp": base["centered_logit_patch_error_mpp"],
        "raw_logit_input_effect_mpp": base["raw_logit_patch_error_mpp"],
        "rows": rows,
        "checkpoint_sha256": sha256(cp),
        "ranking_artifact_sha256": sha256(rp),
        "test_data_sha256": sha256(test_path),
        "max_legacy_prob_fidelity_abs_diff": float(max_legacy_diff),
        "full_patch_max_logit_error": full_error,
        "noop_max_logit_error": noop_error,
    }
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=("d", "e"), required=True)
    p.add_argument("--input-root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.batch_size < 1:
        p.error("--batch-size must be positive")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but unavailable; no silent CPU fallback is used.")

    torch.set_num_threads(2)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    input_root = Path(args.input_root).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    spec = stage_spec(args.stage, input_root)
    device = torch.device(args.device)
    core.ROOT = spec["training"]

    evaluator_design = {
        "stage": args.stage,
        "input_training_design_sha256": sha256(spec["training"] / "design.json"),
        "protocol_sha256": sha256(Path(__file__).with_name("PROTOCOL.md")),
        "evaluator_sha256": sha256(Path(__file__)),
        "core_sha256": sha256(Path(core.__file__)),
        "device": args.device,
        "gpu": torch.cuda.get_device_name(0) if args.device == "cuda" else None,
        "batch_size": args.batch_size,
        "methods": list(METHODS),
        "budgets": list(spec["ks"]),
        "denominator_epsilon": DEN_EPS,
        "legacy_probability_tolerance": LEGACY_TOL,
        "patch_atol": PATCH_ATOL,
        "patch_rtol": PATCH_RTOL,
        "expected_models": spec["expected"],
        "reuses_stored_rankings": True,
        "trains_models": False,
    }
    design_path = out / "design.json"
    if design_path.exists():
        if json.loads(design_path.read_text()) != evaluator_design:
            raise SystemExit("Existing metric-sensitivity design differs. Use a new --output root.")
    else:
        atomic_json(design_path, evaluator_design)

    jobs = [
        (task, arch, block, treatment)
        for block in spec["blocks"]
        for task in spec["tasks"]
        for arch in spec["architectures"]
        for treatment in spec["ids"]
    ]
    if args.smoke:
        jobs = jobs[:1]

    for i, (task, arch, block, treatment) in enumerate(jobs, 1):
        target = out / "runs" / task / arch / f"block{block:04d}" / treatment / f"epoch_{spec['epoch']:04d}.json"
        if target.exists():
            print(f"SKIP [{i}/{len(jobs)}] {task} {arch} block={block} {treatment}", flush=True)
            continue
        result = evaluate_one(spec, task, arch, block, treatment, args.batch_size, device)
        atomic_json(target, result)
        print(f"DONE [{i}/{len(jobs)}] {task} {arch} block={block} {treatment}", flush=True)
        if args.device == "cuda":
            torch.cuda.empty_cache()

    if not args.smoke:
        found = list((out / "runs").glob("*/*/block*/*/epoch_*.json"))
        if len(found) != spec["expected"]:
            raise SystemExit(f"Incomplete metric evaluation: {len(found)} / {spec['expected']}")
        atomic_json(
            out / "EVAL_COMPLETE.json",
            {
                "planned": spec["expected"],
                "complete": len(found),
                "stage": args.stage,
                "training_invoked": False,
            },
        )
    print("Metric-sensitivity evaluation:", out, flush=True)


if __name__ == "__main__":
    main()
