"""Unit tests for the independently usable, provenance-preserving ZIP exporter.

Run: python -m unittest discover -s tests -v
These tests do not require latex, matplotlib, trained checkpoints, or model outputs.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


PROJECT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SubmissionPackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packager = load_module(PROJECT / "paper/build_submission_package.py", "package_exporter")
        cls.runner = load_module(PROJECT / "paper/reproducibility/reproduce.py", "archive_runner")

    def test_python_sources_parse(self):
        for path in (
            PROJECT / "paper/build_submission_package.py",
            PROJECT / "paper/reproducibility/reproduce.py",
            PROJECT / "paper/build_figures.py",
            PROJECT / "paper/prepare_kernel_gallery.py",
            PROJECT / "paper/build.py",
            PROJECT / "paper/build_supplement.py",
        ):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_repro_export_has_no_duplicate_or_unsafe_paths(self):
        export = self.packager.repro_mapping()
        exported = list(export.values())
        self.assertEqual(len(exported), len(set(exported)))
        self.assertIn("README.md", exported)
        self.assertNotIn("manifest.json", exported)  # created from inventory metadata
        self.assertIn("protocols/architecture_posthoc.md", exported)
        self.assertIn("data/additivity/architecture_comparison/B_per_block.csv", exported)
        self.assertIn("code/figures/build_main_results_figure.py", exported)
        self.assertTrue(all(not p.startswith("analysis/") for p in exported))
        self.assertTrue(all(".." not in Path(p).parts for p in exported))

    def test_legacy_gallery_and_supplement_are_fully_packaged(self):
        builder = self.packager
        repro = builder.repro_mapping()
        source = builder.source_mapping()
        self.assertEqual(len(builder.FIGURE_PDFS), 11)
        expected = {
            "results/retention_release_001/analysis/learning_curves.csv": "data/training_dynamics/learning_curves.csv",
            "analysis/exhaustive_robustness_001/full_budget_curves.csv": "data/robustness/full_budget_curves.csv",
            "analysis/kernel_similarity/results/per_checkpoint.csv": "data/filter_structure/per_checkpoint.csv",
            "analysis/kernel_similarity/results/similarity_matrices.npz": "data/filter_structure/similarity_matrices.npz",
            "analysis/kernel_similarity/results/kernel_gallery.npz": "data/filter_structure/kernel_gallery.npz",
            "paper/build_figures.py": "code/figures/build_figures.py",
        }
        for original, expected_export in expected.items():
            self.assertEqual(repro[original], expected_export)
            self.assertIn(original, source)
        for pdf in ("fig05_kernel_gallery.pdf", "fig05_kernel_gallery_compact.pdf"):
            self.assertIn(pdf, builder.FIGURE_PDFS)

    def test_manuscript_source_zip_contains_all_figure_inputs(self):
        mapping = self.packager.source_mapping()
        for path in self.packager.FIGURE_DATA:
            self.assertEqual(mapping[path], path)
        for filename in self.packager.FIGURE_PDFS:
            self.assertIn(f"paper/figures/{filename}", mapping)
        self.assertIn("literature/references.bib", mapping)
        self.assertIn("paper/sn-article-template/sn-jnl.cls", mapping)

    def test_synthetic_zip_manifest_and_tampering(self):
        builder = self.packager
        runner = self.runner
        old_root = builder.ROOT
        old_runner_root = runner.ROOT
        try:
            with tempfile.TemporaryDirectory() as location:
                directory = Path(location)
                src = directory / "src"
                src.mkdir()
                (src / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
                (src / "README.md").write_text("[Data](data/data.csv)\n", encoding="utf-8")
                builder.ROOT = src
                archive = directory / "archive.zip"
                builder.make_archive(
                    archive,
                    {"data.csv": "data/data.csv", "README.md": "README.md"},
                    manifest=True,
                )
                unpacked = directory / "unpacked"
                with zipfile.ZipFile(archive) as zf:
                    self.assertIsNone(zf.testzip())
                    zf.extractall(unpacked)
                runner.ROOT = unpacked
                runner.MANIFEST = unpacked / "manifest.json"
                report = runner.verify_inventory()
                self.assertEqual(report["manifest_files_verified"], 2)
                meta = json.loads(runner.MANIFEST.read_text(encoding="utf-8"))
                record = next(e for e in meta["files"] if e["source_path"] == "data.csv")
                self.assertEqual(
                    record["sha256"], hashlib.sha256(b"a,b\n1,2\n").hexdigest()
                )
                (unpacked / "data/data.csv").write_text("tampered", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                    runner.verify_inventory()
        finally:
            builder.ROOT = old_root
            runner.ROOT = old_runner_root
            runner.MANIFEST = old_runner_root / "manifest.json"

    def test_duplicate_and_missing_files_fail_closed(self):
        builder = self.packager
        old_root = builder.ROOT
        try:
            with tempfile.TemporaryDirectory() as root:
                builder.ROOT = Path(root)
                (builder.ROOT / "one").write_text("one")
                (builder.ROOT / "two").write_text("two")
                with self.assertRaisesRegex(ValueError, "Duplicate archive paths"):
                    builder.validate_mapping({"one": "same", "two": "same"})
                with self.assertRaises(FileNotFoundError):
                    builder.validate_mapping({"missing": "data/missing"})
        finally:
            builder.ROOT = old_root

    def test_submission_text_matches_eleven_figure_archive(self):
        supplement = (PROJECT / "paper/sn_supplement.tex").read_text(encoding="utf-8")
        readme = (PROJECT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("rebuilds all five figures", supplement)
        self.assertNotIn("regeneration of the five manuscript figures", supplement)
        self.assertIn("all eleven figure PDFs", supplement)
        self.assertIn("all eleven generated figure PDFs", readme)

    def test_epoch_80_marks_zero_penalty_in_supplementary_figures(self):
        source = (PROJECT / "paper/build_figures.py").read_text(encoding="utf-8")

        self.assertNotIn("Annealing begins (epoch 80)", source)
        self.assertEqual(source.count("Penalty reaches zero (epoch 80)"), 2)

    def test_filter_gallery_is_fixed_after_penalty_explanation(self):
        manuscript = (PROJECT / "paper/main.tex").read_text(encoding="utf-8")
        explanation = manuscript.index("Downstream parameters can therefore change")
        gallery = manuscript.index("\\includegraphics[width=0.98\\textwidth]{figures/fig05_kernel_gallery_compact.pdf}")

        self.assertLess(explanation, gallery)
        self.assertIn("\\usepackage{float}", manuscript)
        self.assertIn("\\begin{figure}[H]", manuscript[explanation:gallery])


if __name__ == "__main__":
    unittest.main()
