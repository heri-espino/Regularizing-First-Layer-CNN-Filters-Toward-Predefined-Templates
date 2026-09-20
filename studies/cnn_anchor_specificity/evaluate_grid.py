"""Evaluate frozen Stage-G anchor-specificity checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.append(str(Path(__file__).resolve().parent))
import anchor_core as ac  # noqa: E402

KS = tuple(range(1, 17))
MATCH_KS = (1, 2, 4, 8)
N_CONTROLS = 8
DEN_EPS = 1e-10
PATCH_ATOL = 2e-5
PATCH_RTOL = 1e-4
CONTROL_METRICS = (
    "prob_fidelity",
    "centered_logit_fidelity",
    "prob_error_reduction",
    "cf_accuracy",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    os.replace(tmp, path)


def center_logits(x):
    return x - x.mean(dim=1, keepdim=True)


def squared_error_sum(x, y):
    return float((x - y).square().sum())


def squared_error_mpp(x, y):
    return float((x - y).square().sum(dim=1).mean())


def fidelity(patch_sum, base_sum):
    return None if base_sum < DEN_EPS else 1.0 - patch_sum / base_sum


@torch.inference_mode()
def collect(model, x, batch, device):
    hs, logits = [], []
    for st in range(0, len(x), batch):
        h = model.features(torch.from_numpy(x[st:st+batch]).to(device))
        hs.append(h)
        logits.append(model.tail(h))
    return torch.cat(hs), torch.cat(logits)


def pair_tensors(task, n, device):
    return tuple(torch.as_tensor(v, device=device) for v in ac.legacy_core.pairs(task, n // 4))


@torch.inference_mode()
def patch_logits(model, H, order, k, pair, batch):
    b, c, g = pair
    order = torch.as_tensor(order, device=H.device)
    out = []
    for st in range(0, len(b), batch):
        bs, cs, gs = b[st:st+batch], c[st:st+batch], g[st:st+batch]
        h = H[bs].clone()
        ix = order[gs, :k]
        bi = torch.arange(len(bs), device=H.device)[:, None]
        h[bi, ix] = H[cs][bi, ix]
        out.append(model.tail(h))
    return torch.cat(out)


def measure(logits_s, logits_0, logits_1, labels):
    p_s, p_0, p_1 = logits_s.softmax(1), logits_0.softmax(1), logits_1.softmax(1)
    c_s, c_0, c_1 = center_logits(logits_s), center_logits(logits_0), center_logits(logits_1)

    prob_base_sum = squared_error_sum(p_0, p_1)
    prob_patch_sum = squared_error_sum(p_s, p_1)
    clogit_base_sum = squared_error_sum(c_0, c_1)
    clogit_patch_sum = squared_error_sum(c_s, c_1)
    raw_base_sum = squared_error_sum(logits_0, logits_1)
    raw_patch_sum = squared_error_sum(logits_s, logits_1)
    pred = logits_s.argmax(1)
    return {
        "prob_fidelity": fidelity(prob_patch_sum, prob_base_sum),
        "centered_logit_fidelity": fidelity(clogit_patch_sum, clogit_base_sum),
        "raw_logit_fidelity": fidelity(raw_patch_sum, raw_base_sum),
        "prob_error_reduction": squared_error_mpp(p_0, p_1) - squared_error_mpp(p_s, p_1),
        "centered_logit_error_reduction": squared_error_mpp(c_0, c_1) - squared_error_mpp(c_s, c_1),
        "raw_logit_error_reduction": squared_error_mpp(logits_0, logits_1) - squared_error_mpp(logits_s, logits_1),
        "cf_accuracy": float((pred == labels).float().mean()),
        "agreement": float((pred == logits_1.argmax(1)).float().mean()),
    }


def metric_mean(values, key):
    vals = [v[key] for v in values if v[key] is not None]
    return None if not vals else float(np.mean(vals))


def replacement_energy(H, pair, n_concepts):
    b, c, g = pair
    out = np.zeros((n_concepts, H.shape[1]), dtype=np.float64)
    for concept in range(n_concepts):
        d = H[c[g == concept]] - H[b[g == concept]]
        out[concept] = d.square().sum((0, 2, 3)).detach().cpu().numpy().astype(np.float64)
    return out


def subset_tables():
    out = {}
    for k in MATCH_KS:
        combos = np.array(list(itertools.combinations(range(16), k)), dtype=np.int64)
        mask = np.zeros((len(combos), 16), dtype=np.float64)
        mask[np.arange(len(combos))[:, None], combos] = 1.0
        out[k] = (combos, mask)
    return out


SUBSETS = subset_tables()


def energy_matched_orders(ranking, energy, k):
    combos, combo_mask = SUBSETS[k]
    controls = [np.empty_like(ranking) for _ in range(N_CONTROLS)]
    diagnostics = []
    eps = 1e-12
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
                "concept": int(concept),
                "control": int(j),
                "k": int(k),
                "selected_energy": target,
                "control_energy": float(values[idx]),
                "relative_energy_error": float(rel[idx]),
            })
    return controls, diagnostics


@torch.inference_mode()
def evaluate_one(model, val, test, task, arch, anchor_family, block, init_rep, batch, device):
    hv, lv = collect(model, val["x"], batch, device)
    ht, lt = collect(model, test["x"], batch, device)

    zv = hv.amax((2, 3)).cpu()
    ranking, signs, effects = ac.legacy_core.concept_orders(zv, val["concepts"])

    vpairs = pair_tensors(task, len(hv), device)
    energy = replacement_energy(hv, vpairs, ranking.shape[0])
    pairs = pair_tensors(task, len(ht), device)
    b, c, _ = pairs
    logits_0, logits_1 = lt[b], lt[c]
    labels = c % 4

    full = patch_logits(model, ht, ranking, 16, pairs, batch)
    noop = patch_logits(model, ht, ranking, 0, pairs, batch)
    if not torch.allclose(full, logits_1, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError("Full patch identity failed")
    if not torch.allclose(noop, logits_0, atol=PATCH_ATOL, rtol=PATCH_RTOL):
        raise AssertionError("No-op identity failed")

    base = measure(logits_0, logits_0, logits_1, labels)
    rr = np.random.default_rng(ac.control_seed(block, task, arch, init_rep))
    random_orders = [
        np.stack([rr.permutation(16) for _ in range(ranking.shape[0])])
        for _ in range(N_CONTROLS)
    ]

    rows, matching = [], []
    for k in KS:
        selected = measure(
            patch_logits(model, ht, ranking, k, pairs, batch),
            logits_0, logits_1, labels,
        )
        random_values = [
            measure(patch_logits(model, ht, order, k, pairs, batch), logits_0, logits_1, labels)
            for order in random_orders
        ]
        row = {"k": int(k), **selected}
        for metric in CONTROL_METRICS:
            rv = metric_mean(random_values, metric)
            row[f"random_{metric}"] = rv
            row[f"selected_minus_random_{metric}"] = None if selected[metric] is None or rv is None else selected[metric] - rv
            row[f"energy_{metric}"] = None
            row[f"selected_minus_energy_{metric}"] = None

        if k in MATCH_KS:
            controls, diag = energy_matched_orders(ranking, energy, k)
            matching.extend(diag)
            energy_values = [
                measure(patch_logits(model, ht, order, k, pairs, batch), logits_0, logits_1, labels)
                for order in controls
            ]
            for metric in CONTROL_METRICS:
                ev = metric_mean(energy_values, metric)
                row[f"energy_{metric}"] = ev
                row[f"selected_minus_energy_{metric}"] = None if selected[metric] is None or ev is None else selected[metric] - ev
        rows.append(row)

    learned = model.conv.weight.detach().cpu().numpy()
    own_bank = ac.anchor_bank(anchor_family, block, init_rep)
    structured = ac.structured_bank()
    return {
        "test_acc": float((lt.argmax(1).cpu().numpy() == test["y"]).mean()),
        "own_anchor_alignment": ac.alignment_to(learned, own_bank),
        "structured_template_alignment": ac.alignment_to(learned, structured),
        "pair_count": int(len(b)),
        "prob_input_effect_mpp": squared_error_mpp(logits_0.softmax(1), logits_1.softmax(1)),
        "centered_logit_input_effect_mpp": squared_error_mpp(center_logits(logits_0), center_logits(logits_1)),
        "raw_logit_input_effect_mpp": squared_error_mpp(logits_0, logits_1),
        "ranking": ranking.tolist(),
        "ranking_signs": signs.tolist(),
        "ranking_effects": effects.tolist(),
        "validation_channel_replacement_energy": energy.tolist(),
        "matching": matching,
        "rows": rows,
        "full_patch_max_logit_error": float((full - logits_1).abs().max()),
        "noop_max_logit_error": float((noop - logits_0).abs().max()),
        "anchor_diagnostics": ac.verify_anchor(anchor_family, block, init_rep),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--device", choices=("cuda","cpu"), default="cuda")
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    if args.batch_size < 1:
        p.error("batch-size must be positive")
    if args.device == "cuda" and not torch.cuda.is_available():
        p.error("CUDA requested but unavailable")

    torch.set_num_threads(2)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    inp = Path(args.input).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    design = json.loads((inp / "design.json").read_text())
    if not (inp / "GRID_COMPLETE.json").exists():
        raise SystemExit("Stage-G training grid is not marked complete.")

    expected = (
        int(design["blocks"]) * int(design["init_reps"]) * len(design["tasks"])
        * len(design["architectures"]) * len(design["anchor_families"])
        * len(design["treatments"])
    )
    if design.get("smoke"):
        expected = json.loads((inp / "GRID_COMPLETE.json").read_text())["complete"]

    eval_design = {
        "study": "cnn_anchor_specificity_stage_g_evaluation",
        "training_design_sha256": sha256(inp / "design.json"),
        "protocol_sha256": sha256(Path(__file__).with_name("PROTOCOL.md")),
        "anchor_core_sha256": sha256(Path(ac.__file__)),
        "evaluator_sha256": sha256(Path(__file__)),
        "device": args.device,
        "batch_size": args.batch_size,
        "budgets": list(KS),
        "energy_matched_budgets": list(MATCH_KS),
        "random_controls": N_CONTROLS,
        "ranking": "validation_standardized_first_layer_global_max_activation_contrast",
        "expected_models": expected,
        "trains_models": False,
    }
    dp = out / "design.json"
    if dp.exists():
        if json.loads(dp.read_text()) != eval_design:
            raise SystemExit("Existing Stage-G evaluation design differs. Use a new output root.")
    else:
        atomic_json(dp, eval_design)

    jobs = []
    for cp in sorted((inp / "runs").glob("*/*/*/block*/init*/*/epoch_*.pt")):
        treatment = cp.parent.name
        init_rep = int(cp.parent.parent.name.replace("init",""))
        block = int(cp.parent.parent.parent.name.replace("block",""))
        anchor_family = cp.parent.parent.parent.parent.name
        arch = cp.parent.parent.parent.parent.parent.name
        task = cp.parent.parent.parent.parent.parent.parent.name
        jobs.append((task, arch, anchor_family, block, init_rep, treatment, cp))
    if len(jobs) != expected:
        raise SystemExit(f"Expected {expected} Stage-G checkpoints, found {len(jobs)}")
    if args.smoke:
        jobs = jobs[:min(8, len(jobs))]

    device = torch.device(args.device)
    ac.legacy_core.ROOT = inp

    for i, (task, arch, anchor_family, block, init_rep, treatment, cp) in enumerate(jobs, 1):
        target = (
            out / "runs" / task / arch / anchor_family
            / f"block{block:04d}" / f"init{init_rep:02d}" / treatment
            / cp.with_suffix(".json").name
        )
        if target.exists():
            print(f"SKIP [{i}/{len(jobs)}] {task} {arch} {anchor_family} block={block} init={init_rep} {treatment}", flush=True)
            continue

        model = ac.ArchitectureNet(arch)
        saved = torch.load(cp, map_location="cpu", weights_only=True)
        model.load_state_dict(saved["model"])
        model.to(device).eval()

        data = {}
        for split in ("val","test"):
            pth = inp / "data" / task / f"block{block:02d}" / f"{split}.npz"
            with np.load(pth) as z:
                data[split] = {k:z[k] for k in ("x","y","concepts")}

        result = evaluate_one(
            model, data["val"], data["test"], task, arch, anchor_family,
            block, init_rep, args.batch_size, device
        )
        result.update({
            "task": task,
            "architecture": arch,
            "anchor_family": anchor_family,
            "block": block,
            "init_rep": init_rep,
            "treatment": treatment,
            "epoch": int(design["epochs"]),
            "checkpoint_sha256": sha256(cp),
        })
        atomic_json(target, result)
        print(f"DONE [{i}/{len(jobs)}] {task} {arch} {anchor_family} block={block} init={init_rep} {treatment}", flush=True)
        del model, saved
        if args.device == "cuda":
            torch.cuda.empty_cache()

    if not args.smoke:
        found = list((out / "runs").glob("*/*/*/block*/init*/*/epoch_*.json"))
        if len(found) != expected:
            raise SystemExit(f"Incomplete Stage-G evaluation: {len(found)} / {expected}")
        atomic_json(out / "GRID_COMPLETE.json", {"planned": expected, "complete": len(found), "training_invoked": False})
    print("Stage-G evaluation complete:", out, flush=True)


if __name__ == "__main__":
    main()
