"""Analyze the prospectively frozen Stage-G anchor-specificity experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist
from scipy.stats import spearmanr
from scipy.stats import t as student_t
from scipy.stats import ttest_1samp

import sys
sys.path.append(str(Path(__file__).resolve().parent))
import anchor_core as ac  # noqa: E402

PRIMARY_TASK = "two_concepts"
PRIMARY_METRICS = ("centered_logit_fidelity", "prob_error_reduction")
BUDGETS = (1, 2, 4, 8)
N_PERM = 100_000
PERM_SEED = 20260920
# Frozen before Stage-G outcomes. Each margin is 20% of the historical Stage-F
# mean absolute B across the same four diagnostic architectures.
EQUIVALENCE_MARGINS = {
    "centered_logit_fidelity": 0.017040331170505053,
    "prob_error_reduction": 0.06593636028899892,
}


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
    z = ttest_1samp(x, 0.0)
    return {**q, "t_stat": float(z.statistic), "p_two_sided": float(z.pvalue)}


def equivalence_tost(x, margin, alpha=0.05):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return {
            "equivalence_margin": float(margin),
            "equivalence_ci90_low": np.nan,
            "equivalence_ci90_high": np.nan,
            "equivalence_p_lower": np.nan,
            "equivalence_p_upper": np.nan,
            "equivalence_p_tost": np.nan,
            "equivalent_at_alpha_0_05": False,
        }
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=1))
    se = sd / np.sqrt(n)
    crit = float(student_t.ppf(1.0 - alpha, n - 1))
    ci_low = mean - crit * se
    ci_high = mean + crit * se
    if se == 0:
        p_lower = 0.0 if mean > -margin else 1.0
        p_upper = 0.0 if mean < margin else 1.0
    else:
        t_lower = (mean + margin) / se
        t_upper = (mean - margin) / se
        p_lower = float(student_t.sf(t_lower, n - 1))
        p_upper = float(student_t.cdf(t_upper, n - 1))
    p_tost = max(p_lower, p_upper)
    return {
        "equivalence_margin": float(margin),
        "equivalence_ci90_low": float(ci_low),
        "equivalence_ci90_high": float(ci_high),
        "equivalence_p_lower": float(p_lower),
        "equivalence_p_upper": float(p_upper),
        "equivalence_p_tost": float(p_tost),
        "equivalent_at_alpha_0_05": bool(p_tost < alpha),
    }


def holm_adjust(values):
    p = np.asarray(values, dtype=float)
    out = np.full_like(p, np.nan)
    good = np.isfinite(p)
    ids = np.flatnonzero(good)
    pv = p[good]
    if not len(pv):
        return out
    order = np.argsort(pv)
    running = 0.0
    adjusted = np.empty(len(pv), dtype=float)
    for rank, pos in enumerate(order):
        running = max(running, min(1.0, (len(pv) - rank) * pv[pos]))
        adjusted[pos] = running
    out[ids] = adjusted
    return out


def signflip_p(x, n_perm=N_PERM, seed=PERM_SEED):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    observed = abs(float(x.mean()))
    rng = np.random.default_rng(seed)
    extreme = 0
    remaining = n_perm
    while remaining:
        m = min(5000, remaining)
        signs = rng.choice((-1.0, 1.0), size=(m, len(x)))
        means = np.abs((signs * x[None, :]).mean(axis=1))
        extreme += int((means >= observed - 1e-15).sum())
        remaining -= m
    return (extreme + 1) / (n_perm + 1)


def repeated_measures_f(y):
    y = np.asarray(y, dtype=float)
    if not np.isfinite(y).all():
        raise ValueError("Complete finite matrix required")
    n, a = y.shape
    grand = y.mean()
    arch_mean = y.mean(axis=0)
    block_mean = y.mean(axis=1)
    ss_total = float(((y - grand) ** 2).sum())
    ss_arch = float(n * ((arch_mean - grand) ** 2).sum())
    ss_block = float(a * ((block_mean - grand) ** 2).sum())
    ss_error = max(0.0, ss_total - ss_arch - ss_block)
    df1 = a - 1
    df2 = (a - 1) * (n - 1)
    F = (ss_arch / df1) / (ss_error / df2) if ss_error > 0 else np.inf
    return {
        "F": float(F),
        "df1": int(df1),
        "df2": int(df2),
        "partial_eta_squared": float(ss_arch / (ss_arch + ss_error)) if ss_arch + ss_error > 0 else 0.0,
    }


def permutation_architecture_p(y, n_perm=N_PERM, seed=PERM_SEED):
    y = np.asarray(y, dtype=float)
    observed = repeated_measures_f(y)["F"]
    n, a = y.shape
    grand = y.mean()
    block_mean = y.mean(axis=1)
    ss_total = float(((y - grand) ** 2).sum())
    ss_block = float(a * ((block_mean - grand) ** 2).sum())
    df1 = a - 1
    df2 = (a - 1) * (n - 1)

    rng = np.random.default_rng(seed)
    extreme = 0
    remaining = n_perm
    while remaining:
        m = min(500, remaining)
        keys = rng.random((m, n, a))
        perm = np.argsort(keys, axis=2)
        yp = np.take_along_axis(np.broadcast_to(y, (m, n, a)), perm, axis=2)
        means = yp.mean(axis=1)
        ss_arch = n * ((means - grand) ** 2).sum(axis=1)
        ss_error = np.maximum(0.0, ss_total - ss_block - ss_arch)
        F = (ss_arch / df1) / (ss_error / df2)
        extreme += int((F >= observed - 1e-14).sum())
        remaining -= m
    return (extreme + 1) / (n_perm + 1)


def load_outputs(root: Path):
    files = sorted((root / "runs").glob("*/*/*/block*/init*/*/epoch_*.json"))
    if not (root / "GRID_COMPLETE.json").exists():
        raise SystemExit(f"Stage-G evaluation is not marked complete: {root}")
    rows, models, anchor_checks = [], [], []
    for path in files:
        v = json.loads(path.read_text())
        ident = {
            "task": v["task"],
            "architecture": v["architecture"],
            "anchor_family": v["anchor_family"],
            "block": int(v["block"]),
            "init_rep": int(v["init_rep"]),
            "treatment": v["treatment"],
        }
        models.append({
            **ident,
            "test_acc": v["test_acc"],
            "own_anchor_alignment": v["own_anchor_alignment"],
            "structured_template_alignment": v["structured_template_alignment"],
            "full_patch_max_logit_error": v["full_patch_max_logit_error"],
            "noop_max_logit_error": v["noop_max_logit_error"],
        })
        diag = v["anchor_diagnostics"]
        anchor_checks.append({
            **ident,
            "anchor_rank": diag["rank"],
            "anchor_max_abs_row_mean": diag["max_abs_row_mean"],
            "anchor_max_abs_row_norm_error": diag["max_abs_row_norm_error"],
            "anchor_max_abs_gram_error_vs_structured": diag.get("max_abs_gram_error_vs_structured", np.nan),
            "anchor_sha256": diag["bank_sha256"],
        })
        for r in v["rows"]:
            rows.append({**ident, **r})
    return pd.DataFrame(rows), pd.DataFrame(models), pd.DataFrame(anchor_checks), files


def verify(rows, models, checks, files):
    assert len(files) == 25600, len(files)
    assert len(models) == 25600
    assert set(rows.task) == set(ac.TASKS)
    assert set(rows.architecture) == set(ac.ARCHS)
    assert set(rows.anchor_family) == set(ac.ANCHORS)
    assert set(rows.treatment) == set(ac.TREATMENTS)
    assert set(rows.block) == set(range(7000, 7100))
    assert set(rows.init_rep) == {0,1,2,3}
    assert set(rows.k) == set(range(1,17))
    assert len(rows) == 25600 * 16
    assert not rows.duplicated(
        ["task","architecture","anchor_family","block","init_rep","treatment","k"]
    ).any()
    if checks.anchor_max_abs_row_mean.max() > 2e-6:
        raise ValueError("Anchor centering invariant failed")
    if checks.anchor_max_abs_row_norm_error.max() > 2e-6:
        raise ValueError("Anchor norm invariant failed")
    px = checks[checks.anchor_family == "pixel_permuted_template"]
    if px.anchor_max_abs_gram_error_vs_structured.max() > 5e-6:
        raise ValueError("Pixel-permuted Gram invariant failed")
    for metric in PRIMARY_METRICS:
        if not rows[rows.task == PRIMARY_TASK][metric].notna().all():
            raise ValueError(f"Undefined primary metric: {metric}")
        if not rows[rows.task == PRIMARY_TASK][f"random_{metric}"].notna().all():
            raise ValueError(f"Undefined random primary metric: {metric}")


def make_b(rows, value_kind):
    out = []
    id_cols = ["task","architecture","anchor_family","block","init_rep","k"]
    for metric in PRIMARY_METRICS:
        col = metric if value_kind == "selected" else f"random_{metric}"
        p = rows.pivot(index=id_cols, columns="treatment", values=col).reset_index()
        p["delta"] = p["release_default"] - p["retention_1"]
        p["metric"] = metric
        sub = p[p.k.isin(BUDGETS)]
        q = sub.pivot(
            index=["task","architecture","anchor_family","block","init_rep","metric"],
            columns="k", values="delta"
        ).reset_index()
        q["B"] = (q[4] + q[8]) / 2 - (q[1] + q[2]) / 2
        q["value_kind"] = value_kind
        out.append(q[["task","architecture","anchor_family","block","init_rep","metric","value_kind","B"]])
    init = pd.concat(out, ignore_index=True)
    block = (
        init.groupby(["task","architecture","anchor_family","block","metric","value_kind"], as_index=False)
        .agg(B=("B","mean"), init_reps=("B","count"))
    )
    return init, block


def spatial_contrasts(block_b, value_kind):
    rec, per = [], []
    sub = block_b[(block_b.task == PRIMARY_TASK) & (block_b.value_kind == value_kind)]
    for metric in PRIMARY_METRICS:
        s = sub[sub.metric == metric]
        p = s.pivot(index="block", columns=["architecture","anchor_family"], values="B")
        structured = p.xs("structured_template", level="anchor_family", axis=1).reindex(columns=ac.ARCHS)
        permuted = p.xs("pixel_permuted_template", level="anchor_family", axis=1).reindex(columns=ac.ARCHS)
        d = (structured - permuted).mean(axis=1)
        values = d.to_numpy(float)
        q = one_sample(values)
        q["p_signflip"] = signflip_p(values, seed=PERM_SEED + PRIMARY_METRICS.index(metric) + (100 if value_kind=="random" else 0))
        eq = equivalence_tost(values, EQUIVALENCE_MARGINS[metric])
        rec.append({
            "task": PRIMARY_TASK,
            "metric": metric,
            "value_kind": value_kind,
            "contrast": "structured - pixel_permuted averaged over architectures",
            **q,
            **eq,
        })
        per.extend({
            "task": PRIMARY_TASK, "metric": metric, "value_kind": value_kind,
            "block": int(b), "difference": float(v)
        } for b,v in d.items())
    out = pd.DataFrame(rec)
    if value_kind == "selected":
        out["p_holm_two_metric_family"] = holm_adjust(out.p_signflip.to_numpy(float))
        out["equivalence_p_tost_holm_two_metric_family"] = holm_adjust(
            out.equivalence_p_tost.to_numpy(float)
        )
    return out, pd.DataFrame(per)


def spatial_interaction(block_b, value_kind):
    rec = []
    sub = block_b[(block_b.task == PRIMARY_TASK) & (block_b.value_kind == value_kind)]
    for metric in PRIMARY_METRICS:
        s = sub[sub.metric == metric]
        p = s.pivot(index="block", columns=["architecture","anchor_family"], values="B")
        structured = p.xs("structured_template", level="anchor_family", axis=1).reindex(columns=ac.ARCHS)
        permuted = p.xs("pixel_permuted_template", level="anchor_family", axis=1).reindex(columns=ac.ARCHS)
        matrix = (structured - permuted).to_numpy(float)
        stat = repeated_measures_f(matrix)
        pperm = permutation_architecture_p(
            matrix,
            seed=PERM_SEED + 20 + PRIMARY_METRICS.index(metric) + (100 if value_kind=="random" else 0),
        )
        rec.append({
            "task": PRIMARY_TASK, "metric": metric, "value_kind": value_kind,
            "contrast": "(structured - pixel_permuted) x architecture",
            **stat, "p_permutation": pperm,
        })
    out = pd.DataFrame(rec)
    if value_kind == "selected":
        out["p_holm_two_metric_family"] = holm_adjust(out.p_permutation.to_numpy(float))
    return out


def secondary_anchor_contrasts(block_b):
    pairs = (
        ("structured_template","pixel_permuted_template","structured - pixel_permuted"),
        ("pixel_permuted_template","random_rank10","pixel_permuted - random_rank10"),
        ("random_rank10","random_fullrank","random_rank10 - random_fullrank"),
        ("structured_template","random_fullrank","structured - random_fullrank"),
    )
    rec, per = [], []
    selected = block_b[block_b.value_kind == "selected"]
    for task in ac.TASKS:
        for metric in PRIMARY_METRICS:
            s = selected[(selected.task==task)&(selected.metric==metric)]
            p = s.pivot(index=["block","architecture"], columns="anchor_family", values="B")
            for alt, ref, label in pairs:
                d = (p[alt] - p[ref]).rename("difference").reset_index()
                for arch, a in d.groupby("architecture", sort=False):
                    q = one_sample(a.difference.to_numpy(float))
                    rec.append({"task":task,"metric":metric,"contrast":label,"architecture":arch,**q})
                per.extend({
                    "task":task,"metric":metric,"contrast":label,
                    "block":int(r.block),"architecture":r.architecture,
                    "difference":float(r.difference),
                } for _,r in d.iterrows())
    out = pd.DataFrame(rec)
    out["p_holm_within_task_metric_contrast"] = np.nan
    for _, idx in out.groupby(["task","metric","contrast"]).groups.items():
        idx = list(idx)
        out.loc[idx,"p_holm_within_task_metric_contrast"] = holm_adjust(out.loc[idx,"p_two_sided"].to_numpy(float))
    return out, pd.DataFrame(per)


def structural_summaries(models):
    rec = []
    for metric in ("own_anchor_alignment","structured_template_alignment","test_acc"):
        p = models.pivot(
            index=["task","architecture","anchor_family","block","init_rep"],
            columns="treatment", values=metric
        ).reset_index()
        p["retention_minus_release"] = p["retention_1"] - p["release_default"]
        block = p.groupby(["task","architecture","anchor_family","block"], as_index=False).agg(
            retention=("retention_1","mean"),
            release=("release_default","mean"),
            retention_minus_release=("retention_minus_release","mean"),
        )
        for keys, s in block.groupby(["task","architecture","anchor_family"], sort=False):
            q = interval(s.retention_minus_release.to_numpy(float))
            rec.append({
                "task":keys[0],"architecture":keys[1],"anchor_family":keys[2],
                "quantity":metric,
                "retention_mean":float(s.retention.mean()),
                "release_mean":float(s.release.mean()),
                **{f"delta_{k}":v for k,v in q.items()},
            })
    return pd.DataFrame(rec)


def architecture_anchor_summary(block_b):
    rec = []
    for keys, s in block_b.groupby(["task","architecture","anchor_family","metric","value_kind"], sort=False):
        q = interval(s.B.to_numpy(float))
        rec.append({
            "task":keys[0],"architecture":keys[1],"anchor_family":keys[2],
            "metric":keys[3],"value_kind":keys[4],**q,
        })
    return pd.DataFrame(rec)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    root = Path(args.input).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows, models, checks, files = load_outputs(root)
    verify(rows, models, checks, files)

    selected_init, selected_block = make_b(rows, "selected")
    random_init, random_block = make_b(rows, "random")
    b_block = pd.concat([selected_block, random_block], ignore_index=True)

    spatial_selected, spatial_selected_per = spatial_contrasts(b_block, "selected")
    interaction_selected = spatial_interaction(b_block, "selected")
    spatial_random, spatial_random_per = spatial_contrasts(b_block, "random")
    interaction_random = spatial_interaction(b_block, "random")
    secondary, secondary_per = secondary_anchor_contrasts(b_block)
    structural = structural_summaries(models)
    summary = architecture_anchor_summary(b_block)

    selected_block.to_csv(out / "selected_B_per_block.csv", index=False)
    random_block.to_csv(out / "random_B_per_block.csv", index=False)
    summary.to_csv(out / "anchor_architecture_B_summary.csv", index=False)
    spatial_selected.to_csv(out / "primary_spatial_specificity.csv", index=False)
    spatial_selected_per.to_csv(out / "primary_spatial_specificity_per_block.csv", index=False)
    interaction_selected.to_csv(out / "primary_spatial_architecture_interaction.csv", index=False)
    spatial_random.to_csv(out / "random_channel_spatial_specificity.csv", index=False)
    spatial_random_per.to_csv(out / "random_channel_spatial_specificity_per_block.csv", index=False)
    interaction_random.to_csv(out / "random_channel_spatial_architecture_interaction.csv", index=False)
    secondary.to_csv(out / "secondary_anchor_contrasts.csv", index=False)
    secondary_per.to_csv(out / "secondary_anchor_contrasts_per_block.csv", index=False)
    structural.to_csv(out / "structural_endpoint_summary.csv", index=False)
    checks.drop_duplicates(["anchor_family","block","init_rep"]).to_csv(out / "anchor_integrity.csv", index=False)

    max_full = float(models.full_patch_max_logit_error.max())
    max_noop = float(models.noop_max_logit_error.max())
    lines = [
        "# Anchor-specificity analysis",
        "",
        "Status: prospectively frozen fresh-sample specificity experiment.",
        "",
        f"- evaluated models: **{len(models):,} / 25,600**",
        "- renderer blocks: **100**",
        "- init/anchor replicates averaged within block: **4**",
        "- primary task: **two_concepts**",
        "",
        "## Primary spatial-template specificity",
        "",
        "| Metric | mean structured-pixelperm B | 95% CI | sign-flip Holm p | equivalence margin | 90% CI | equivalence Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in spatial_selected.iterrows():
        lines.append(
            f"| {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | "
            f"{r.p_holm_two_metric_family:.3g} | {r.equivalence_margin:.6f} | "
            f"[{r.equivalence_ci90_low:+.6f}, {r.equivalence_ci90_high:+.6f}] | "
            f"{r.equivalence_p_tost_holm_two_metric_family:.3g} |"
        )
    lines += [
        "",
        "## Spatial-structure x architecture interaction",
        "",
        "| Metric | F | partial eta^2 | permutation p | Holm p |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, r in interaction_selected.iterrows():
        lines.append(
            f"| {r.metric} | {r.F:.4f} | {r.partial_eta_squared:.4f} | "
            f"{r.p_permutation:.3g} | {r.p_holm_two_metric_family:.3g} |"
        )
    lines += [
        "",
        "## Prespecified random-channel diagnostic",
        "",
        "| Metric | mean structured-pixelperm random-B | 95% CI | sign-flip p |",
        "|---|---:|---:|---:|",
    ]
    for _, r in spatial_random.iterrows():
        lines.append(
            f"| {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | {r.p_signflip:.3g} |"
        )
    lines += [
        "",
        "## Integrity",
        "",
        f"- maximum full-patch logit error: **{max_full:.6g}**",
        f"- maximum no-op logit error: **{max_noop:.6g}**",
        f"- maximum pixel-permuted Gram error: **{checks.anchor_max_abs_gram_error_vs_structured.max(skipna=True):.6g}**",
        "",
        "Interpretation rule: a nonzero difference test supports spatial-structure sensitivity; equivalence requires the frozen TOST margin; if neither criterion is met, the result is inconclusive rather than evidence of no difference.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")

    (out / "summary.json").write_text(json.dumps({
        "study":"cnn_anchor_specificity_stage_g",
        "status":"prospectively_frozen_fresh_sample",
        "models":len(models),
        "blocks":100,
        "init_reps":4,
        "architectures":list(ac.ARCHS),
        "anchors":list(ac.ANCHORS),
        "primary_task":PRIMARY_TASK,
        "primary_metrics":list(PRIMARY_METRICS),
        "permutations":N_PERM,
        "max_full_patch_logit_error":max_full,
        "max_noop_logit_error":max_noop,
    }, indent=2) + "\n")

    print("Anchor-specificity report:", out / "REPORT.md")


if __name__ == "__main__":
    main()
