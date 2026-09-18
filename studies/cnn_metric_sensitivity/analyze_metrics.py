"""Analyze the frozen checkpoint-only patching metric-sensitivity study.

This script does not train or evaluate models. It summarizes outputs produced by
evaluate_metrics.py according to PROTOCOL.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from scipy.stats import ttest_1samp

D_KS = (1, 2, 4, 8)
METHODS = ("contrast", "auroc", "validation_patch")
D_ARCHS = ("TinyCNN", "TwoLayerCNN")
D_CONDITIONS = ("template_retention_1", "template_release")
E_TASKS = ("single_shape", "two_concepts")
E_ARCHS = ("TinyCNN", "TwoLayerCNN")
E_PROFILES = (
    "template_init",
    "retention_0p1",
    "retention_1",
    "release_early",
    "release_default",
    "release_late",
)
PRIMARY_METRICS = ("centered_logit_fidelity", "prob_error_reduction")
SECONDARY_METRICS = (
    "prob_fidelity",
    "raw_logit_fidelity",
    "centered_logit_error_reduction",
    "raw_logit_error_reduction",
    "cf_accuracy",
    "agreement",
)
ALL_METRICS = PRIMARY_METRICS + SECONDARY_METRICS
INPUT_EFFECT_METRICS = (
    "prob_input_effect_mpp",
    "centered_logit_input_effect_mpp",
    "raw_logit_input_effect_mpp",
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_blob_for(path):
    try:
        root = Path(__file__).resolve().parents[2]
        rel = Path(path).resolve().relative_to(root)
        return subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{rel.as_posix()}"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip() or None
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


def git_commit_for(path):
    try:
        root = Path(__file__).resolve().parents[2]
        rel = Path(path).resolve().relative_to(root)
        return subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%H", "--", str(rel)],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip() or None
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


def interval(x):
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all():
        raise ValueError("Non-finite values in interval input")
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=1))
    err = float(student_t.ppf(0.975, n - 1) * sd / np.sqrt(n))
    return {"n": n, "mean": mean, "sd": sd, "ci_low": mean - err, "ci_high": mean + err}


def holm_adjust(values):
    p = np.asarray(values, dtype=float)
    order = np.argsort(p)
    out = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[idx]))
        out[idx] = running
    return out


def load_stage(root: Path, stage: str):
    if not (root / "EVAL_COMPLETE.json").exists():
        raise SystemExit(f"Metric evaluation is not complete: {root}")
    files = sorted((root / "runs").glob("*/*/block*/*/epoch_*.json"))
    expected = 80 if stage == "D" else 1200
    if len(files) != expected:
        raise SystemExit(f"{stage}: expected {expected} model outputs, found {len(files)}")

    rows, models = [], []
    id_key = "condition" if stage == "D" else "profile"
    for p in files:
        v = json.loads(p.read_text())
        ident = {
            "stage": stage,
            "task": v["task"],
            "architecture": v["architecture"],
            "block": int(v["block"]),
            id_key: v[id_key],
            "epoch": int(v["epoch"]),
        }
        models.append(
            {
                **ident,
                "pair_count": int(v["pair_count"]),
                "prob_input_effect_mpp": v["prob_input_effect_mpp"],
                "centered_logit_input_effect_mpp": v["centered_logit_input_effect_mpp"],
                "raw_logit_input_effect_mpp": v["raw_logit_input_effect_mpp"],
                "max_legacy_prob_fidelity_abs_diff": v["max_legacy_prob_fidelity_abs_diff"],
                "full_patch_max_logit_error": v["full_patch_max_logit_error"],
                "noop_max_logit_error": v["noop_max_logit_error"],
                "checkpoint_sha256": v["checkpoint_sha256"],
                "ranking_artifact_sha256": v["ranking_artifact_sha256"],
                "test_data_sha256": v["test_data_sha256"],
            }
        )
        for r in v["rows"]:
            rows.append({**ident, **r})
    return pd.DataFrame(rows), pd.DataFrame(models), files


def verify_stage_d(rows, models):
    assert set(rows.task) == {"two_concepts"}
    assert set(rows.architecture) == set(D_ARCHS)
    assert set(rows.condition) == set(D_CONDITIONS)
    assert set(rows.block) == set(range(4000, 4020))
    assert set(rows.method) == set(METHODS)
    assert set(rows.k) == set(D_KS)
    assert len(models) == 80
    assert not rows.duplicated(["architecture", "block", "condition", "method", "k"]).any()
    assert len(rows) == 2 * 20 * 2 * 3 * 4
    primary = rows[(rows.architecture == "TinyCNN") & (rows.method == "contrast")]
    assert primary.selection_valid.all()
    for metric in ALL_METRICS:
        assert primary[metric].notna().all(), metric


def verify_stage_e(rows, models):
    assert set(rows.task) == set(E_TASKS)
    assert set(rows.architecture) == set(E_ARCHS)
    assert set(rows.profile) == set(E_PROFILES)
    assert set(rows.block) == set(range(5000, 5050))
    assert set(rows.method) == set(METHODS)
    assert set(rows.k) == set(range(1, 17))
    assert len(models) == 1200
    assert not rows.duplicated(["task", "architecture", "block", "profile", "method", "k"]).any()
    assert len(rows) == 2 * 2 * 50 * 6 * 3 * 16


def paired_summary(delta, keys, metric):
    rec = []
    for group_keys, s in delta.groupby(keys, sort=False):
        if not isinstance(group_keys, tuple):
            group_keys = (group_keys,)
        q = interval(s["delta"].to_numpy(float))
        rec.append({**dict(zip(keys, group_keys)), "metric": metric, **q})
    return pd.DataFrame(rec)


def stage_d_treatment(rows, metric):
    per = []
    for arch in D_ARCHS:
        for method in METHODS:
            s = rows[(rows.architecture == arch) & (rows.method == method)]
            for k in D_KS:
                a = s[(s.condition == "template_release") & (s.k == k)].set_index("block")[metric]
                b = s[(s.condition == "template_retention_1") & (s.k == k)].set_index("block")[metric]
                d = (a - b).sort_index()
                assert len(d) == 20
                per.extend(
                    {
                        "architecture": arch,
                        "method": method,
                        "k": k,
                        "metric": metric,
                        "block": int(block),
                        "delta": float(value),
                    }
                    for block, value in d.items()
                )
    per = pd.DataFrame(per)
    summary = paired_summary(per, ["architecture", "method", "k"], metric)
    return summary, per


def budget_from_per_block(per_block, stage):
    rec, vals = [], []
    group_cols = ["architecture", "method", "metric"] if stage == "D" else ["task", "architecture", "profile", "method", "metric"]
    for keys, s in per_block.groupby(group_cols, sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        ident = dict(zip(group_cols, keys))
        p = s[s.k.isin(D_KS)].pivot(index="block", columns="k", values="delta").sort_index()
        expected_n = 20 if stage == "D" else 50
        assert len(p) == expected_n and all(k in p for k in D_KS)
        B = p[[4, 8]].mean(axis=1) - p[[1, 2]].mean(axis=1)
        q = interval(B.to_numpy(float))
        test = ttest_1samp(B.to_numpy(float), 0.0)
        rec.append({**ident, "t_stat": float(test.statistic), "p_two_sided": float(test.pvalue), **q})
        vals.extend({**ident, "block": int(block), "B": float(value)} for block, value in B.items())
    return pd.DataFrame(rec), pd.DataFrame(vals)


def stage_d_input_effect(models):
    rec, per = [], []
    for arch in D_ARCHS:
        s = models[models.architecture == arch]
        for metric in INPUT_EFFECT_METRICS:
            a = s[s.condition == "template_release"].set_index("block")[metric]
            b = s[s.condition == "template_retention_1"].set_index("block")[metric]
            d = (a - b).sort_index()
            q = interval(d.to_numpy(float))
            test = ttest_1samp(d.to_numpy(float), 0.0)
            rec.append(
                {
                    "architecture": arch,
                    "metric": metric,
                    "t_stat": float(test.statistic),
                    "p_two_sided": float(test.pvalue),
                    **q,
                }
            )
            per.extend(
                {"architecture": arch, "metric": metric, "block": int(block), "delta": float(value)}
                for block, value in d.items()
            )
    return pd.DataFrame(rec), pd.DataFrame(per)


def stage_e_pairwise(rows, metric):
    per = []
    for task in E_TASKS:
        for arch in E_ARCHS:
            for method in METHODS:
                s = rows[(rows.task == task) & (rows.architecture == arch) & (rows.method == method)]
                ref = s[s.profile == "retention_1"]
                for profile in E_PROFILES:
                    if profile == "retention_1":
                        continue
                    cur = s[s.profile == profile]
                    for k in range(1, 17):
                        a = cur[cur.k == k].set_index("block")[metric]
                        b = ref[ref.k == k].set_index("block")[metric]
                        d = (a - b).sort_index()
                        assert len(d) == 50
                        per.extend(
                            {
                                "task": task,
                                "architecture": arch,
                                "profile": profile,
                                "method": method,
                                "k": k,
                                "metric": metric,
                                "block": int(block),
                                "delta": float(value),
                            }
                            for block, value in d.items()
                        )
    per = pd.DataFrame(per)
    summary = paired_summary(per, ["task", "architecture", "profile", "method", "k"], metric)
    return summary, per


def add_holm_stage_e(B):
    B = B.copy()
    B["p_holm_within_setting"] = np.nan
    for _, idx in B.groupby(["task", "architecture", "method", "metric"]).groups.items():
        idx = list(idx)
        B.loc[idx, "p_holm_within_setting"] = holm_adjust(B.loc[idx, "p_two_sided"].to_numpy(float))
    return B


def summarize_stage_e_curves(rows):
    rec = []
    for keys, s in rows.groupby(["task", "architecture", "profile", "method", "k"], sort=False):
        task, arch, profile, method, k = keys
        for metric in ("prob_fidelity", "centered_logit_fidelity", "prob_error_reduction"):
            q = interval(s[metric].to_numpy(float))
            rec.append(
                {
                    "task": task,
                    "architecture": arch,
                    "profile": profile,
                    "method": method,
                    "k": int(k),
                    "metric": metric,
                    **q,
                }
            )
    return pd.DataFrame(rec)


def fmt_p(x):
    return f"{x:.3g}"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage-d", required=True, help="Stage-D metric evaluator output directory")
    p.add_argument("--stage-e", required=True, help="Stage-E metric evaluator output directory")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    droot = Path(args.stage_d).resolve()
    eroot = Path(args.stage_e).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    protocol = Path(__file__).with_name("PROTOCOL.md")
    protocol_blob = git_blob_for(protocol)
    protocol_commit = git_commit_for(protocol)
    analysis_blob = git_blob_for(Path(__file__))

    drows, dmodels, dfiles = load_stage(droot, "D")
    erows, emodels, efiles = load_stage(eroot, "E")
    verify_stage_d(drows, dmodels)
    verify_stage_e(erows, emodels)

    drows.to_csv(out / "stage_d_model_metric_rows.csv", index=False)
    dmodels.to_csv(out / "stage_d_model_integrity.csv", index=False)
    erows.to_csv(out / "stage_e_model_metric_rows.csv", index=False)
    emodels.to_csv(out / "stage_e_model_integrity.csv", index=False)

    d_summaries, d_blocks = [], []
    for metric in ALL_METRICS:
        q, b = stage_d_treatment(drows, metric)
        d_summaries.append(q)
        d_blocks.append(b)
    d_summary = pd.concat(d_summaries, ignore_index=True)
    d_block = pd.concat(d_blocks, ignore_index=True)
    d_B, d_Bblock = budget_from_per_block(d_block, "D")

    primary = d_B[
        (d_B.architecture == "TinyCNN")
        & (d_B.method == "contrast")
        & (d_B.metric.isin(PRIMARY_METRICS))
    ].copy()
    assert len(primary) == 2
    primary["p_holm_two_metric_family"] = holm_adjust(primary.p_two_sided.to_numpy(float))

    denom, denom_block = stage_d_input_effect(dmodels)

    d_summary.to_csv(out / "stage_d_treatment_contrasts.csv", index=False)
    d_block.to_csv(out / "stage_d_treatment_contrasts_per_block.csv", index=False)
    d_B.to_csv(out / "stage_d_budget_contrasts_B.csv", index=False)
    d_Bblock.to_csv(out / "stage_d_budget_contrasts_B_per_block.csv", index=False)
    primary.to_csv(out / "stage_d_primary_metric_robustness.csv", index=False)
    denom.to_csv(out / "stage_d_input_effect_scale_contrasts.csv", index=False)
    denom_block.to_csv(out / "stage_d_input_effect_scale_contrasts_per_block.csv", index=False)

    e_summaries, e_blocks = [], []
    for metric in ALL_METRICS:
        q, b = stage_e_pairwise(erows, metric)
        e_summaries.append(q)
        e_blocks.append(b)
    e_summary = pd.concat(e_summaries, ignore_index=True)
    e_block = pd.concat(e_blocks, ignore_index=True)
    e_B, e_Bblock = budget_from_per_block(e_block, "E")
    e_B = add_holm_stage_e(e_B)
    e_curves = summarize_stage_e_curves(erows)

    e_summary.to_csv(out / "stage_e_profile_contrasts.csv", index=False)
    e_block.to_csv(out / "stage_e_profile_contrasts_per_block.csv", index=False)
    e_B.to_csv(out / "stage_e_budget_contrasts_B.csv", index=False)
    e_Bblock.to_csv(out / "stage_e_budget_contrasts_B_per_block.csv", index=False)
    e_curves.to_csv(out / "stage_e_metric_curves.csv", index=False)

    max_legacy = max(
        float(dmodels.max_legacy_prob_fidelity_abs_diff.max()),
        float(emodels.max_legacy_prob_fidelity_abs_diff.max()),
    )
    max_full = max(
        float(dmodels.full_patch_max_logit_error.max()),
        float(emodels.full_patch_max_logit_error.max()),
    )
    max_noop = max(
        float(dmodels.noop_max_logit_error.max()),
        float(emodels.noop_max_logit_error.max()),
    )

    primary_curve = d_summary[
        (d_summary.architecture == "TinyCNN")
        & (d_summary.method == "contrast")
        & (d_summary.metric.isin(PRIMARY_METRICS))
    ].copy()

    default_e = e_B[
        (e_B.profile == "release_default")
        & (e_B.method == "contrast")
        & (e_B.metric.isin(PRIMARY_METRICS))
    ].copy()

    lines = [
        "# Patching metric-sensitivity analysis",
        "",
        "Statistical status: frozen post hoc robustness analysis of saved Stage-D/E checkpoints. No model was retrained and no stored channel ranking was changed.",
        "",
        f"- protocol commit: {protocol_commit or 'unavailable'}",
        f"- protocol Git blob: {protocol_blob or 'unavailable'}",
        f"- analysis Git blob: {analysis_blob or 'unavailable'}",
        f"- Stage-D checkpoint evaluations: **{len(dfiles)} / 80**",
        f"- Stage-E checkpoint evaluations: **{len(efiles)} / 1200**",
        "",
        "## Stage-D primary metric-sensitivity setting",
        "",
        "Setting: two_concepts / TinyCNN / contrast, with the original release-minus-retention treatment pairing and B contrast.",
        "",
        "| Metric | mean B | 95% interval | p | Holm p (2 metrics) |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, r in primary.iterrows():
        lines.append(
            f"| {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | {fmt_p(r.p_two_sided)} | {fmt_p(r.p_holm_two_metric_family)} |"
        )

    lines += [
        "",
        "### Pointwise release-minus-retention contrasts",
        "",
        "| Metric | k | mean delta | 95% interval |",
        "|---|---:|---:|---:|",
    ]
    for _, r in primary_curve.sort_values(["metric", "k"]).iterrows():
        lines.append(f"| {r.metric} | {int(r.k)} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] |")

    lines += [
        "",
        "## Stage-D input-effect normalization diagnostics",
        "",
        "These are release-minus-retention differences in the model-level base-to-counterfactual squared-error scale used as the denominator of normalized metrics.",
        "",
        "| Architecture | Input-effect scale | mean delta | 95% interval | p |",
        "|---|---|---:|---:|---:|",
    ]
    for _, r in denom.iterrows():
        lines.append(
            f"| {r.architecture} | {r.metric} | {r['mean']:+.6g} | [{r.ci_low:+.6g}, {r.ci_high:+.6g}] | {fmt_p(r.p_two_sided)} |"
        )

    lines += [
        "",
        "## Stage-E default-release extension",
        "",
        "Secondary B contrasts for release_default - retention_1 under the original contrast ranking.",
        "",
        "| Task | Architecture | Metric | mean B | 95% interval | Holm p within Stage-E setting |",
        "|---|---|---|---:|---:|---:|",
    ]
    for _, r in default_e.sort_values(["task", "architecture", "metric"]).iterrows():
        lines.append(
            f"| {r.task} | {r.architecture} | {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | {fmt_p(r.p_holm_within_setting)} |"
        )

    lines += [
        "",
        "## Integrity",
        "",
        f"- maximum absolute difference between recomputed and stored probability fidelity: **{max_legacy:.6g}**",
        f"- maximum full-patch logit identity error: **{max_full:.6g}**",
        f"- maximum no-op logit identity error: **{max_noop:.6g}**",
        "",
        "Raw-logit fidelity, alternative rankings, architecture results, all Stage-E profiles, full k curves, and block-level values are retained in the CSV files. No binary pass/fail decision is defined by the frozen protocol.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")

    summary = {
        "status": "post_hoc_frozen_metric_sensitivity",
        "training_invoked": False,
        "protocol_commit": protocol_commit,
        "protocol_git_blob": protocol_blob,
        "analysis_git_blob": analysis_blob,
        "stage_d_models": len(dfiles),
        "stage_e_models": len(efiles),
        "primary_metrics": list(PRIMARY_METRICS),
        "maximum_legacy_probability_fidelity_abs_diff": max_legacy,
        "maximum_full_patch_logit_error": max_full,
        "maximum_noop_logit_error": max_noop,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Metric-sensitivity report:", out / "REPORT.md")


if __name__ == "__main__":
    main()
