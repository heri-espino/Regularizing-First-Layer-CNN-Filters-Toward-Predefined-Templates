# Literature and BibTeX

The reusable bibliography for the manuscript is [`references.bib`](references.bib). The directory also retains the literature corpus, extracted text, and technical reading notes used during development of the study.

From the manuscript in `paper/`, the bibliography is loaded as:

```latex
\bibliography{../literature/references}
```

The current TMLR manuscript uses the official `tmlr` bibliography style vendored under `paper/tmlr/`. Only cited entries appear unless `\nocite{*}` is used.

Keys preserve the corpus naming convention so references remain stable across analyses. Some local files are preprints even when a later publication year appears in the filename; `references.bib` records the version selected for citation.

For the literature-to-experiment rationale, see [`TECHNICAL_COMPARISON.md`](TECHNICAL_COMPARISON.md).

For manuscript wording and canonical terminology, use [`TERMINOLOGY.md`](TERMINOLOGY.md) as the source of truth before coining or revising recurring terms.
