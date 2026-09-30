"""Predetermined technical validation and benchmark for patching additivity.

Runs earliest renderer blocks by identifier, never selected by outcomes. No training.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import evaluate as ev

CORE_ARCHS = list(ev.CORE_ARCHS)
PRIMARY_ANCHORS = list(ev.PRIMARY_ANCHORS)


def args_for(source, input_root, output_root, device, batch_size, set_families, max_blocks=1, save_pair_arrays=False):
    return SimpleNamespace(
        source=source, input=str(input_root), output=str(output_root), device=device,
        batch_size=batch_size, tasks=["single_shape", "two_concepts"],
        architectures=CORE_ARCHS, anchor_families=PRIMARY_ANCHORS if source == "anchor" else None,
        treatments=list(ev.TREATMENTS), set_families=list(set_families), max_blocks=max_blocks,
        save_pair_arrays=save_pair_arrays,
    )


def selected_rows(result):
    return {(int(r["k"])): r for r in result["rows"] if r["set_family"] == "selected" and r.get("control_id") is None}


def compare_batches(a, b, tol=8e-6):
    ra, rb = selected_rows(a), selected_rows(b)
    fields = (
        "observed_centered_logit_fidelity", "additive_centered_logit_fidelity",
        "observed_prob_error_reduction", "additive_prob_error_reduction",
        "centered_residual_energy_ratio", "g_cross_term_mpp", "g_nonadditive_correction_mpp",
    )
    max_diff = 0.0
    for k in sorted(set(ra) & set(rb)):
        for f in fields:
            xa, xb = ra[k].get(f), rb[k].get(f)
            if xa is None or xb is None: continue
            max_diff = max(max_diff, abs(float(xa) - float(xb)))
    if max_diff > tol:
        raise AssertionError(f"Batch-size stability failed: max difference {max_diff:.6g} > {tol}")
    return max_diff


def source_validation(source, root, out, device, batch_size):
    run_args = args_for(source, root, out, device, batch_size, ["selected"], max_blocks=1, save_pair_arrays=False)
    ev.run(run_args)
    model_files = sorted((out / "runs").rglob("epoch_0200.json"))
    mtimes = {str(p): p.stat().st_mtime_ns for p in model_files}
    ev.run(run_args)  # Resume audit: every completed model must be skipped.
    after = {str(p): p.stat().st_mtime_ns for p in model_files}
    if mtimes != after:
        raise AssertionError("Resume validation failed: completed model outputs were rewritten")

    core = ev.load_core(source)
    training, _, _ = ev.source_paths(root)
    core.legacy_core.ROOT = training
    cps = ev.checkpoint_glob(source, training)
    metas = [ev.parse_checkpoint(source, p) for p in cps]
    candidates = [(p,m) for p,m in zip(cps,metas) if m["architecture"] in CORE_ARCHS and m["task"] == "two_concepts" and m["treatment"] == "retention_1" and (source != "anchor" or m["anchor_family"] == "structured_template")]
    candidates.sort(key=lambda pm: (pm[1]["block"], pm[1]["init_rep"], pm[1]["architecture"]))
    cp, meta = candidates[0]

    a64 = args_for(source, root, out, device, 64, ["selected"])
    a256 = args_for(source, root, out, device, batch_size, ["selected"])
    r64, _ = ev.evaluate_checkpoint(source, core, root, cp, out, a64)
    r256, _ = ev.evaluate_checkpoint(source, core, root, cp, out, a256)
    batch_diff = compare_batches(r64, r256)

    all_args = args_for(source, root, out, device, batch_size, ["selected", "random", "energy"])
    t0 = time.perf_counter()
    rall, _ = ev.evaluate_checkpoint(source, core, root, cp, out, all_args)
    all_seconds = time.perf_counter() - t0
    all_json_bytes = len((json.dumps(rall, allow_nan=False) + "\n").encode("utf-8"))

    objs = [json.loads(p.read_text()) for p in model_files]
    selected_seconds = [x.get("evaluation_seconds") for x in objs if x.get("evaluation_seconds") is not None]
    selected_sizes = [p.stat().st_size for p in model_files]
    return {
        "source": source,
        "validation_models": len(model_files),
        "earliest_block": min(x["block"] for x in objs),
        "batch_stability_checkpoint": str(cp),
        "batch_stability_max_abs_difference": batch_diff,
        "selected_only_mean_seconds_per_model": float(np.mean(selected_seconds)),
        "selected_only_mean_json_bytes_per_model": float(np.mean(selected_sizes)),
        "all_controls_benchmark_seconds_one_model": all_seconds,
        "all_controls_json_bytes_one_model": all_json_bytes,
        "all_controls_to_selected_time_ratio": all_seconds / max(float(np.mean(selected_seconds)), 1e-12),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--architecture-root", required=True)
    p.add_argument("--anchor-root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    p.add_argument("--batch-size", type=int, default=256)
    args = p.parse_args()
    ev.configure_determinism(args.device)

    out = Path(args.output).resolve(); out.mkdir(parents=True, exist_ok=True)
    arch = source_validation("architecture", Path(args.architecture_root).resolve(), out / "architecture", args.device, args.batch_size)
    anchor = source_validation("anchor", Path(args.anchor_root).resolve(), out / "anchor", args.device, args.batch_size)

    central_models = {"architecture": 25600, "anchor": 12800}
    arch_hours = arch["all_controls_benchmark_seconds_one_model"] * central_models["architecture"] / 3600
    anchor_hours = anchor["all_controls_benchmark_seconds_one_model"] * central_models["anchor"] / 3600
    additional_secondary_hours = anchor["all_controls_benchmark_seconds_one_model"] * 12800 / 3600
    central_hours = arch_hours + anchor_hours
    additional_ratio = additional_secondary_hours / max(central_hours, 1e-12)
    additional_storage_gib = anchor["all_controls_json_bytes_one_model"] * 12800 / (1024**3)
    secondary_permitted = bool(additional_ratio <= 0.35 and additional_storage_gib <= 10.0)

    benchmark = {
        "status": "technical_validation_complete_no_scientific_interpretation",
        "device": args.device,
        "batch_size": args.batch_size,
        "architecture": arch,
        "anchor": anchor,
        "projected_all_controls_hours": {
            "architecture_25600_models": arch_hours,
            "anchor_primary_12800_models": anchor_hours,
            "central_total": central_hours,
            "secondary_anchor_additional_12800_models": additional_secondary_hours,
        },
        "secondary_anchor_predeclared_cost_rule": {
            "max_additional_runtime_fraction_of_central": 0.35,
            "max_additional_summary_storage_gib": 10.0,
            "projected_additional_runtime_fraction": additional_ratio,
            "projected_additional_summary_storage_gib": additional_storage_gib,
            "run_secondary_anchors": secondary_permitted,
            "note": "Decision uses timing/storage only; do not inspect additivity outcomes before applying it.",
        },
    }
    ev.atomic_json(out / "VALIDATION_AND_BENCHMARK.json", benchmark)
    print(json.dumps(benchmark, indent=2))


if __name__ == "__main__":
    main()