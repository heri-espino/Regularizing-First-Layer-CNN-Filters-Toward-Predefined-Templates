"""Aggregate the post-hoc patching-additivity study at renderer-block level."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

BOOT_SEED = 20260930
N_BOOT = 10000
BUDGETS = (1, 2, 4, 8)
PRIMARY_METRICS = ("centered_logit_fidelity", "prob_error_reduction")
CORE_ARCHS = ("tiny_gmp", "tiny_gap", "plain2_w16_gmp", "plain2_w16_gap")


def bootstrap_mean_ci(values: Iterable[float], seed: int, n_boot: int = N_BOOT, alpha: float = 0.05):
    x = np.asarray(list(values), dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return {"n": 0, "mean": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    means = x[idx].mean(axis=1)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return {"n": len(x), "mean": float(x.mean()), "ci_low": float(lo), "ci_high": float(hi)}


def load_rows(root: Path):
    rec = []
    models = []
    files = sorted((root / "runs").rglob("epoch_0200.json"))
    if not files:
        raise SystemExit(f"No additivity outputs found under {root / 'runs'}")
    for p in files:
        obj = json.loads(p.read_text())
        anchor_family = obj.get("anchor_family") or "not_applicable"
        id_cols = {
            "task": obj["task"], "architecture": obj["architecture"],
            "block": int(obj["block"]), "init_rep": int(obj["init_rep"]),
            "treatment": obj["treatment"],
            "anchor_family": anchor_family,
        }
        models.append({
            **id_cols, "path": str(p), "pair_count": int(obj["pair_count"]),
            "full_patch_max_logit_error": obj["full_patch_max_logit_error"],
            "noop_max_logit_error": obj["noop_max_logit_error"],
            "evaluation_seconds": obj.get("evaluation_seconds"),
        })
        for row in obj["rows"]:
            rec.append({**id_cols, **row})
    return pd.DataFrame(rec), pd.DataFrame(models), files


def average_controls(rows: pd.DataFrame) -> pd.DataFrame:
    """One row per model/set-family/budget; random/energy controls averaged within model."""
    ids = ["task", "architecture", "anchor_family", "block", "init_rep", "treatment", "set_family", "k"]
    numeric = [c for c in rows.columns if c not in ids + ["control_id"] and pd.api.types.is_numeric_dtype(rows[c])]
    return rows.groupby(ids, dropna=False, as_index=False)[numeric].mean()


def init_average(curves: pd.DataFrame) -> pd.DataFrame:
    ids = ["task", "architecture", "anchor_family", "block", "treatment", "set_family", "k"]
    numeric = [c for c in curves.columns if c not in ids + ["init_rep"] and pd.api.types.is_numeric_dtype(curves[c])]
    return curves.groupby(ids, dropna=False, as_index=False)[numeric].mean()


def release_minus_retention(block_curves: pd.DataFrame) -> pd.DataFrame:
    ids = ["task", "architecture", "anchor_family", "block", "set_family", "k"]
    value_cols = [c for c in block_curves.columns if c.startswith("observed_") or c.startswith("additive_") or c in (
        "centered_residual_energy_ratio", "centered_residual_norm_mpp", "cancellation_mean",
        "g_cross_term_mpp", "g_nonadditive_correction_mpp", "g_individual_sum_mpp", "g_add_mpp", "g_obs_mpp",
    )]
    out = None
    for col in value_cols:
        p = block_curves.pivot_table(index=ids, columns="treatment", values=col, aggfunc="first").reset_index()
        if not {"release_default", "retention_1"}.issubset(p.columns):
            continue
        p[col] = p["release_default"] - p["retention_1"]
        q = p[ids + [col]]
        out = q if out is None else out.merge(q, on=ids, how="outer")
    if out is None:
        raise ValueError("No treatment contrasts could be formed")
    return out


def b_table(delta: pd.DataFrame) -> pd.DataFrame:
    ids = ["task", "architecture", "anchor_family", "block", "set_family"]
    records = []
    for metric in PRIMARY_METRICS:
        for kind in ("observed", "additive"):
            col = f"{kind}_{metric}"
            if col not in delta:
                continue
            p = delta[delta.k.isin(BUDGETS)].pivot_table(index=ids, columns="k", values=col, aggfunc="first").reset_index()
            if not set(BUDGETS).issubset(p.columns):
                continue
            p["B"] = (p[4] + p[8]) / 2.0 - (p[1] + p[2]) / 2.0
            p["metric"] = metric
            p["curve"] = kind
            records.append(p[ids + ["metric", "curve", "B"]])
    if not records:
        return pd.DataFrame(columns=ids + ["metric", "curve", "B"])
    return pd.concat(records, ignore_index=True)


def summarize_groups(df: pd.DataFrame, group_cols: list[str], value_col: str, seed_offset: int = 0):
    rec = []
    for i, (keys, s) in enumerate(df.groupby(group_cols, dropna=False, sort=False)):
        if not isinstance(keys, tuple): keys = (keys,)
        q = bootstrap_mean_ci(s[value_col].to_numpy(float), BOOT_SEED + seed_offset + i)
        rec.append({**dict(zip(group_cols, keys)), **q})
    return pd.DataFrame(rec)


def curve_summary(block_curves: pd.DataFrame):
    subset = block_curves[block_curves.set_family == "selected"].copy()
    records = []
    cols = [
        "observed_centered_logit_fidelity", "additive_centered_logit_fidelity",
        "observed_prob_error_reduction", "additive_prob_error_reduction",
        "centered_residual_energy_ratio", "centered_residual_norm_mpp", "cancellation_mean",
        "g_individual_sum_mpp", "g_cross_term_mpp", "g_nonadditive_correction_mpp",
    ]
    group = ["task", "architecture", "anchor_family", "treatment", "k"]
    counter = 0
    for keys, s in subset.groupby(group, dropna=False, sort=False):
        for col in cols:
            if col not in s:
                continue
            q = bootstrap_mean_ci(s[col].to_numpy(float), BOOT_SEED + 1000 + counter)
            counter += 1
            records.append({**dict(zip(group, keys)), "quantity": col, **q})
    return pd.DataFrame(records)


def reconstruction_gap_summary(block_curves: pd.DataFrame):
    s = block_curves[block_curves.set_family == "selected"].copy()
    rec = []
    counter = 0
    for metric in PRIMARY_METRICS:
        obs, add = f"observed_{metric}", f"additive_{metric}"
        s[f"gap_{metric}"] = s[obs] - s[add]
        group = ["task", "architecture", "anchor_family", "treatment", "k"]
        for keys, g in s.groupby(group, dropna=False, sort=False):
            q = bootstrap_mean_ci(g[f"gap_{metric}"].to_numpy(float), BOOT_SEED + 2000 + counter)
            counter += 1
            rec.append({**dict(zip(group, keys)), "metric": metric, **q})
    return pd.DataFrame(rec)


def spatial_b_contrasts(b: pd.DataFrame):
    s = b[(b.set_family == "selected") & (b.anchor_family != "not_applicable")].copy()
    if s.empty or not {"structured_template", "pixel_permuted_template"}.issubset(set(s.anchor_family)):
        return pd.DataFrame(), pd.DataFrame()
    p = s.pivot_table(index=["task", "architecture", "block", "metric", "curve"], columns="anchor_family", values="B", aggfunc="first").reset_index()
    p["difference"] = p["structured_template"] - p["pixel_permuted_template"]
    per_arch = summarize_groups(p, ["task", "architecture", "metric", "curve"], "difference", 3000)
    avg = p.groupby(["task", "block", "metric", "curve"], as_index=False).difference.mean()
    averaged = summarize_groups(avg, ["task", "metric", "curve"], "difference", 4000)
    return per_arch, averaged


def simultaneous_gap_bands(block_curves: pd.DataFrame, n_boot: int = 5000):
    """Unstudentized simultaneous 95% bands for observed-additive curve gaps over k."""
    s = block_curves[block_curves.set_family == "selected"].copy()
    rec = []
    groups = ["task", "architecture", "anchor_family", "treatment"]
    rng = np.random.default_rng(BOOT_SEED + 5000)
    for keys, g in s.groupby(groups, dropna=False, sort=False):
        for metric in PRIMARY_METRICS:
            obs, add = f"observed_{metric}", f"additive_{metric}"
            p = g.pivot_table(index="block", columns="k", values=[obs, add], aggfunc="first")
            ks = sorted(set(p[obs].columns) & set(p[add].columns))
            if not ks: continue
            gap = (p[obs][ks] - p[add][ks]).dropna()
            if len(gap) < 2: continue
            mean = gap.mean(axis=0).to_numpy(float)
            arr = gap.to_numpy(float)
            idx = rng.integers(0, len(arr), size=(n_boot, len(arr)))
            boot = arr[idx].mean(axis=1)
            maxdev = np.max(np.abs(boot - mean[None, :]), axis=1)
            radius = float(np.quantile(maxdev, 0.95))
            for j, k in enumerate(ks):
                vals = arr[:, j]
                q = bootstrap_mean_ci(vals, BOOT_SEED + 6000 + j, n_boot=n_boot)
                rec.append({
                    **dict(zip(groups, keys)), "metric": metric, "k": int(k), "mean_gap": float(mean[j]),
                    "pointwise_ci_low": q["ci_low"], "pointwise_ci_high": q["ci_high"],
                    "simultaneous_ci_low": float(mean[j] - radius), "simultaneous_ci_high": float(mean[j] + radius),
                    "band_type": "unstudentized block-bootstrap simultaneous band across intervention sizes",
                })
    return pd.DataFrame(rec)


def make_figures(curves: pd.DataFrame, gaps: pd.DataFrame, out: Path):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    figdir = out / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    made = []
    core = curves[(curves.set_family if "set_family" in curves else pd.Series(index=curves.index, data="selected")) == "selected"] if "set_family" in curves else curves
    # One compact core figure per metric. Curves are block-bootstrap means; panels are architectures.
    for metric in PRIMARY_METRICS:
        quantity_obs = f"observed_{metric}"
        quantity_add = f"additive_{metric}"
        sub = curves[(curves.quantity.isin([quantity_obs, quantity_add])) & curves.architecture.isin(CORE_ARCHS)]
        if sub.empty: continue
        for task in sorted(sub.task.unique()):
            st = sub[sub.task == task]
            # Keep anchor families separate. The architecture study uses the
            # explicit sentinel ``not_applicable`` so pandas pivot/groupby does
            # not silently drop every row through an all-NaN index level.
            anchor_values = list(st.anchor_family.drop_duplicates())
            for anchor in anchor_values:
                sa = st[st.anchor_family == anchor]
                if sa.empty: continue
                fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
                for ax, arch in zip(axes.ravel(), CORE_ARCHS):
                    a = sa[sa.architecture == arch]
                    for treatment in ("retention_1", "release_default"):
                        t = a[a.treatment == treatment]
                        for quantity, ls in ((quantity_obs, "-"), (quantity_add, "--")):
                            q = t[t.quantity == quantity].sort_values("k")
                            if q.empty: continue
                            label = f"{treatment}: {'observed' if quantity==quantity_obs else 'additive'}"
                            ax.plot(q.k, q["mean"], linestyle=ls, label=label)
                        ax.set_title(arch)
                    ax.set_xlabel("patched channels k")
                    ax.set_ylabel(metric.replace("_", " "))
                handles, labels = axes.ravel()[0].get_legend_handles_labels()
                if handles: fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=8)
                fig.tight_layout(rect=(0,0,1,0.92))
                suffix = "architecture" if anchor == "not_applicable" else str(anchor)
                path = figdir / f"observed_vs_additive_{task}_{suffix}_{metric}.pdf"
                fig.savefig(path, bbox_inches="tight"); plt.close(fig); made.append(path)
    # Residual-energy curve for all architectures in each source grouping.
    sub = curves[curves.quantity == "centered_residual_energy_ratio"]
    for task in sorted(sub.task.unique()):
        for treatment in sorted(sub.treatment.unique()):
            q = sub[(sub.task == task) & (sub.treatment == treatment) & (sub.anchor_family == "not_applicable")]
            if q.empty: continue
            fig, ax = plt.subplots(figsize=(8, 5))
            for arch, a in q.groupby("architecture", sort=False):
                a = a.sort_values("k")
                ax.plot(a.k, a["mean"], label=arch)
            ax.set_xlabel("patched channels k"); ax.set_ylabel("centered residual energy / base-donor energy")
            ax.legend(fontsize=6, ncol=2); fig.tight_layout()
            path = figdir / f"residual_energy_{task}_{treatment}.pdf"
            fig.savefig(path, bbox_inches="tight"); plt.close(fig); made.append(path)
    return made


def write_report(out: Path, source: str, models: pd.DataFrame, curves: pd.DataFrame, b_summary: pd.DataFrame,
                 gap_summary: pd.DataFrame, spatial_avg: pd.DataFrame, files_count: int):
    max_full = models.full_patch_max_logit_error.max()
    max_noop = models.noop_max_logit_error.max()
    lines = [
        "# Patching additivity report", "",
        "Status: post-hoc analysis of previously trained checkpoints; no new training.", "",
        f"- source study: **{source}**",
        f"- evaluated checkpoint files: **{files_count:,}**",
        f"- renderer blocks represented: **{models.block.nunique()}**",
        f"- maximum full-patch logit identity error: **{max_full:.6g}**",
        f"- maximum no-op logit identity error: **{max_noop:.6g}**", "",
        "## Central decomposition", "",
        "For each matched pair, the centered-logit change is decomposed as `observed = additive singleton sum + residual`. "
        "All singleton geometry, cancellation, cross terms, and residual corrections are computed per pair before aggregation.", "",
        "The squared-error decomposition is reported through the individual contribution sum, the pairwise cross-term correction, "
        "and the exact non-additivity correction. Curvature of fidelity/probability curves is therefore not treated as evidence of model non-additivity by itself.", "",
        "## Release-minus-retention intervention-size contrast B", "",
        "`B = mean(delta at k=4,8) - mean(delta at k=1,2)`, where delta is release minus retention. "
        "Intervals are renderer-block bootstrap intervals after averaging initialization replicates within each block.", "",
    ]
    core = b_summary[(b_summary.set_family == "selected") if "set_family" in b_summary else np.ones(len(b_summary), dtype=bool)]
    if not core.empty:
        lines += ["| Task | Architecture | Anchor | Metric | Curve | Mean B | 95% block-bootstrap CI |", "|---|---|---|---|---|---:|---:|"]
        for _, r in core.iterrows():
            anchor = "—" if r.get("anchor_family") == "not_applicable" else r.get("anchor_family")
            lines.append(f"| {r.task} | {r.architecture} | {anchor} | {r.metric} | {r.curve} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] |")
    lines += ["", "## Observed minus additive reconstruction", "",
              "Positive values mean the observed metric is larger than the additive reconstruction; negative values mean it is smaller. "
              "For centered logits, the corresponding residual and exact squared-error correction are reported separately.", ""]
    if source == "anchor" and not spatial_avg.empty:
        lines += ["## Structured versus pixel-permuted filter banks", "",
                  "The table below compares the structured and pixel-permuted banks on B after averaging the four architectures within each renderer block.", "",
                  "| Task | Metric | Curve | Mean structured-pixel-permuted B | 95% block-bootstrap CI |", "|---|---|---|---:|---:|"]
        for _, r in spatial_avg.iterrows():
            lines.append(f"| {r.task} | {r.metric} | {r.curve} | {r['mean']:+.6f} | [{r.ci_low:+.6f}, {r.ci_high:+.6f}] |")
        lines.append("")
    lines += [
        "## Interpretation frame", "",
        "- **Additive account:** agreement between observed and reconstructed curves, together with nonzero cancellation/cross terms and small residual energy, supports a superposition-plus-metric explanation.",
        "- **Non-additive account:** reproducible reconstruction gaps accompanied by non-negligible residual energy and exact residual correction identify where downstream computation departs from the singleton superposition model.",
        "- **Combined account:** both can coexist and should be quantified by architecture, treatment, task, and filter bank rather than collapsed into a single mechanism label.", "",
        "## Limits", "",
        "This analysis is post-hoc and reuses the same models and matched counterfactual pairs as the source studies. It does not provide an independent confirmatory sample, identify a unique semantic mechanism, or establish natural-image generalization. "
        "Tiny architectures are an analytic implementation control: because their tail is pooling followed by a linear classifier, whole-channel patching should be additive in logits up to numerical error even when fidelity or probability curves are nonlinear.",
    ]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--source", choices=("architecture", "anchor"), required=True)
    args = p.parse_args()
    root = Path(args.input).resolve(); out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    rows, models, files = load_rows(root)
    curves_model = average_controls(rows)
    block_curves = init_average(curves_model)
    delta = release_minus_retention(block_curves)
    b = b_table(delta)
    b_summary = summarize_groups(b, ["task", "architecture", "anchor_family", "set_family", "metric", "curve"], "B", 10)
    curves = curve_summary(block_curves)
    gaps = reconstruction_gap_summary(block_curves)
    spatial_arch, spatial_avg = spatial_b_contrasts(b)
    bands = simultaneous_gap_bands(block_curves)

    curves_model.to_csv(out / "per_model_curves.csv", index=False)
    block_curves.to_csv(out / "per_block_curves.csv", index=False)
    delta.to_csv(out / "release_minus_retention_per_block.csv", index=False)
    b.to_csv(out / "B_per_block.csv", index=False)
    b_summary.to_csv(out / "B_summary.csv", index=False)
    curves.to_csv(out / "curve_summary.csv", index=False)
    gaps.to_csv(out / "reconstruction_gap_summary.csv", index=False)
    bands.to_csv(out / "reconstruction_gap_bands.csv", index=False)
    if not spatial_arch.empty: spatial_arch.to_csv(out / "structured_vs_pixel_permuted_B_by_architecture.csv", index=False)
    if not spatial_avg.empty: spatial_avg.to_csv(out / "structured_vs_pixel_permuted_B_averaged_architectures.csv", index=False)
    models.to_csv(out / "model_integrity.csv", index=False)
    made = make_figures(curves, gaps, out)
    write_report(out, args.source, models, curves, b_summary, gaps, spatial_avg, len(files))
    (out / "summary.json").write_text(json.dumps({
        "study": "cnn_patching_additivity_001", "source": args.source,
        "models": len(models), "blocks": int(models.block.nunique()),
        "bootstrap_seed": BOOT_SEED, "bootstrap_replicates": N_BOOT,
        "primary_metrics": list(PRIMARY_METRICS), "B_budgets": list(BUDGETS),
        "figures": [str(p.relative_to(out)) for p in made],
        "max_full_patch_logit_error": float(models.full_patch_max_logit_error.max()),
        "max_noop_logit_error": float(models.noop_max_logit_error.max()),
    }, indent=2) + "\n", encoding="utf-8")
    print("Report:", out / "REPORT.md")


if __name__ == "__main__":
    main()