import io
from unittest.mock import Mock

import matplotlib.pyplot as plt
import pytest

from homcloud.histogram import Ruler, PDHistogram
from homcloud.pdgm import SimplePDGM
from homcloud.plot_PD import PDPlotter, MarkerDrawer, AuxPlotInfo, PDColorHistogramPlotter, ZSpec


class TestPDPLotter:
    @pytest.mark.parametrize(
        ("aux_info", "key", "expected"),
        [
            (AuxPlotInfo(None, None), "Birth", "Birth"),
            (AuxPlotInfo("", "A^2"), "Death", "Death[A^2]"),
        ],
    )
    def test_label_text(self, aux_info, key, expected):
        plotter = PDPlotter(None, ZSpec.Linear(0, 1), aux_info)
        assert plotter.label_text(key) == expected


class TestMarkerDrawer:
    def test_parse_line(self):
        parse_line = MarkerDrawer.parse_line
        assert parse_line("") is None
        assert parse_line("# comment") is None
        assert parse_line("  # commnent with spacee") is None
        assert parse_line("point 0.0 1 0 1 0") == ("point", (0.0, 1.0), (0.0, 1.0, 0.0))
        assert parse_line("line 0.0 1 2 3 0 1 0") == ("line", (0.0, 1.0), (2.0, 3.0), (0.0, 1.0, 0.0))
        assert parse_line("arrow 0.0 1 2 3 0 1 0") == ("arrow", (0.0, 1.0), (2.0, 3.0), (0.0, 1.0, 0.0))
        with pytest.raises(ValueError):
            parse_line("unknown 0.0 1 2 3 0 1 0")

    def test_load(self):
        f = io.StringIO(
            """
        # comment
        point 0 1 0 0 1
        line 1 2 3 4 1 0 0
        """
        )
        assert MarkerDrawer.load(f).markers == [("point", (0, 1), (0, 0, 1)), ("line", (1, 2), (3, 4), (1, 0, 0))]

    def test_draw(self):
        marker_drawer = MarkerDrawer(
            [
                ("point", (0, 1), (0, 0, 1)),
                ("arrow", (0, 1), (2, 3), (0, 1, 0)),
                ("line", (1, 2), (3, 4), (1, 0, 0)),
            ]
        )
        ax = Mock()
        marker_drawer.draw(ax)
        ax.arrow.assert_called_once_with(0, 1, 2, 2, color=(0, 1, 0), width=0.0001, length_includes_head=True)
        ax.plot.assert_called_once_with([1, 3], [2, 4], color=(1, 0, 0))
        ax.scatter.assert_called_once_with([0], [1], color=(0, 0, 1), edgecolor="black")


@pytest.mark.integration
@pytest.mark.plotting
class Test_plot:
    def test_case_plot(self, picture_dir):
        pd = SimplePDGM(0, [0.0, 1.0, 3.0, 4.0], [1.0, 3.0, 5.0, 5.0])

        ruler = Ruler((0, 7), 64)
        histogram = PDHistogram(pd, ruler, ruler)
        fig, ax = plt.subplots()
        PDColorHistogramPlotter(histogram, ZSpec.Linear(), AuxPlotInfo(None, None)).plot(fig, ax)
        plt.savefig(str(picture_dir.joinpath("plot_PD_plot.png")))

    def test_case_plot_with_ess(self, picture_dir):
        pd = SimplePDGM(0, [0.0, 1.0, 3.0, 4.0], [1.0, 3.0, 5.0, 5.0], [2.0])

        ruler = Ruler((0, 7), 64)
        histogram = PDHistogram(pd, ruler, ruler)
        auxplotinfo = AuxPlotInfo(None, None, plot_ess=True)
        fig, ax = plt.subplots()
        PDColorHistogramPlotter(histogram, ZSpec.Linear(), auxplotinfo).plot(fig, ax)
        plt.savefig(str(picture_dir.joinpath("plot_PD_plot_with_ess.png")))

    def test_case_plot_with_ess_flipped(self, picture_dir):
        pd = SimplePDGM(0, [0.0, 1.0, 3.0, 4.0], [1.0, 3.0, 5.0, 5.0], [2.0], True)
        ruler = Ruler((0, 7), 64)
        histogram = PDHistogram(pd, ruler, ruler)
        auxplotinfo = AuxPlotInfo(None, None, plot_ess=True)
        fig, ax = plt.subplots()
        PDColorHistogramPlotter(histogram, ZSpec.Linear(), auxplotinfo).plot(fig, ax)
        plt.savefig(str(picture_dir.joinpath("plot_PD_plot_with_ess_flipped.png")))
