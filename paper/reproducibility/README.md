# Activation patching — reproducibility archive

Companion artifact for **When Do Activation-Patching Effects Add Up? Evidence from Controlled CNNs**, submitted to *SN Computer Science*.

This archive is designed for a reviewer who does **not** have the original repository. It provides the exact archived inputs required for all manuscript and restored supplementary figures, selected numerical cross-checks, and the original frozen study code and protocols. The data are **derived aggregate and block-level tables**, not raw images, neural-network checkpoints, or per-model evaluator JSON files.

## Quick start

Requires Python 3.10–3.12. Extract this ZIP into a new empty folder, open a terminal in that folder, and run:

~~~bash
python -m pip install -r requirements.txt
python reproduce.py --all
~~~

Eleven figure PDFs appear in `outputs/figures/` after the command completes. The numerical and integrity report appears at `outputs/verification_report.json`. The outputs directory is **generated**; these links are to command outputs and will not exist before reproduction.

You can run the components separately:

~~~bash
python reproduce.py --check     # archive checksums and README relative links
python reproduce.py --numbers   # recompute selected archived-table statistics
python reproduce.py --figures   # regenerate every manuscript and supplementary figure
~~~

The reproduction script temporarily reconstructs the original expected input paths in an isolated directory, runs all archived figure generators, and copies their outputs into outputs/figures/. It does not download PyTorch checkpoints or depend on the original repository.

## Directory guide

- [data/](data/): readable, study-grouped CSV/JSON and compact NPZ results. The files preserve their original basenames.
- [code/figures/](code/figures/): all six figure-generator scripts (five current plus one legacy/restored) and their plotting module.
- [code/experiments/](code/experiments/): archived training/evaluation and analysis routines supplied for methodological inspection. These are **not** independent end-to-end training commands without external raw run outputs.
- [protocols/](protocols/): frozen experimental plans, including an explicitly **post hoc** architecture diagnostic protocol.
- [manifest.json](manifest.json): source commit when available, original-to-exported path mapping, SHA-256 checksums, and byte sizes of every packaged source file.
- [LICENSE](LICENSE): original project license.

## Paper-figure mapping

| Manuscript figure | Exported input group | Output |
| --- | --- | --- |
| Fig. 1 — controlled inputs and filters | Procedural renderer, no external data | fig00_overview.pdf |
| Fig. 2 — direct additivity curves | data/additivity/architecture_comparison | fig09_additivity_curves.pdf |
| Fig. 3 — intervention size and architecture | data/metric_sensitivity; data/architecture | fig06_main_results.pdf |
| Fig. 4 — spatial filter-bank specificity | data/spatial_specificity | fig07_anchor_specificity.pdf |
| Fig. 5 — additive reconstruction | data/additivity/architecture_comparison; data/additivity/spatial_controls | fig08_additivity.pdf |

The outputs listed above are generated under `outputs/figures/`.

### Restored training-dynamics and filter figures

| Figure | Archived input group | Output |
| --- | --- | --- |
| Main compact gallery | [data/filter_structure/](data/filter_structure/) | fig05_kernel_gallery_compact.pdf |
| Supplementary S1 — learning curves | [data/training_dynamics/](data/training_dynamics/) | fig01_learning.pdf |
| Supplementary S2 — patching curves | [data/robustness/](data/robustness/) | fig02_patch_size.pdf |
| Supplementary S3 — matching trajectories | [data/filter_structure/](data/filter_structure/) | fig03_matching_trajectories.pdf |
| Supplementary S4 — similarity matrices | [data/filter_structure/](data/filter_structure/) | fig04_similarity_matrices.pdf |
| Supplementary S5 — full kernel gallery | [data/filter_structure/](data/filter_structure/) | fig05_kernel_gallery.pdf |

The immutable historical inputs are `learning_curves.csv`, `full_budget_curves.csv`, `per_checkpoint.csv`, and `similarity_matrices.npz`. Both galleries use `kernel_gallery.npz` and require no PyTorch or original model checkpoints for plotting. The gallery example is `two_concepts` / TinyCNN / block 2000, epochs 0 and 200. The NPZ preserves all five condition identifiers, the original templates, ten unmodified first-layer weight arrays, and their source checksums/provenance. The matching procedure is maximum-sum one-to-one assignment on centered, unit-norm cosine similarities; visualization applies the same normalization and a shared symmetric color limit to complete and compact galleries.

**Uncertainty:** S1 and S3 show run-level mean ± one standard deviation. S2 uses archived interval bounds; S4 and S5 display a single example run without statistical uncertainty. The renderer, archived tables, and NPZ are the full supported figure-reproduction boundary.

## Numerical verification

The command recomputes the means in the intervention-budget summary from the archived per-block table. It also independently recomputes the two-concept BN2-GAP paired observed-minus-additive estimate and its conventional Student-t 95% confidence interval from 100 archived blocks. The comparison values used for verification are:

- estimate: -0.1799415521;
- 95% Student-t interval: [-0.2008225633, -0.1590605409].

Other tables are provided for transparent inspection and for figure reproduction. Some of their published bootstrap intervals, adjusted tests, and permutation analyses are **not recomputed by this entry point**; they are retained as archived values. Generating a figure from the archived results must not be confused with independently repeating the original statistical estimation.

## Reproduction boundary

**Included:** frozen protocols; manuscript figure scripts; documented model/evaluation code; aggregate and block-level result tables for the listed analyses; integrity metadata; a numerical check.

**Not included:** original raw model outputs (including per-model JSON files), training checkpoints, source datasets, GPU environments, and complete rerun environments. Those are needed to repeat all model training, evaluation, bootstraps, and post hoc analyses from the beginning. They remain in the original research repository/store, not in this submission ZIP.

Pre-specified experiments and outcome-informed post hoc diagnostics are separate in the protocols. A reader should not interpret the presence of an analysis script as evidence that its full raw-data pipeline can execute using only these derived tables.

The experiment identifiers are retained in manifest.json as provenance; the readable export paths are a presentation layer, **not new experiments or altered results**.
