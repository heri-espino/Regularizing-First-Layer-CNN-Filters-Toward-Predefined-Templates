# Template Priors in Small CNNs

Research artifact for:

> **Regularizing First-Layer CNN Filters Toward Predefined Templates: Activation-Patching Comparisons Depend on Channel Count and Architecture**

This repository contains the manuscript, frozen experimental protocols, saved analysis outputs, and reproduction code. The paper separates first-layer **kernel-template similarity** from **activation-patching behavior**: persistent template retention strongly preserves template-like kernels, while the measured release-versus-retention effect changes with the number of patched channels and with architecture.

## Start here

- **Current research state / handoff:** [`RESEARCH_STATUS.md`](RESEARCH_STATUS.md)
- **Post-Stage-F manuscript revision plan:** [`paper/REVISION_PLAN.md`](paper/REVISION_PLAN.md)
- **Paper:** [`paper/main.tex`](paper/main.tex)
- **Build:** `python paper/build.py`
- **Publication figures:** `python paper/build_figures.py`
- **Prospective test (Stage D):** [`analysis/budget_confirmation_001/REPORT.md`](analysis/budget_confirmation_001/REPORT.md)
- **1,200-model sensitivity study (Stage E):** [`analysis/exhaustive_robustness_001/REPORT.md`](analysis/exhaustive_robustness_001/REPORT.md)
- **Independent checkpoint audit:** [`analysis/checkpoint_audit/AUDIT_REPORT.md`](analysis/checkpoint_audit/AUDIT_REPORT.md)
- **Completed metric-sensitivity analysis:** [`analysis/metric_sensitivity_001/REPORT.md`](analysis/metric_sensitivity_001/REPORT.md)
- **Frozen Stage-F architecture protocol:** [`studies/cnn_architecture_robustness/PROTOCOL.md`](studies/cnn_architecture_robustness/PROTOCOL.md)
- **Study map:** [`studies/README.md`](studies/README.md)
- **Run helpers:** [`run/README.md`](run/README.md)
- **Analysis map:** [`analysis/README.md`](analysis/README.md)

## Build the manuscript

A TeX installation providing `pdflatex` and `bibtex` must be available on `PATH`.

```bash
python paper/build.py --clean
```

This produces:

```text
paper/espino_2026_template-priors.pdf
```

The manuscript builder itself uses only the Python standard library. LaTeX intermediates and the generated PDF are not versioned.

### Regenerate the publication figures

The figures used by the manuscript are generated separately from saved experimental artifacts:

```bash
python -m pip install -e ".[experiments]"
python paper/build_figures.py
```

The publication plotting system uses a consistent white-grid theme, a color-blind-friendly palette, and a Latin/Computer Modern serif stack. Figures are saved as PDF; axes and typography remain vector while dense heatmaps and kernel images are selectively rasterized inside the PDF. This step changes presentation only and does not retrain models or redefine analyses.

## Python environment

`pyproject.toml` provides a convenient common analysis environment:

```bash
python -m pip install -e .
```

For scripts that require PyTorch:

```bash
python -m pip install -e ".[experiments]"
```

Individual study directories still contain their original requirement files and environment notes; those remain authoritative when reproducing a frozen experiment.

## Repository layout

```text
.
├── paper/                 # Manuscript, publication figures, style, paper builders
├── run/                   # Convenience launchers
├── studies/               # Frozen protocols and experiment implementations
├── analysis/              # Paper-facing analyses, figures, tables, reports
├── results/               # Imported experiment outputs used by analyses
├── literature/            # Bibliography and literature notes
├── scripts/               # Shared environment/execution helpers
├── pyproject.toml          # Common Python metadata and dependencies
├── CITATION.cff            # Machine-readable citation metadata
├── .zenodo.json            # Zenodo release metadata
└── LICENSE                 # Repository license
```

The repository intentionally preserves the experimental record instead of flattening all stages into a single pipeline. Frozen protocols and historical study directories remain separate so the inferential status and provenance of each result are traceable.

## Experimental record

| Stage | Role | Main location |
|---|---|---|
| A | Initial alignment and intervention study | `studies/cnn_causal_milestone/` |
| B | 200-epoch retention/release study | `studies/cnn_release_experiment/` |
| C | Post hoc patch-size and baseline decomposition | `studies/cnn_patch_robustness/`, `studies/cnn_patch_energy_control/` |
| D | Frozen prespecified prospective test | `studies/cnn_budget_confirmation/` |
| E | Predeclared sensitivity study on 50 new blocks per setting | `studies/cnn_exhaustive_robustness/` |
| Metric audit | Frozen post hoc metric-sensitivity analysis of saved Stage-D/E checkpoints; no retraining | `studies/cnn_metric_sensitivity/` |
| F | Frozen fresh-sample architecture robustness study: 16 architectures, 100 renderer blocks, 4 paired initializations | `studies/cnn_architecture_robustness/` |
| Audit | Independent checkpoint reimplementation | `studies/cnn_checkpoint_audit/` |

The Stage-D primary analysis used 20 previously unused `two_concepts` TinyCNN blocks. The predeclared contrast was

\[
B=0.33098,\qquad 95\%\ \mathrm{CI}=[0.27368,0.38827],
\]

with two-sided \(p=2.28\times10^{-10}\). Stage E evaluated the same patch-size contrast across two tasks, two architectures, six prior schedules, and 50 new blocks. TinyCNN gives positive values of the contrast in both tasks, while TwoLayerCNN shows a different pattern.

## Reproducing the prospective studies

The convenience wrappers are now grouped under `run/`.

Windows:

```powershell
.\run\run_paper_experiments.cmd
```

PowerShell directly:

```powershell
.\run\run_paper_experiments.ps1
```

Zsh:

```bash
zsh run/run_paper_experiments.zsh
```

These experiments are computationally expensive. Read the corresponding `PROTOCOL.md` before rerunning them.

The completed metric-sensitivity study does **not** retrain models. After the Stage-D/E artifacts are present, run:

```powershell
.\run\run_metric_sensitivity.ps1
```

or:

```bash
zsh run/run_metric_sensitivity.zsh
```

Its protocol was frozen before any centered-logit or unnormalized-error outputs were generated. The completed audit showed that the TinyCNN patch-budget contrast persists under centered-logit fidelity and unnormalized probability error reduction, while architecture remains a major source of heterogeneity.

Stage F targets that remaining architecture question with fresh blocks and multiple paired initialization replicates. The official run is a clean CUDA run under `%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001`. As of 2026-09-20, all 25,600 models and all frozen evaluations are complete; the Stage-F analysis is archived under `analysis/architecture_robustness_001/`. See `RESEARCH_STATUS.md` for the exact live state and resume command.

## Scope

The empirical claims are restricted to the tested synthetic renderer, first-layer interventions, and small CNN family. Kernel-template similarity is a weight-space measurement; selected-channel fidelity is defined for the specified activation-patching procedure. The experiments do not establish a unique causal mechanism, human interpretability, or natural-image generalization.

## Citation and archival release

Citation metadata is provided in [`CITATION.cff`](CITATION.cff), with Zenodo metadata in [`.zenodo.json`](.zenodo.json). The repository is prepared for a versioned archival release; after Zenodo mints the DOI, add that DOI to both metadata files and the README before freezing the final citation record.
