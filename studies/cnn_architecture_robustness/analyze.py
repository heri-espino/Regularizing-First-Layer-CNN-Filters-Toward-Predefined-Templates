"""Analyze the frozen Stage-F architecture-robustness experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist
from scipy.stats import t as student_t
from scipy.stats import ttest_1samp

import sys
sys.path.append(str(Path(__file__).resolve().parent))
import architecture_core as ac  # noqa: E402

PRIMARY_TASK = "two_concepts"
PRIMARY_METRICS = ("centered_logit_fidelity", "prob_error_reduction")
ALL_METRICS = (
    "centered_logit_fidelity",
    "prob_error_reduction",
    "prob_fidelity",
    "raw_logit_fidelity",
    "centered_logit_error_reduction",
    "raw_logit_error_reduction",
    "cf_accuracy",
    "agreement",
)
INPUT_EFFECT_METRICS = (
    "prob_input_effect_mpp",
    "centered_logit_input_effect_mpp",
    "raw_logit_input_effect_mpp",
)
CORE_CONTROL_METRICS = (
    "centered_logit_fidelity",
    "prob_error_reduction",
    "prob_fidelity",
    "cf_accuracy",
)
BUDGETS_B = (1, 2, 4, 8)


def interval(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return {"n": n, "mean": np.nan, "sd": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    mean = float(x.mean())
    sd = float(x.std(ddof=1))
    err = float(student_t.ppf(0.975, n - 1) * sd / np.sqrt(n))
    return {"n": n, "mean": mean, "sd": sd, "ci_low": mean - err, "ci_high": mean + err}


def one_sample(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    q = interval(x)
    if len(x) < 2:
        return {**q, "t_stat": np.nan, "p_two_sided": np.nan}
    test = ttest_1samp(x, 0.0)
    return {**q, "t_stat": float(test.statistic), "p_two_sided": float(test.pvalue)}


def holm_adjust(values):
    p = np.asarray(values, dtype=float)
    out = np.full_like(p, np.nan)
    valid = np.isfinite(p)
    if not valid.any():
        return out
    ids = np.flatnonzero(valid)
    pv = p[valid]
    order = np.argsort(pv)
    running = 0.0
    m = len(pv)
    adjusted = np.empty(m, dtype=float)
    for rank, pos in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pv[pos]))
        adjusted[pos] = running
    out[ids] = adjusted
    return out


def repeated_measures_anova(matrix):
    y = np.asarray(matrix, dtype=float)
    if not np.isfinite(y).all():
        raise ValueError("Repeated-measures ANOVA requires a complete finite matrix")
    n, a = y.shape
    grand = y.mean()
    arch_means = y.mean(axis=0)
    block_means = y.mean(axis=1)
    ss_total = float(((y - grand) ** 2).sum())
    ss_arch = float(n * ((arch_means - grand) ** 2).sum())
    ss_block = float(a * ((block_means - grand) ** 2).sum())
    ss_error = max(0.0, ss_total - ss_arch - ss_block)
    df_arch = a - 1
    df_error = (a - 1) * (n - 1)
    ms_arch = ss_arch / df_arch
    ms_error = ss_error / df_error
    stat = np.inf if ms_error == 0 and ms_arch > 0 else (0.0 if ms_error == 0 else ms_arch / ms_error)
    p = 0.0 if np.isinf(stat) else float(f_dist.sf(stat, df_arch, df_error))
    partial_eta2 = ss_arch / (ss_arch + ss_error) if (ss_arch + ss_error) > 0 else 0.0
    return {
        "n_blocks": n,
        "n_architectures": a,
        "df_architecture": df_arch,
        "df_error": df_error,
        "F": float(stat),
        "p_two_sided_equivalent_upper_tail": p,
        "ss_architecture": ss_arch,
        "ss_block": ss_block,
        "ss_error": ss_error,
        "partial_eta_squared": float(partial_eta2),
    }


def load_outputs(root):
    files = sorted((root / "runs").glob("*/*/block*/init*/*/epoch_*.json"))
    if not (root / "GRID_COMPLETE.json").exists():
        raise SystemExit(f"Stage-F evaluation is not marked complete: {root}")

    rows = []
    models = []
    matching = []
    for path in files:
        v = json.loads(path.read_text())
        ident = {
            "task": v["task"],
            "architecture": v["architecture"],
            "block": int(v["block"]),
            "init_rep": int(v["init_rep"]),
            "treatment": v["treatment"],
            "epoch": int(v["epoch"]),
        }
        models.append(
            {
                **ident,
                "test_acc": v["test_acc"],
                "alignment": v["alignment"],
                "pair_count": v["pair_count"],
                "prob_input_effect_mpp": v["prob_input_effect_mpp"],
                "centered_logit_input_effect_mpp": v["centered_logit_input_effect_mpp"],
                "raw_logit_input_effect_mpp": v["raw_logit_input_effect_mpp"],
                "full_patch_max_logit_error": v["full_patch_max_logit_error"],
                "noop_max_logit_error": v["noop_max_logit_error"],
                "checkpoint_sha256": v["checkpoint_sha256"],
            }
        )
        for r in v["rows"]:
            rows.append({**ident, **r})
        for m in v.get("matching", []):
            matching.append({**ident, **m})
    return pd.DataFrame(rows), pd.DataFrame(models), pd.DataFrame(matching), files


def verify(rows, models, files):
    assert len(files) == 25600, len(files)
    assert len(models) == 25600
    assert set(rows.task) == set(ac.TASKS)
    assert set(rows.architecture) == set(ac.ARCHS)
    assert set(rows.treatment) == set(ac.TREATMENTS)
    assert set(rows.block) == set(range(6000, 6100))
    assert set(rows.init_rep) == {0, 1, 2, 3}
    assert set(rows.k) == set(range(1, 17))
    assert not rows.duplicated(
        ["task", "architecture", "block", "init_rep", "treatment", "k"]
    ).any()
    assert len(rows) == 25600 * 16
    for metric in PRIMARY_METRICS:
        primary = rows[rows.task == PRIMARY_TASK][metric]
        if not primary.notna().all():
            raise ValueError(f"Primary Stage-F metric contains undefined values: {metric}")


def treatment_deltas(rows):
    records = []
    id_cols = ["task", "architecture", "block", "init_rep", "k"]
    for metric in ALL_METRICS:
        p = rows.pivot(index=id_cols, columns="treatment", values=metric).reset_index()
        p["metric"] = metric
        p["delta"] = p["release_default"] - p["retention_1"]
        records.append(p[id_cols + ["metric", "delta"]])
    return pd.concat(records, ignore_index=True)


def make_b(delta_init):
    sub = delta_init[delta_init.k.isin(BUDGETS_B)]
    p = sub.pivot(
        index=["task", "architecture", "block", "init_rep", "metric"],
        columns="k",
        values="delta",
    ).reset_index()
    for k in BUDGETS_B:
        if k not in p:
            p[k] = np.nan
    p["B"] = (p[4] + p[8]) / 2 - (p[1] + p[2]) / 2
    return p[["task", "architecture", "block", "init_rep", "metric", "B"]]


def block_average_delta(delta_init):
    return (
        delta_init.groupby(["task", "architecture", "block", "metric", "k"], as_index=False)
        .agg(delta=("delta", "mean"), init_reps_finite=("delta", "count"))
    )


def block_average_b(b_init):
    return (
        b_init.groupby(["task", "architecture", "block", "metric"], as_index=False)
        .agg(B=("B", "mean"), init_reps_finite=("B", "count"))
    )


def summarize_architecture_b(b_block):
    rec = []
    for keys, s in b_block.groupby(["task", "architecture", "metric"], sort=False):
        q = one_sample(s.B.to_numpy(float))
        rec.append(
            {
                "task": keys[0],
                "architecture": keys[1],
                "metric": keys[2],
                **q,
            }
        )
    return pd.DataFrame(rec)


def summarize_curves(delta_block):
    rec = []
    for keys, s in delta_block.groupby(["task", "architecture", "metric", "k"], sort=False):
        q = interval(s.delta.to_numpy(float))
        rec.append(
            {
                "task": keys[0],
                "architecture": keys[1],
                "metric": keys[2],
                "k": int(keys[3]),
                **q,
            }
        )
    return pd.DataFrame(rec)


def primary_omnibus(b_block):
    rec = []
    for metric in PRIMARY_METRICS:
        s = b_block[(b_block.task == PRIMARY_TASK) & (b_block.metric == metric)]
        matrix = (
            s.pivot(index="block", columns="architecture", values="B")
            .reindex(index=range(6000, 6100), columns=list(ac.ARCHS))
        )
        result = repeated_measures_anova(matrix.to_numpy(float))
        rec.append({"task": PRIMARY_TASK, "metric": metric, **result})
    out = pd.DataFrame(rec)
    out["p_holm_two_metric_family"] = holm_adjust(
        out["p_two_sided_equivalent_upper_tail"].to_numpy(float)
    )
    return out


def bridge_contrasts(b_block):
    rec = []
    per = []
    for metric in PRIMARY_METRICS:
        s = b_block[(b_block.task == PRIMARY_TASK) & (b_block.metric == metric)]
        p = s.pivot(index="block", columns="architecture", values="B")
        d = p["tiny_gmp"] - p["plain2_w16_gmp"]
        q = one_sample(d.to_numpy(float))
        rec.append(
            {
                "task": PRIMARY_TASK,
                "metric": metric,
                "contrast": "tiny_gmp - plain2_w16_gmp",
                **q,
            }
        )
        per.extend(
            {
                "task": PRIMARY_TASK,
                "metric": metric,
                "block": int(block),
                "contrast": "tiny_gmp - plain2_w16_gmp",
                "difference": float(value),
            }
            for block, value in d.items()
        )
    out = pd.DataFrame(rec)
    out["p_holm_two_metric_family"] = holm_adjust(out.p_two_sided.to_numpy(float))
    return out, pd.DataFrame(per)


FACTOR_PAIRS = {
    "pooling": [
        ("tiny_gap", "tiny_gmp", "tiny: GAP - GMP"),
        ("plain2_w16_gap", "plain2_w16_gmp", "plain2_w16: GAP - GMP"),
        ("plain4_w16_gap", "plain4_w16_gmp", "plain4_w16: GAP - GMP"),
        ("plain2_w64_gap", "plain2_w64_gmp", "plain2_w64: GAP - GMP"),
        ("plain4_w64_gap", "plain4_w64_gmp", "plain4_w64: GAP - GMP"),
        ("res4_w16_gap", "res4_w16_gmp", "res4_w16: GAP - GMP"),
        ("bn2_w16_gap", "bn2_w16_gmp", "bn2_w16: GAP - GMP"),
        ("bn4_w16_gap", "bn4_w16_gmp", "bn4_w16: GAP - GMP"),
    ],
    "depth": [
        ("plain2_w16_gmp", "tiny_gmp", "GMP: plain2 - tiny"),
        ("plain2_w16_gap", "tiny_gap", "GAP: plain2 - tiny"),
        ("plain4_w16_gmp", "plain2_w16_gmp", "GMP: plain4 - plain2"),
        ("plain4_w16_gap", "plain2_w16_gap", "GAP: plain4 - plain2"),
    ],
    "width": [
        ("plain2_w64_gmp", "plain2_w16_gmp", "depth2 GMP: w64 - w16"),
        ("plain2_w64_gap", "plain2_w16_gap", "depth2 GAP: w64 - w16"),
        ("plain4_w64_gmp", "plain4_w16_gmp", "depth4 GMP: w64 - w16"),
        ("plain4_w64_gap", "plain4_w16_gap", "depth4 GAP: w64 - w16"),
    ],
    "residual": [
        ("res4_w16_gmp", "plain4_w16_gmp", "GMP: residual4 - plain4"),
        ("res4_w16_gap", "plain4_w16_gap", "GAP: residual4 - plain4"),
    ],
    "batchnorm": [
        ("bn2_w16_gmp", "plain2_w16_gmp", "depth2 GMP: BN - noBN"),
        ("bn2_w16_gap", "plain2_w16_gap", "depth2 GAP: BN - noBN"),
        ("bn4_w16_gmp", "plain4_w16_gmp", "depth4 GMP: BN - noBN"),
        ("bn4_w16_gap", "plain4_w16_gap", "depth4 GAP: BN - noBN"),
    ],
}


def factor_contrasts(b_block):
    rec = []
    per = []
    for task in ac.TASKS:
        for metric in ALL_METRICS:
            s = b_block[(b_block.task == task) & (b_block.metric == metric)]
            p = s.pivot(index="block", columns="architecture", values="B")
            for family, pairs in FACTOR_PAIRS.items():
                for alt, ref, label in pairs:
                    d = p[alt] - p[ref]
                    q = one_sample(d.to_numpy(float))
                    rec.append(
                        {
                            "task": task,
                            "metric": metric,
                            "family": family,
                            "contrast": label,
                            "alternative_architecture": alt,
                            "reference_architecture": ref,
                            **q,
                        }
                    )
                    per.extend(
                        {
                            "task": task,
                            "metric": metric,
                            "family": family,
                            "contrast": label,
                            "block": int(block),
                            "difference": float(value),
                        }
                        for block, value in d.items()
                        if np.isfinite(value)
                    )
    out = pd.DataFrame(rec)
    out["p_holm_within_factor_family"] = np.nan
    for _, idx in out.groupby(["task", "metric", "family"]).groups.items():
        idx = list(idx)
        out.loc[idx, "p_holm_within_factor_family"] = holm_adjust(
            out.loc[idx, "p_two_sided"].to_numpy(float)
        )
    return out, pd.DataFrame(per)


def initialization_dispersion(b_init):
    within = (
        b_init.groupby(["task", "architecture", "block", "metric"], as_index=False)
        .agg(init_sd=("B", "std"), init_mean=("B", "mean"), finite_reps=("B", "count"))
    )
    rec = []
    for keys, s in within.groupby(["task", "architecture", "metric"], sort=False):
        vals = s.init_sd.to_numpy(float)
        vals = vals[np.isfinite(vals)]
        rec.append(
            {
                "task": keys[0],
                "architecture": keys[1],
                "metric": keys[2],
                "n_blocks": len(vals),
                "mean_within_block_init_sd": float(vals.mean()) if len(vals) else np.nan,
                "median_within_block_init_sd": float(np.median(vals)) if len(vals) else np.nan,
                "max_within_block_init_sd": float(vals.max()) if len(vals) else np.nan,
            }
        )
    return pd.DataFrame(rec), within


def input_effect_contrasts(models):
    rec = []
    per = []
    id_cols = ["task", "architecture", "block", "init_rep"]
    for metric in INPUT_EFFECT_METRICS:
        p = models.pivot(index=id_cols, columns="treatment", values=metric).reset_index()
        p["delta"] = p["release_default"] - p["retention_1"]
        block = (
            p.groupby(["task", "architecture", "block"], as_index=False)
            .agg(delta=("delta", "mean"))
        )
        for keys, s in block.groupby(["task", "architecture"], sort=False):
            q = one_sample(s.delta.to_numpy(float))
            rec.append(
                {
                    "task": keys[0],
                    "architecture": keys[1],
                    "metric": metric,
                    **q,
                }
            )
        for _, r in block.iterrows():
            per.append(
                {
                    "task": r.task,
                    "architecture": r.architecture,
                    "block": int(r.block),
                    "metric": metric,
                    "delta": float(r.delta),
                }
            )
    return pd.DataFrame(rec), pd.DataFrame(per)


def control_summaries(rows):
    records = []
    for metric in CORE_CONTROL_METRICS:
        for control in ("random", "energy"):
            col = f"selected_minus_{control}_{metric}"
            if col not in rows:
                continue
            s0 = rows[rows[col].notna()]
            block = (
                s0.groupby(
                    ["task", "architecture", "treatment", "block", "k"], as_index=False
                )
                .agg(value=(col, "mean"))
            )
            for keys, s in block.groupby(
                ["task", "architecture", "treatment", "k"], sort=False
            ):
                q = interval(s.value.to_numpy(float))
                records.append(
                    {
                        "task": keys[0],
                        "architecture": keys[1],
                        "treatment": keys[2],
                        "k": int(keys[3]),
                        "metric": metric,
                        "control": control,
                        **q,
                    }
                )
    return pd.DataFrame(records)


def fmt_p(x):
    return "NA" if not np.isfinite(x) else f"{x:.3g}"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    root = Path(args.input).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows, models, matching, files = load_outputs(root)
    verify(rows, models, files)

    delta_init = treatment_deltas(rows)
    b_init = make_b(delta_init)
    delta_block = block_average_delta(delta_init)
    b_block = block_average_b(b_init)

    architecture_summary = summarize_architecture_b(b_block)
    curves = summarize_curves(delta_block)
    omnibus = primary_omnibus(b_block)
    bridge, bridge_per_block = bridge_contrasts(b_block)
    factors, factors_per_block = factor_contrasts(b_block)
    init_summary, init_per_block = initialization_dispersion(b_init)
    input_summary, input_per_block = input_effect_contrasts(models)
    controls = control_summaries(rows)

    architecture_summary.to_csv(out / "architecture_B_summary.csv", index=False)
    curves.to_csv(out / "treatment_delta_curves.csv", index=False)
    omnibus.to_csv(out / "primary_architecture_omnibus.csv", index=False)
    bridge.to_csv(out / "primary_bridge_contrast.csv", index=False)
    bridge_per_block.to_csv(out / "primary_bridge_contrast_per_block.csv", index=False)
    factors.to_csv(out / "architecture_factor_contrasts.csv", index=False)
    factors_per_block.to_csv(out / "architecture_factor_contrasts_per_block.csv", index=False)
    init_summary.to_csv(out / "initialization_dispersion_summary.csv", index=False)
    init_per_block.to_csv(out / "initialization_dispersion_per_block.csv", index=False)
    input_summary.to_csv(out / "input_effect_scale_contrasts.csv", index=False)
    input_per_block.to_csv(out / "input_effect_scale_contrasts_per_block.csv", index=False)
    controls.to_csv(out / "control_diagnostics.csv", index=False)

    # Compact model endpoint table is useful for training/performance diagnostics
    # without archiving the much larger raw per-k evaluator JSONs.
    models.to_csv(out / "model_endpoints.csv", index=False)

    max_full = float(models.full_patch_max_logit_error.max())
    max_noop = float(models.noop_max_logit_error.max())

    primary_arch = architecture_summary[
        (architecture_summary.task == PRIMARY_TASK)
        & (architecture_summary.metric.isin(PRIMARY_METRICS))
    ].copy()

    lines = [
        "# Stage-F architecture robustness analysis",
        "",
        "Status: prospectively frozen fresh-sample architecture study.",
        "",
        f"- evaluated models: **{len(models):,} / 25,600**",
        "- renderer blocks: **100**",
        "- initialization replicates per block/treatment/architecture/task: **4**",
        "- inferential unit: renderer block after averaging initialization replicates",
        "",
        "## Primary architecture-heterogeneity tests",
        "",
        "| Metric | F | df | partial eta^2 | p | Holm p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in omnibus.iterrows():
        lines.append(
            f"| {r.metric} | {r.F:.4f} | {int(r.df_architecture)}, {int(r.df_error)} | "
            f"{r.partial_eta_squared:.4f} | {fmt_p(r.p_two_sided_equivalent_upper_tail)} | "
            f"{fmt_p(r.p_holm_two_metric_family)} |"
        )

    lines += [
        "",
        "## Fresh-sample TinyCNN vs TwoLayer-form bridge",
        "",
        "| Metric | mean difference in B | 95% interval | p | Holm p |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, r in bridge.iterrows():
        lines.append(
            f"| {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | "
            f"{fmt_p(r.p_two_sided)} | {fmt_p(r.p_holm_two_metric_family)} |"
        )

    lines += [
        "",
        "## Primary two-concepts architecture estimates",
        "",
        "| Architecture | Metric | mean B | 95% interval |",
        "|---|---|---:|---:|",
    ]
    for _, r in primary_arch.sort_values(["metric", "architecture"]).iterrows():
        lines.append(
            f"| {r.architecture} | {r.metric} | {r['mean']:+.6f} | "
            f"[{r.ci_low:+.6f}, {r.ci_high:+.6f}] |"
        )

    lines += [
        "",
        "## Integrity",
        "",
        f"- maximum full-patch logit identity error: **{max_full:.6g}**",
        f"- maximum no-op logit identity error: **{max_noop:.6g}**",
        "",
        "Pooling, depth, width, residual, BatchNorm, single_shape, denominator-scale, initialization-dispersion, and control contrasts are retained in the CSV outputs. No binary pass/fail rule is defined.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")

    summary = {
        "study": "cnn_architecture_robustness_stage_f",
        "status": "prospectively_frozen_fresh_sample",
        "models": len(models),
        "renderer_blocks": 100,
        "init_reps": 4,
        "architectures": list(ac.ARCHS),
        "primary_task": PRIMARY_TASK,
        "primary_metrics": list(PRIMARY_METRICS),
        "maximum_full_patch_logit_error": max_full,
        "maximum_noop_logit_error": max_noop,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print("Stage-F analysis report:", out / "REPORT.md")


if __name__ == "__main__":
    main()
