"""Post hoc robustness diagnostics for the completed architecture study.

This analysis is outcome-informed by design. Read PROTOCOL.md before use.
No model retraining occurs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import f as f_dist
from scipy.stats import friedmanchisquare, spearmanr
from scipy.stats import t as student_t
from scipy.stats import ttest_1samp

import sys
STAGE_F = Path(__file__).resolve().parents[1] / "cnn_architecture_robustness"
sys.path.append(str(STAGE_F))
import architecture_core as ac  # noqa: E402

PRIMARY_TASK = "two_concepts"
PRIMARY_METRICS = ("centered_logit_fidelity", "prob_error_reduction")
BUDGETS = (1, 2, 4, 8)
N_PERM = 100_000
PERM_SEED = 20260920
BOOTSTRAPS = 5000


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
    adj = np.empty(len(pv), dtype=float)
    for rank, pos in enumerate(order):
        running = max(running, min(1.0, (len(pv) - rank) * pv[pos]))
        adj[pos] = running
    out[ids] = adj
    return out


def rm_anova(y):
    y = np.asarray(y, dtype=float)
    if not np.isfinite(y).all():
        raise ValueError("Complete matrix required")
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
    p = 0.0 if np.isinf(F) else float(f_dist.sf(F, df1, df2))
    return {
        "F": float(F), "df1": int(df1), "df2": int(df2), "p_uncorrected": p,
        "partial_eta_squared": float(ss_arch / (ss_arch + ss_error)) if ss_arch + ss_error > 0 else 0.0,
        "ss_arch": ss_arch, "ss_error": ss_error,
    }


def greenhouse_geisser(y, F):
    y = np.asarray(y, dtype=float)
    n, a = y.shape
    cov = np.cov(y, rowvar=False, ddof=1)
    C = np.eye(a) - np.ones((a, a)) / a
    S = C @ cov @ C
    tr = float(np.trace(S))
    denom = float((a - 1) * np.trace(S @ S))
    eps = 1.0 if denom <= 0 else tr * tr / denom
    eps = float(np.clip(eps, 1.0 / (a - 1), 1.0))
    df1 = eps * (a - 1)
    df2 = eps * (a - 1) * (n - 1)
    p = float(f_dist.sf(F, df1, df2))
    return {"gg_epsilon": eps, "gg_df1": df1, "gg_df2": df2, "gg_p": p}


def permutation_p(y, observed_F, seed, n_perm=N_PERM):
    y = np.asarray(y, dtype=float)
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
        perm = np.argsort(rng.random((m, n, a)), axis=2)
        yp = np.take_along_axis(np.broadcast_to(y, (m, n, a)), perm, axis=2)
        means = yp.mean(axis=1)
        ss_arch = n * ((means - grand) ** 2).sum(axis=1)
        ss_error = np.maximum(0.0, ss_total - ss_block - ss_arch)
        fp = (ss_arch / df1) / (ss_error / df2)
        extreme += int((fp >= observed_F - 1e-14).sum())
        remaining -= m
    return (extreme + 1) / (n_perm + 1)


def bootstrap_spearman(x, y, seed, n_boot=BOOTSTRAPS):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rho = float(spearmanr(x, y).statistic)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(x), len(x))
        r = spearmanr(x[idx], y[idx]).statistic
        if np.isfinite(r):
            vals.append(float(r))
    if vals:
        low, high = np.quantile(vals, [0.025, 0.975])
    else:
        low = high = np.nan
    return rho, float(low), float(high)


def load_outputs(root: Path):
    files = sorted((root / "runs").glob("*/*/block*/init*/*/epoch_*.json"))
    if not (root / "GRID_COMPLETE.json").exists():
        raise SystemExit(f"Completed Stage-F evaluation required: {root}")
    rows, models = [], []
    for path in files:
        v = json.loads(path.read_text())
        ident = {
            "task": v["task"], "architecture": v["architecture"],
            "block": int(v["block"]), "init_rep": int(v["init_rep"]),
            "treatment": v["treatment"],
        }
        models.append({
            **ident,
            "alignment": v["alignment"],
            "test_acc": v["test_acc"],
            "full_patch_max_logit_error": v["full_patch_max_logit_error"],
            "noop_max_logit_error": v["noop_max_logit_error"],
        })
        for r in v["rows"]:
            rows.append({**ident, **r})
    return pd.DataFrame(rows), pd.DataFrame(models), files


def verify(rows, models, files):
    assert len(files) == 25600, len(files)
    assert len(models) == 25600
    assert set(rows.task) == set(ac.TASKS)
    assert set(rows.architecture) == set(ac.ARCHS)
    assert set(rows.treatment) == set(ac.TREATMENTS)
    assert set(rows.block) == set(range(6000,6100))
    assert set(rows.init_rep) == {0,1,2,3}
    assert set(rows.k) == set(range(1,17))


def make_b(rows, kind):
    all_b = []
    id_cols = ["task","architecture","block","init_rep","k"]
    for metric in PRIMARY_METRICS:
        col = metric if kind == "selected" else f"random_{metric}"
        p = rows.pivot(index=id_cols, columns="treatment", values=col).reset_index()
        p["delta"] = p["release_default"] - p["retention_1"]
        s = p[p.k.isin(BUDGETS)]
        q = s.pivot(
            index=["task","architecture","block","init_rep"],
            columns="k", values="delta"
        ).reset_index()
        q["B"] = (q[4] + q[8]) / 2 - (q[1] + q[2]) / 2
        q["metric"] = metric
        q["kind"] = kind
        all_b.append(q[["task","architecture","block","init_rep","metric","kind","B"]])
    init = pd.concat(all_b, ignore_index=True)
    block = init.groupby(["task","architecture","block","metric","kind"], as_index=False).agg(
        B=("B","mean"), init_reps=("B","count")
    )
    return init, block


def robust_omnibus(block_b, kind):
    records = []
    for metric in PRIMARY_METRICS:
        s = block_b[(block_b.task==PRIMARY_TASK)&(block_b.metric==metric)&(block_b.kind==kind)]
        matrix = s.pivot(index="block", columns="architecture", values="B").reindex(
            index=range(6000,6100), columns=list(ac.ARCHS)
        ).to_numpy(float)
        base = rm_anova(matrix)
        gg = greenhouse_geisser(matrix, base["F"])
        pperm = permutation_p(matrix, base["F"], PERM_SEED + PRIMARY_METRICS.index(metric) + (100 if kind=="random" else 200 if kind=="selected_minus_random" else 0))
        fried = friedmanchisquare(*[matrix[:,i] for i in range(matrix.shape[1])])
        records.append({
            "task":PRIMARY_TASK,"metric":metric,"kind":kind,
            **base,**gg,
            "permutation_p":pperm,
            "friedman_chi2":float(fried.statistic),
            "friedman_p":float(fried.pvalue),
        })
    out = pd.DataFrame(records)
    out["permutation_p_holm_two_metric_family"] = holm_adjust(out.permutation_p.to_numpy(float))
    return out


def summarize_selected_random(selected, random):
    merged = selected.merge(
        random,
        on=["task","architecture","block","metric"],
        suffixes=("_selected","_random"),
    )
    merged["B_selected_minus_random"] = merged.B_selected - merged.B_random
    diff = merged[["task","architecture","block","metric","B_selected_minus_random"]].copy()
    diff["kind"] = "selected_minus_random"
    diff = diff.rename(columns={"B_selected_minus_random":"B"})
    rec = []
    for keys, s in merged.groupby(["task","architecture","metric"], sort=False):
        qs, qr, qd = interval(s.B_selected), interval(s.B_random), interval(s.B_selected_minus_random)
        rec.append({
            "task":keys[0],"architecture":keys[1],"metric":keys[2],
            "selected_mean":qs["mean"],"selected_ci_low":qs["ci_low"],"selected_ci_high":qs["ci_high"],
            "random_mean":qr["mean"],"random_ci_low":qr["ci_low"],"random_ci_high":qr["ci_high"],
            "selected_minus_random_mean":qd["mean"],
            "selected_minus_random_ci_low":qd["ci_low"],"selected_minus_random_ci_high":qd["ci_high"],
        })
    return merged, diff, pd.DataFrame(rec)


def architecture_mean_correlations(summary):
    rec = []
    for metric in PRIMARY_METRICS:
        s = summary[(summary.task==PRIMARY_TASK)&(summary.metric==metric)].sort_values("architecture")
        rho = spearmanr(s.selected_mean, s.random_mean)
        rec.append({
            "task":PRIMARY_TASK,"metric":metric,
            "spearman_selected_vs_random":float(rho.statistic),
            "p_spearman":float(rho.pvalue),
        })
    return pd.DataFrame(rec)


def random_bridge(random_b):
    rec = []
    for metric in PRIMARY_METRICS:
        s = random_b[(random_b.task==PRIMARY_TASK)&(random_b.metric==metric)]
        p = s.pivot(index="block", columns="architecture", values="B")
        d = p["tiny_gmp"] - p["plain2_w16_gmp"]
        q = one_sample(d.to_numpy(float))
        rec.append({"task":PRIMARY_TASK,"metric":metric,"contrast":"tiny_gmp - plain2_w16_gmp","kind":"random",**q})
    out = pd.DataFrame(rec)
    out["p_holm_two_metric_family"] = holm_adjust(out.p_two_sided.to_numpy(float))
    return out


def alignment_block(models):
    p = models.pivot(
        index=["task","architecture","block","init_rep"],
        columns="treatment", values="alignment"
    ).reset_index()
    p["delta_alignment_retention_minus_release"] = p["retention_1"] - p["release_default"]
    return p.groupby(["task","architecture","block"], as_index=False).agg(
        delta_alignment=("delta_alignment_retention_minus_release","mean"),
        retention_alignment=("retention_1","mean"),
        release_alignment=("release_default","mean"),
    )


def alignment_function_analysis(alignment, selected_b):
    joined = selected_b.merge(alignment, on=["task","architecture","block"])
    joined = joined[joined.task==PRIMARY_TASK].copy()

    summary = []
    correlations = []
    for metric in PRIMARY_METRICS:
        s = joined[joined.metric==metric]
        for arch, a in s.groupby("architecture", sort=False):
            qa = interval(a.delta_alignment)
            qb = interval(a.B)
            rho, low, high = bootstrap_spearman(
                a.delta_alignment.to_numpy(float),
                a.B.to_numpy(float),
                seed=PERM_SEED + 500 + list(ac.ARCHS).index(arch) + 50*PRIMARY_METRICS.index(metric),
            )
            summary.append({
                "task":PRIMARY_TASK,"architecture":arch,"metric":metric,
                "delta_alignment_mean":qa["mean"],"delta_alignment_ci_low":qa["ci_low"],"delta_alignment_ci_high":qa["ci_high"],
                "B_mean":qb["mean"],"B_ci_low":qb["ci_low"],"B_ci_high":qb["ci_high"],
            })
            correlations.append({
                "task":PRIMARY_TASK,"architecture":arch,"metric":metric,
                "spearman_rho":rho,"bootstrap_ci_low":low,"bootstrap_ci_high":high,
            })

    summary_df = pd.DataFrame(summary)
    corr_df = pd.DataFrame(correlations)

    arch_corr = []
    for metric in PRIMARY_METRICS:
        s = summary_df[summary_df.metric==metric]
        rho = spearmanr(s.delta_alignment_mean, s.B_mean)
        arch_corr.append({
            "task":PRIMARY_TASK,"metric":metric,
            "n_architectures":len(s),
            "spearman_architecture_means":float(rho.statistic),
            "p_descriptive":float(rho.pvalue),
        })
    return joined, summary_df, corr_df, pd.DataFrame(arch_corr)


def architecture_definitions():
    rec = []
    for arch in ac.ARCHS:
        spec = ac.ARCH_SPECS[arch]
        rec.append({
            "architecture":arch,
            "total_conv_depth":spec.total_depth,
            "downstream_width":spec.width,
            "pooling":spec.pooling,
            "connectivity":spec.connectivity,
            "batchnorm":spec.batchnorm,
            "parameter_count":ac.parameter_count(arch),
        })
    return pd.DataFrame(rec)


def make_scatter(summary, out):
    metrics = list(PRIMARY_METRICS)
    fig, axes = plt.subplots(1,2,figsize=(8.2,4.0))
    for ax, metric in zip(axes, metrics):
        s = summary[summary.metric==metric]
        ax.axhline(0,color="0.7",lw=0.8)
        ax.scatter(s.delta_alignment_mean, s.B_mean, s=22)
        for _, r in s.iterrows():
            ax.annotate(r.architecture, (r.delta_alignment_mean,r.B_mean), fontsize=6, xytext=(3,2), textcoords="offset points")
        ax.set_xlabel("retention - release template alignment")
        ax.set_ylabel("B")
        ax.set_title(metric)
    fig.tight_layout()
    fig.savefig(out / "alignment_B_scatter.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Completed Stage-F evaluation root")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    root = Path(args.input).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows, models, files = load_outputs(root)
    verify(rows, models, files)

    _, selected = make_b(rows, "selected")
    _, random = make_b(rows, "random")
    merged, diff, sr_summary = summarize_selected_random(selected, random)

    selected_omni = robust_omnibus(selected, "selected")
    random_omni = robust_omnibus(random, "random")
    diff_omni = robust_omnibus(diff, "selected_minus_random")
    omnibus = pd.concat([selected_omni,random_omni,diff_omni],ignore_index=True)

    mean_corr = architecture_mean_correlations(sr_summary)
    bridge = random_bridge(random)

    align = alignment_block(models)
    joined, align_summary, align_corr, align_arch_corr = alignment_function_analysis(align, selected)
    defs = architecture_definitions()

    selected.to_csv(out / "selected_B_per_block.csv", index=False)
    random.to_csv(out / "random_B_per_block.csv", index=False)
    sr_summary.to_csv(out / "selected_random_summary.csv", index=False)
    omnibus.to_csv(out / "omnibus_robustness.csv", index=False)
    mean_corr.to_csv(out / "selected_random_architecture_correlations.csv", index=False)
    bridge.to_csv(out / "random_bridge_contrast.csv", index=False)
    joined.to_csv(out / "alignment_B_per_block.csv", index=False)
    align_summary.to_csv(out / "alignment_B_architecture_summary.csv", index=False)
    align_corr.to_csv(out / "alignment_B_correlations.csv", index=False)
    align_arch_corr.to_csv(out / "alignment_B_architecture_mean_correlations.csv", index=False)
    defs.to_csv(out / "architecture_definitions.csv", index=False)
    make_scatter(align_summary, out)

    selected_primary = omnibus[omnibus.kind=="selected"]
    random_primary = omnibus[omnibus.kind=="random"]
    max_full = float(models.full_patch_max_logit_error.max())
    max_noop = float(models.noop_max_logit_error.max())

    lines = [
        "# Post hoc architecture diagnostics",
        "",
        "Status: outcome-informed diagnostic analysis; not prospective confirmation.",
        "",
        "## Sphericity-robust selected-channel architecture omnibus",
        "",
        "| Metric | F | GG epsilon | GG p | permutation p | Holm permutation p | Friedman p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in selected_primary.iterrows():
        lines.append(
            f"| {r.metric} | {r.F:.4f} | {r.gg_epsilon:.4f} | {r.gg_p:.3g} | "
            f"{r.permutation_p:.3g} | {r.permutation_p_holm_two_metric_family:.3g} | {r.friedman_p:.3g} |"
        )

    lines += [
        "",
        "## Ranking-independence diagnostic: random channel orders",
        "",
        "| Metric | random-B architecture permutation p | Holm p | selected/random architecture-mean Spearman rho |",
        "|---|---:|---:|---:|",
    ]
    for _, r in random_primary.iterrows():
        rho = mean_corr[mean_corr.metric==r.metric].iloc[0]
        lines.append(
            f"| {r.metric} | {r.permutation_p:.3g} | {r.permutation_p_holm_two_metric_family:.3g} | "
            f"{rho.spearman_selected_vs_random:+.3f} |"
        )

    lines += [
        "",
        "## Random-channel TinyGMP vs Plain2-GMP bridge",
        "",
        "| Metric | mean difference in random B | 95% CI | Holm p |",
        "|---|---:|---:|---:|",
    ]
    for _, r in bridge.iterrows():
        lines.append(
            f"| {r.metric} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] | {r.p_holm_two_metric_family:.3g} |"
        )

    lines += [
        "",
        "## Structural-versus-functional diagnostic",
        "",
        "Architecture-level alignment/B summaries and within-architecture correlations are in the CSV outputs and alignment_B_scatter.pdf. Correlations are descriptive and are not interpreted as mediation.",
        "",
        "## Integrity",
        "",
        f"- evaluated model JSONs: **{len(files):,}**",
        f"- maximum full-patch logit error: **{max_full:.6g}**",
        f"- maximum no-op logit error: **{max_noop:.6g}**",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")

    (out / "execution_manifest.json").write_text(json.dumps({
        "analysis":"architecture_posthoc_diagnostics_001",
        "status":"post_hoc_outcome_informed",
        "source_evaluation_root":str(root),
        "models":len(files),
        "primary_task":PRIMARY_TASK,
        "primary_metrics":list(PRIMARY_METRICS),
        "permutations":N_PERM,
        "bootstrap_replicates":BOOTSTRAPS,
        "protocol_path":str(Path(__file__).with_name("PROTOCOL.md")),
    }, indent=2) + "\n")

    print("Post hoc architecture diagnostics:", out / "REPORT.md")


if __name__ == "__main__":
    main()
