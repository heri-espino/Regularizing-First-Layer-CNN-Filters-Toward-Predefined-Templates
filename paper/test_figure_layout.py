"""Regression checks for publication-figure layout and typography."""
from __future__ import annotations

import importlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import matplotlib.pyplot as plt
import matplotlib as mpl


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
        top_xlabel = word(words, "Intervention")
        self.assertGreater(
            float(header["y0"]) - float(top_xlabel["y1"]),
            3.0,
            "Panel-b header must clear the top-row x-axis labels.",
        )

    def test_anchor_header_b_clears_top_x_axis_labels(self) -> None:
        path = self.build_to_temp("build_anchor_specificity_figure", "fig07_layout_test.pdf")
        words = pdf_words(path)
        header = word(words, "Channels")
        top_xlabel = word(words, "Difference:")
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

    def test_overview_channel_contribution_labels_clear_downstream_block(self) -> None:
        path = self.build_to_temp("build_overview_figure", "fig00_labels_test.pdf")
        words = pdf_words(path)
        downstream = word(words, "downstream")
        for label in ("retain", "copy"):
            self.assertLess(
                float(word(words, label)["x1"]),
                float(downstream["x0"]),
                f"The {label!r} label must clear the downstream block horizontally.",
            )
        self.assertLess(float(word(words, "retain")["y1"]), float(downstream["y0"]))
        self.assertGreater(float(word(words, "copy")["y0"]), float(downstream["y1"]))

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

    def test_style_defines_consistent_observed_and_additive_roles(self) -> None:
        import plot_style

        self.assertTrue(
            hasattr(plot_style, "ROLE_STYLES"),
            "The shared style must define cross-figure observed/additive semantics.",
        )
        roles = getattr(plot_style, "ROLE_STYLES", {})
        self.assertEqual(roles["observed"]["color"], "#0072B2")
        self.assertEqual(roles["additive"]["color"], "#D55E00")
        self.assertNotEqual(roles["observed"]["linestyle"], roles["additive"]["linestyle"])
        self.assertNotEqual(roles["observed"]["marker"], roles["additive"]["marker"])

    def test_additivity_curves_use_shared_role_styles(self) -> None:
        import build_additivity_curves_figure as figure
        import plot_style

        rows = figure.read_csv(figure.CURVE_TABLE)
        fig, ax = plt.subplots()
        try:
            figure.draw_delta_panel(ax, rows, "tiny_gmp", "Tiny - GMP")
            lines = {line.get_label(): line for line in ax.get_lines()}
            for label, role in (("Observed", "observed"), ("Additive reconstruction", "additive")):
                expected = plot_style.ROLE_STYLES[role]
                self.assertIn(label, lines)
                self.assertEqual(lines[label].get_color(), expected["color"])
                self.assertEqual(lines[label].get_marker(), expected["marker"])
                self.assertEqual(lines[label].get_linestyle(), expected["linestyle"])
        finally:
            plt.close(fig)

    def test_style_uses_visible_black_major_ticks(self) -> None:
        import plot_style

        plot_style.apply_paper_style()
        self.assertTrue(mpl.rcParams["xtick.bottom"])
        self.assertTrue(mpl.rcParams["ytick.left"])
        self.assertEqual(mpl.rcParams["xtick.color"], mpl.rcParams["axes.edgecolor"])
        self.assertEqual(mpl.rcParams["ytick.color"], mpl.rcParams["axes.edgecolor"])
        self.assertGreaterEqual(mpl.rcParams["xtick.major.size"], 4.0)
        self.assertGreaterEqual(mpl.rcParams["ytick.major.size"], 4.0)
        self.assertLessEqual(mpl.rcParams["xtick.major.width"], 0.65)
        self.assertLessEqual(mpl.rcParams["ytick.major.width"], 0.65)

    def test_tick_marks_are_hidden_when_their_labels_are_hidden(self) -> None:
        import plot_style

        plot_style.apply_paper_style()
        fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
        try:
            fig.canvas.draw()
            plot_style.synchronize_tick_visibility(fig)
            self.assertFalse(any(tick.tick1line.get_visible() for tick in top.xaxis.majorTicks))
            self.assertTrue(any(tick.tick1line.get_visible() for tick in bottom.xaxis.majorTicks))
        finally:
            plt.close(fig)

    def test_additivity_curve_panels_show_grid_in_both_directions(self) -> None:
        import build_additivity_curves_figure as figure

        rows = figure.read_csv(figure.CURVE_TABLE)
        fig, ax = plt.subplots()
        try:
            figure.draw_delta_panel(ax, rows, "tiny_gmp", "Tiny - GMP")
            self.assertTrue(any(line.get_visible() for line in ax.get_xgridlines()))
            self.assertTrue(any(line.get_visible() for line in ax.get_ygridlines()))
        finally:
            plt.close(fig)

    def test_main_results_forest_is_grouped_without_horizontal_tick_clutter(self) -> None:
        import build_main_results_figure as figure
        import plot_style

        plot_style.apply_paper_style()
        rows = figure.read_csv(figure.ARCH_TABLE)
        selected = figure.architecture_rows(rows, figure.ARCH_METRICS[0][0])
        fig, ax = plt.subplots()
        try:
            figure.draw_forest(ax, selected, "Metric", "#0072B2", show_labels=True)
            y = [tick.get_position()[1] for tick in ax.get_yticklabels()]
            gaps = [left - right for left, right in zip(y, y[1:])]

            self.assertEqual(len(figure.ARCH_GROUPS), 5)
            expected_boundaries = {1, 5, 9, 11}
            self.assertEqual(
                {index for index, gap in enumerate(gaps) if gap > 1.0},
                expected_boundaries,
            )
            self.assertGreaterEqual(len(ax.patches), 2)
            self.assertTrue(any(line.get_visible() for line in ax.get_xgridlines()))
            self.assertFalse(any(line.get_visible() for line in ax.get_ygridlines()))
            self.assertTrue(
                all(tick.tick1line.get_markersize() == 0 for tick in ax.yaxis.majorTicks)
            )
        finally:
            plt.close(fig)

    def test_main_results_forest_uses_aligned_label_columns(self) -> None:
        import build_main_results_figure as figure
        import plot_style

        plot_style.apply_paper_style()
        rows = figure.read_csv(figure.ARCH_TABLE)
        selected = figure.architecture_rows(rows, figure.ARCH_METRICS[0][0])
        fig, ax = plt.subplots()
        try:
            figure.draw_forest(ax, selected, "Metric", "#0072B2", show_labels=True)
            architecture = [text for text in ax.texts if text.get_gid() == "architecture-label"]
            pooling = [text for text in ax.texts if text.get_gid() == "pooling-label"]

            self.assertEqual(len(architecture), len(figure.ARCH_ORDER))
            self.assertEqual(len(pooling), len(figure.ARCH_ORDER))
            self.assertEqual(len({text.get_position()[0] for text in architecture}), 1)
            self.assertEqual(len({text.get_position()[0] for text in pooling}), 1)
            self.assertEqual(
                [text.get_position()[1] for text in architecture],
                [text.get_position()[1] for text in pooling],
            )
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
