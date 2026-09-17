# Template Priors in Small CNNs

This repository contains the manuscript, frozen experimental protocols, analysis outputs, and reproducibility code for:

> **Template Priors in Small CNNs: Activation-Patching Effects Depend on the Number of Patched Channels**

The paper studies first-layer template priors in small convolutional networks and separates **kernel-template similarity** from **activation-patching behavior**. Persistent template retention produces high kernel-template similarity, while the measured release-versus-retention effect under activation patching changes with the number of patched channels and with architecture.

## Start here

- **Paper source:** [`papers/main.tex`](papers/main.tex)
- **Build the paper:** `python build.py`
- **Prospective confirmation (Stage D):** [`analysis/budget_confirmation_001/REPORT.md`](analysis/budget_confirmation_001/REPORT.md)
- **1,200-model sensitivity study (Stage E):** [`analysis/exhaustive_robustness_001/REPORT.md`](analysis/exhaustive_robustness_001/REPORT.md)
- **Independent checkpoint audit:** [`analysis/checkpoint_audit/AUDIT_REPORT.md`](analysis/checkpoint_audit/AUDIT_REPORT.md)
- **Study map and frozen protocols:** [`studies/README.md`](studies/README.md)
- **Analysis map:** [`analysis/README.md`](analysis/README.md)

## Build the manuscript

Python itself has no package dependencies for the paper build. A TeX installation providing `pdflatex` and `bibtex` must be available on `PATH`.

From the repository root:

```bash
python build.py
```

The final PDF is written as:

```text
espino_2026_template-priors.pdf
```

For a clean rebuild:

```bash
python build.py --clean
```

Intermediate LaTeX files are kept under `papers/build/` and are ignored by Git.

## Repository layout

```text
.
├── build.py                         # Cross-platform paper builder
├── papers/                          # TMLR manuscript source and appendix tables
├── studies/                         # Frozen protocols and experiment code
├── analysis/                        # Paper-facing analyses, tables, figures, reports
├── results/                         # Imported experiment outputs used by later analyses
├── literature/                      # Bibliography and literature notes
├── scripts/                         # Shared execution helpers
└── run_paper_experiments.*          # Stage-D / Stage-E reproduction launchers
```

The repository preserves the experimental record rather than flattening all stages into a single script. Each confirmatory or secondary study keeps its own protocol, implementation, and analysis files. The top-level documentation is intended to make that record navigable without rewriting it.

## Experimental record

The manuscript is built around five evidential stages.

| Stage | Role | Main location |
|---|---|---|
| A | Initial alignment and intervention study | `studies/cnn_causal_milestone/` |
| B | 200-epoch retention/release study | `studies/cnn_release_experiment/` |
| C | Post hoc patch-size and baseline decomposition | `studies/cnn_patch_robustness/`, `studies/cnn_patch_energy_control/` |
| D | Frozen prospective confirmation | `studies/cnn_budget_confirmation/` |
| E | Predeclared 1,200-model sensitivity study | `studies/cnn_exhaustive_robustness/` |

The independent reimplementation audit is in `studies/cnn_checkpoint_audit/`.

The single Stage-D primary test used 20 previously unused `two_concepts` TinyCNN blocks. Its predeclared contrast was

\[
B=0.33098,\qquad 95\%\ \mathrm{CI}=[0.27368,0.38827],
\]

with two-sided \(p=2.28\times10^{-10}\). Stage E then tested the same patch-size contrast across two tasks, two architectures, six prior schedules, and 50 new blocks. TinyCNN gives positive values of the contrast in both tasks, while TwoLayerCNN shows a different pattern. The paper therefore treats architecture and the number of patched channels as part of the reported result.

## Reproducing the prospective studies

The Stage-D and Stage-E launchers are retained because their protocols were frozen before the corresponding outcomes were generated.

Windows:

```powershell
.\run_paper_experiments.cmd
```

PowerShell directly:

```powershell
.\run_paper_experiments.ps1
```

Zsh:

```bash
zsh run_paper_experiments.zsh
```

These experiments are computationally expensive. For exact design details, source hashes, block ranges, and output structure, read the protocol in the relevant study directory before running anything.

## Scope

The empirical claims are intentionally restricted to the tested synthetic renderer, first-layer interventions, and small CNN family. Kernel-template similarity is a weight-space measurement; selected-channel fidelity is defined for the specified activation-patching procedure. The experiments do not establish a unique causal mechanism, human interpretability, or natural-image generalization.

## Archival note

This repository is being prepared as the archival research artifact associated with the manuscript. A Zenodo DOI and final citation metadata should be added only after the archival release is minted. Third-party TMLR style files retain their original license in `papers/tmlr/`.
