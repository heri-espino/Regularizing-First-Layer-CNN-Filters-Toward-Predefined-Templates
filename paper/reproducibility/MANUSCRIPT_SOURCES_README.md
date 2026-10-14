# Manuscript LaTeX sources

This archive contains the submission's LaTeX source, frozen figure inputs, figure generators, bibliography, Springer Nature class/BibTeX style, and generated figure PDFs.

## Build from this extracted directory

Install Python 3.10–3.12 dependencies listed in pyproject.toml, plus a LaTeX distribution providing pdflatex, bibtex, the standard latex packages, and xurl. Run from **this folder**, not from the original GitHub checkout:

~~~bash
python -m pip install numpy pandas scipy matplotlib seaborn pillow
python paper/build.py --clean
python paper/build_supplement.py --clean
~~~

The commands regenerate both manuscript and supplementary figures from the *included* CSV/NPZ input files and produce paper/sn_submission.pdf and paper/sn_supplement.pdf. All eleven figure PDFs are also supplied under paper/figures/ so the typeset visual assets can be inspected without rebuilding.

The figures are presentation-level regenerations from archived derived tables and frozen kernel arrays; rebuilding these sources does not repeat neural-network training or the full statistical analysis.

The main LaTeX file is paper/main.tex; the supplementary source is paper/sn_supplement.tex; the bibliography is literature/references.bib. Source paths are preserved in this archive so the original LaTeX relative references resolve. For numerical verification and experiment protocols, see the **separate** activation_patching_reproducibility.zip archive.
