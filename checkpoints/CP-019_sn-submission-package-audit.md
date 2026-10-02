# CP-019 — SN submission package and reproducibility audit

## 1. Status / date / evidential role

- **Date:** 2026-10-02
- **Status:** submission-package audit complete at source level; final compiled-PDF visual check still requires running the manual `paper-compile` workflow.
- **Evidential role:** engineering/reproducibility and manuscript-integrity checkpoint. No new models were trained and no new scientific experiment was introduced.

## 2. Why this checkpoint exists

After the compact SN Computer Science manuscript was expanded from 12 to approximately 15 pages, a referee-style pass judged the scientific presentation close to submission-ready and recommended checking the actual supplementary/reproducibility package rather than adding experiments.

The audit was therefore aimed at a stricter question: **does every central main-text figure and quantitative claim have an exact archived source, frozen protocol, and submission-facing path that will actually be included with the paper?**

## 3. Scientific question or engineering objective

The engineering objective was to make the SN submission self-consistent and auditable without returning to the long TMLR-style appendix structure.

Required properties:

1. Supplementary Section S1 cited by the manuscript must actually exist.
2. The supplement must be standalone rather than a collection of old appendix fragments with unresolved cross-references.
3. Every main figure and principal statistic must map to archived paper-facing data.
4. Frozen protocols and relevant analysis code must be included.
5. Raw checkpoints and tens of thousands of per-model JSON files must remain outside the journal package.
6. Historical and current confidence-interval conventions must not be mixed.
7. Repository/citation metadata shipped with the artifact must match the SN manuscript.

## 4. What was done

### Visual-source fixes

- `paper/build_additivity_curves_figure.py`
  - moved the residual-panel legend below the panel;
  - increased legend readability.
- `paper/build_additivity_figure.py`
  - moved the spatial metric labels inside the spatial panel to avoid crowding the Tiny-GMP annotation and panel separation.

### Standalone Supplementary Information

Added:

- `paper/sn_supplement.tex`
- `paper/build_supplement.py`

The supplement now has numbered Sections S1--S7 and includes:

- S1 architecture and training specification;
- intervention-size and metric robustness;
- architecture robustness plus post-hoc robustness checks;
- pixel-permuted spatial control;
- singleton-additive decomposition;
- a figure/data provenance map;
- integrity-check and artifact-scope notes.

### Reproducibility map and package builder

Added:

- `paper/SUPPLEMENT_REPRODUCIBILITY.md`
- `paper/build_submission_package.py`

The package is allowlist-based. At this checkpoint it contains **126 repository files** totaling approximately **23.2 MiB uncompressed**, plus the built main and supplementary PDFs. Static path validation found **zero missing allowlisted files**.

The package includes:

- relevant Springer class/style and bibliography files;
- manuscript/supplement sources and build scripts;
- renderer/model definitions;
- frozen protocols;
- paper-facing training/evaluation/analysis code;
- aggregate and block-level tables needed for main figures and inferential summaries;
- integrity/audit reports;
- project, citation, Zenodo, and license metadata.

It excludes:

- raw checkpoints;
- per-model evaluator JSONs;
- Git history;
- caches;
- local machine outputs;
- large development-only intermediates not required for paper verification.

### Manual CI packaging

The manual-only workflow `.github/workflows/paper_compile.yml` now:

1. builds the SN manuscript;
2. builds the standalone supplement;
3. builds the allowlisted submission ZIP;
4. uploads manuscript, supplement, ZIP, and build logs as a 30-day artifact.

The workflow remains `workflow_dispatch` only.

### Documentation and metadata

Updated:

- `paper/README.md`
- `paper/SUBMISSION_CHECKLIST.md`
- `analysis/README.md`
- root `README.md`
- `pyproject.toml`
- `CITATION.cff`
- `.zenodo.json`

The current title is consistently:

> **Activation Patching in Structured CNNs: Intervention Size, Architecture, and Additivity**

Author metadata now uses **Espino Montelongo** without a hyphen, and repository URLs point to the current repository.

## 5. Evidence / results available now

### Claim-to-source audit

The main numerical claims were checked against their archived sources.

#### Fresh schedule/task endpoint values

The first Results paragraph uses the 50-block schedule/task sensitivity endpoint study, not the older 10-block retention/release table.

Source:

`analysis/exhaustive_robustness_001/model_endpoint_summary.csv`

For `two_concepts`:

- TinyCNN retention: accuracy 0.98046875, alignment 0.94414658;
- TinyCNN release: accuracy 0.99453125, alignment 0.57411191;
- TwoLayerCNN retention: accuracy 0.99109375, alignment 0.99875220;
- TwoLayerCNN release: accuracy 0.992578125, alignment 0.89568788.

These reproduce the rounded manuscript values 98.05/99.45%, 0.944/0.574, 99.11/99.26%, and 0.999/0.896.

#### Pre-specified intervention-size contrast

Source:

`analysis/budget_confirmation_001/budget_contrasts.csv`

Primary TinyCNN contrast:

[
B=0.3309763,qquad
95%,CI=[0.2736799,0.3882727].
]

Pointwise release-minus-retention effects at (k=1,2,4,8) are reproduced by `treatment_contrasts.csv`.

#### Alternative metrics

Source:

`analysis/metric_sensitivity_001/stage_d_budget_contrasts_B.csv`

- centered-logit fidelity: (B=0.1788812), 95% CI ([0.1272680,0.2304943]);
- probability-error reduction: (B=0.8944113), 95% CI ([0.7863008,1.0025219]).

#### Architecture omnibus

Source:

`analysis/architecture_robustness_001/primary_architecture_omnibus.csv`

- centered logits: (F(15,1485)=77.0874), partial (eta^2=0.4378);
- probability error reduction: (F(15,1485)=656.7002), partial (eta^2=0.8690).

The post-hoc robustness statement is sourced to:

`analysis/architecture_posthoc_diagnostics_001/omnibus_robustness.csv`

and accompanying random-channel tables.

#### Spatial-control interval correction

The audit found that the manuscript had been using the **bootstrap 95% interval from the later additivity analysis** while discussing the **primary spatial-control experiment**.

The mean was unchanged, but the inferential source should match the experiment being described.

The main spatial-control Results section now uses the original paired Student-(t) intervals from:

`analysis/anchor_specificity_001/primary_spatial_specificity.csv`

- centered logits: +0.05743, 95% CI **[0.05116, 0.06369]**;
- probability error reduction: +0.04563, 95% CI **[0.03728, 0.05397]**.

The 90% TOST intervals and frozen margins remain:

- centered logits: [0.05219, 0.06266], margin (pm0.01704);
- probability error: [0.03864, 0.05261], margin (pm0.06594).

The later Figure 5/additivity panel correctly retains its renderer-block **bootstrap** intervals from `analysis/patching_additivity_001/anchor_analysis/`. The two interval conventions are now explicitly separated.

#### BN2-GAP additive discrepancy

Recomputed directly from the 100 rows in:

`analysis/patching_additivity_001/architecture_analysis/B_per_block.csv`

for `two_concepts/bn2_w16_gap`, centered-logit fidelity:

[
B_{mathrm{obs}}-B_{mathrm{add}}
=-0.1799415521,
]

with paired Student-(t) 95% CI

[
[-0.2008225633,-0.1590605409].
]

This matches the manuscript.

### Supplement integrity

Static source checks on `paper/sn_supplement.tex` found:

- all internal `\ref` targets defined;
- balanced LaTeX braces;
- no missing package-file paths in the allowlist;
- S1 is exactly **Architecture and training specification**, matching the main-text citation.

## 6. Interpretation

The scientific study does **not** need another experiment based on this audit.

The important effect of this checkpoint is narrower but significant: the submission now distinguishes

1. primary versus later-bootstrap uncertainty;
2. historical endpoint sources versus the fresh 50-block endpoint study;
3. pre-specified architecture inference versus post-hoc robustness checks;
4. manuscript evidence versus separately retained raw checkpoints.

This makes the package materially easier for a reviewer or editor to audit and reduces the risk of an otherwise correct result appearing unreproducible because the wrong supporting file was shipped.

## 7. What this does not establish

This checkpoint does not:

- add new scientific evidence;
- change inferential sample sizes;
- make the synthetic-CNN conclusions generalize to natural images or transformers;
- identify a unique downstream layer responsible for non-additivity;
- verify final PDF typography after a fresh CI build;
- verify the journal upload interface or editorial-system requirements.

The final visual build must still be inspected after running the manual workflow.

## 8. Repository / provenance pointers

Primary manuscript and supplement:

- `paper/main.tex`
- `paper/sn_supplement.tex`
- `paper/SUPPLEMENT_REPRODUCIBILITY.md`
- `paper/SUBMISSION_CHECKLIST.md`

Build/package scripts:

- `paper/build.py`
- `paper/build_supplement.py`
- `paper/build_submission_package.py`

Key paper-facing analyses:

- `analysis/budget_confirmation_001/`
- `analysis/exhaustive_robustness_001/`
- `analysis/metric_sensitivity_001/`
- `analysis/architecture_robustness_001/`
- `analysis/architecture_posthoc_diagnostics_001/`
- `analysis/anchor_specificity_001/`
- `analysis/patching_additivity_001/`

Relevant frozen protocols:

- `studies/cnn_budget_confirmation/PROTOCOL.md`
- `studies/cnn_exhaustive_robustness/PROTOCOL.md`
- `studies/cnn_metric_sensitivity/PROTOCOL.md`
- `studies/cnn_architecture_robustness/PROTOCOL.md`
- `studies/cnn_anchor_specificity/PROTOCOL.md`
- `studies/cnn_patching_additivity/PROTOCOL.md`

Post-hoc architecture robustness:

- `studies/cnn_architecture_posthoc/PROTOCOL.md`

## 9. Next actions

1. Run the manual GitHub Actions workflow **paper-compile**.
2. Download the resulting artifact.
3. Inspect:
   - `sn_submission.pdf`;
   - `sn_supplement.pdf`;
   - `sn_submission_package.zip`;
   - both LaTeX logs.
4. Visually confirm:
   - Figure 4 residual legend is below the residual panel and readable;
   - Figure 5 spatial metric labels sit inside the panel without overlapping data;
   - supplement tables fit the SN page width;
   - there are no undefined references/citations or overfull elements severe enough to impair reading.
5. Open the ZIP and spot-check the provenance paths in `SUPPLEMENT_REPRODUCIBILITY.md`.
6. Only then freeze the exact submission commit/tag.

## 10. Do-not-forget constraints

- Do not re-expand the main article back toward the 28-page TMLR version.
- Do not add another experimental campaign unless a new reviewer/editor identifies a substantive evidential gap.
- Keep Figure 3 spatial-control (t) intervals separate from Figure 5 additivity bootstrap intervals.
- Keep Stage-F primary inference distinct from the explicitly post-hoc architecture robustness checks.
- Keep raw checkpoints/per-model evaluator JSONs out of the journal ZIP.
- Heavy paper/PDF workflows remain manual-only through `workflow_dispatch`.
