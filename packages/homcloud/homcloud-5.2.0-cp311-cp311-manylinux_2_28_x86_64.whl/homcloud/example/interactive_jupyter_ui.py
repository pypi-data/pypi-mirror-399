import collections

import numpy as np
from IPython.display import display
import ipywidgets
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector


class InteractivePDUI:
    def __init__(self, pd):
        self.pd = pd
        # セレクターで選択された矩形領域内にある生成消滅対を保持する変数
        self.selected_pairs = []
        # ウィジットを保持しておく場所を準備する
        self.widgets = collections.namedtuple(
            "Widgets",
            [
                "x_range",
                "y_range",
                "link_range_checkbox",
                "link_range",
                "x_bins",
                "y_bins",
                "link_bins_checkbox",
                "link_bins",
                "colorbar_type",
                "colorbar_max",
                "num_pairs_in_rectangle",
                "output",
            ],
        )
        self.max_birthdeath = np.max([np.max(pd.births), np.max(pd.deaths)])
        self.min_birthdeath = np.min([np.min(pd.births), np.min(pd.deaths)])
        self.selector = None

    @property
    def output(self):
        return self.widgets.output

    def build(self):
        self.setup_matplotlib_figure()
        self.build_widgets()
        self.arrange_widgets()
        self.bind_gui_events()
        self.plot()

    def setup_matplotlib_figure(self):
        plt.close("all")
        self.fig = plt.figure(layout="compressed")
        self.fig.canvas.header_visible = False

    def build_widgets(self):
        self.widgets.output = ipywidgets.Output()
        self.widgets.x_range = self.build_range_slider("Birth Range:")
        self.widgets.y_range = self.build_range_slider("Death Range:")
        self.widgets.link_range_checkbox = ipywidgets.Checkbox(value=True, description="Sync Range")
        self.widgets.x_bins = self.build_bins_slider("Birth Bins:")
        self.widgets.y_bins = self.build_bins_slider("Death Bins:")
        self.widgets.link_bins_checkbox = ipywidgets.Checkbox(value=True, description="Sync Bins")
        self.set_range_link()
        self.set_bins_link()

        self.widgets.colorbar_type = self.build_colorbar_type_radiobuttons()
        self.widgets.colorbar_max = self.build_colorbar_max_textbox()

        self.widgets.num_pairs_in_rectangle = self.build_num_pairs_in_rectable_label()

    def build_range_slider(self, description):
        return ipywidgets.FloatRangeSlider(
            value=self.initial_range_slider(),
            min=self.min_range_slider(),
            max=self.max_range_slider(),
            step=self.step_range_slider(),
            description=description,
            continuous_update=False,
        )

    def initial_range_slider(self):
        return [self.min_birthdeath, self.max_birthdeath]

    def min_range_slider(self):
        return self.min_birthdeath - (self.max_birthdeath - self.min_birthdeath) / 2

    def max_range_slider(self):
        return self.max_birthdeath + (self.max_birthdeath - self.min_birthdeath) / 2

    def step_range_slider(self):
        return (self.max_birthdeath - self.min_birthdeath) / 100

    def build_bins_slider(self, description):
        return ipywidgets.IntSlider(
            value=128,
            min=8,
            max=256,
            step=1,
            description=description,
            continuous_update=False,
        )

    def set_range_link(self):
        self.widgets.link_range = ipywidgets.dlink((self.widgets.x_range, "value"), (self.widgets.y_range, "value"))

    def set_bins_link(self):
        self.widgets.link_bins = ipywidgets.dlink((self.widgets.x_bins, "value"), (self.widgets.y_bins, "value"))

    def build_colorbar_type_radiobuttons(self):
        return ipywidgets.RadioButtons(
            options=["linear", "log", "loglog"], value="log", orientation="horizontal", description="colorbar"
        )

    def build_colorbar_max_textbox(self):
        return ipywidgets.FloatText(
            value=0, description="Colorbar max (0 for adaptive max value):", style={"description_width": "initial"}
        )

    # 範囲選択セレクターで指定された矩形領域の生成消滅対の個数を表示するウィジェット
    def build_num_pairs_in_rectable_label(self):
        return ipywidgets.Label(
            value=self.text_of_num_pairs_in_rectangle(),
            style={"description_width": "initial"},
        )

    # 矩形領域の生成消滅対の個数を数える関数
    def text_of_num_pairs_in_rectangle(self):
        n = len(self.selected_pairs)
        return f"Number of pairs in rectangular selection: {n}"

    def arrange_widgets(self):
        layout = ipywidgets.VBox(
            [
                ipywidgets.HBox([self.widgets.x_range, self.widgets.y_range, self.widgets.link_range_checkbox]),
                ipywidgets.HBox([self.widgets.x_bins, self.widgets.y_bins, self.widgets.link_bins_checkbox]),
                ipywidgets.HBox([self.widgets.colorbar_type, self.widgets.colorbar_max]),
                self.widgets.num_pairs_in_rectangle,
                self.widgets.output,
            ]
        )
        display(layout)

    def bind_gui_events(self):
        self.widgets.x_range.observe(self.replot)
        self.widgets.y_range.observe(self.replot)
        self.widgets.x_bins.observe(self.replot)
        self.widgets.y_bins.observe(self.replot)
        self.widgets.colorbar_type.observe(self.replot)
        self.widgets.colorbar_max.observe(self.replot)
        self.widgets.link_range_checkbox.observe(self.toggle_range_link)
        self.widgets.link_bins_checkbox.observe(self.toggle_bins_link)

    def replot(self, event):
        # with self.output:
        #     print(event)
        if event["name"] == "value":
            self.plot()

    def plot(self):
        self.invalidate_selector()
        self.fig.clear()
        self.ax = self.fig.gca()
        self.pd.histogram(
            self.widgets.x_range.value,
            self.widgets.x_bins.value,
            self.widgets.y_range.value,
            self.widgets.y_bins.value,
        ).plot(
            colorbar={
                "type": self.widgets.colorbar_type.value,
                "max": self.colorbar_max_value(),
            },
            ax=self.ax,
        )
        self.setup_selector()
        self.fig.canvas.draw()

    def invalidate_selector(self):
        if self.selector:
            self.selector.set_active(False)

    def setup_selector(self):
        self.selector = RectangleSelector(
            self.ax,
            self.select_rectangle,
            useblit=True,
            button=[1],
            interactive=True,
        )

    def colorbar_max_value(self):
        return None if self.widgets.colorbar_max.value == 0.0 else self.widgets.colorbar_max.value

    def select_rectangle(self, eclick, erelease):
        # with self.output:
        #     print(eclick)
        #     print(erelease)
        xmin, xmax = sorted([eclick.xdata, erelease.xdata])
        ymin, ymax = sorted([eclick.ydata, erelease.ydata])
        self.selected_pairs = self.pd.pairs_in_rectangle(xmin, xmax, ymin, ymax)
        self.widgets.num_pairs_in_rectangle.value = self.text_of_num_pairs_in_rectangle()

    def toggle_range_link(self, event):
        if event["name"] != "value":
            return

        if event["new"]:
            self.set_range_link()
        else:
            self.widgets.link_range.unlink()

    def toggle_bins_link(self, event):
        if event["name"] != "value":
            return

        if event["new"]:
            self.set_bins_link()
        else:
            self.widgets.link_bins.unlink()
