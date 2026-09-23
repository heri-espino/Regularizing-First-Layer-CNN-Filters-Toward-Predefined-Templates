"""Regression checks for publication-figure layout and typography."""
from __future__ import annotations

import importlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


PAPER = Path(__file__).resolve().parent
if str(PAPER) not in sys.path:
    sys.path.insert(0, str(PAPER))


def pdf_words(path: Path) -> list[dict[str, float | str]]:
    """Extract word bounding boxes with Poppler's layout-aware XML output."""
    xml = subprocess.check_output(
        ["pdftotext", "-bbox", str(path), "-"], text=True, encoding="utf-8"
    )
    return [
        {
            "text": text,
            "x0": float(x0),
            "y0": float(y0),
            "x1": float(x1),
            "y1": float(y1),
        }
        for x0, y0, x1, y1, text in re.findall(
            r'<word xMin="([^"]+)" yMin="([^"]+)" '
            r'xMax="([^"]+)" yMax="([^"]+)">([^<]+)</word>',
            xml,
        )
    ]


def word(words: list[dict[str, float | str]], text: str, occurrence: int = 0) -> dict[str, float | str]:
    matches = [item for item in words if item["text"] == text]
    if len(matches) <= occurrence:
        raise AssertionError(f"Could not find word {text!r} occurrence {occurrence}")
    return matches[occurrence]


class FigureLayoutTests(unittest.TestCase):
    def build_to_temp(self, module_name: str, filename: str) -> Path:
        module = importlib.import_module(module_name)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / filename
            original_out = module.OUT
            module.OUT = output
            try:
                module.build_figure()
            finally:
                module.OUT = original_out
            persistent = Path(tempfile.gettempdir()) / filename
            persistent.write_bytes(output.read_bytes())
        return persistent

    def test_main_results_header_b_clears_top_x_axis_labels(self) -> None:
        path = self.build_to_temp("build_main_results_figure", "fig06_layout_test.pdf")
        words = pdf_words(path)
        header = word(words, "Architecture")
        top_xlabel = word(words, "Patched")
        self.assertGreater(
            float(header["y0"]) - float(top_xlabel["y1"]),
            3.0,
            "Panel-b header must clear the top-row x-axis labels.",
        )

    def test_anchor_header_b_clears_top_x_axis_labels(self) -> None:
        path = self.build_to_temp("build_anchor_specificity_figure", "fig07_layout_test.pdf")
        words = pdf_words(path)
        header = word(words, "Selected-channel")
        top_xlabel = word(words, "Structured", occurrence=0)
        self.assertGreater(
            float(header["y0"]) - float(top_xlabel["y1"]),
            3.0,
            "Panel-b header must clear the top-row x-axis labels.",
        )

    def test_overview_patching_annotation_clears_downstream_note(self) -> None:
        path = self.build_to_temp("build_overview_figure", "fig00_layout_test.pdf")
        words = pdf_words(path)
        replacement = word(words, "channels")
        downstream = word(words, "Downstream")
        self.assertGreater(
            float(downstream["y0"]) - float(replacement["y1"]),
            3.0,
            "The patching annotation must not collide with the downstream note.",
        )

    def test_overview_patching_panel_is_proportionate_to_the_data_panels(self) -> None:
        path = self.build_to_temp("build_overview_figure", "fig00_width_test.pdf")
        title = word(pdf_words(path), "First-layer")
        self.assertGreater(
            float(title["x0"]),
            270.0,
            "Panel (c) must not dominate the overall figure width.",
        )

    def test_overview_channel_contribution_labels_clear_the_state_stacks(self) -> None:
        path = self.build_to_temp("build_overview_figure", "fig00_labels_test.pdf")
        words = pdf_words(path)
        for label in ("retain", "copy"):
            self.assertLess(
                float(word(words, label)["x0"]),
                400.0,
                f"The {label!r} label must remain near its source stack.",
            )

    def test_overview_downstream_block_aligns_with_hybrid_state(self) -> None:
        path = self.build_to_temp("build_overview_figure", "fig00_downstream_test.pdf")
        downstream = word(pdf_words(path), "downstream")
        self.assertGreater(
            float(downstream["y0"]),
            102.0,
            "The downstream block must be vertically aligned with H_S.",
        )

    def test_layout_figures_embed_latin_modern_body_text(self) -> None:
        path = self.build_to_temp("build_main_results_figure", "fig06_font_test.pdf")
        fonts = subprocess.check_output(["pdffonts", str(path)], text=True, encoding="utf-8")
        self.assertIn("LMRoman", fonts)
        self.assertNotIn("CMUSerif", fonts)


if __name__ == "__main__":
    unittest.main()
