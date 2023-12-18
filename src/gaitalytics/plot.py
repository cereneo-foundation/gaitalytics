from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from pandas import DataFrame

import gaitalytics.utils
import gaitalytics.files



class PlotGroup(Enum):
    KINEMATICS = "Kinematics"
    KINETICS = "Kinetics"


class BasicPlotter(ABC):
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        self.configs = configs

    @abstractmethod
    def plot(self, results: DataFrame, plot_groups: List[PlotGroup]):
        pass

    def _get_valid_data_keys(self, plot_group: PlotGroup) -> List[str]:
        keys = []
        for key in self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_PLOTS]:
            if self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_PLOTS][key]['group'] == plot_group.value:
                keys.append(key)
        return keys

    def _plot_side_by_side_figure(self, ax, key, results):
        ax.set_title(
            self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_PLOTS][key]['plot_name'],
            fontsize=self.MEDIUM_SIZE)
        left = results[(
                results.metric == f"L{self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_PLOTS][key]['modelled_name']}")]
        left.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="red", ax=ax)
        right = results[(
                results.metric == f"R{self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_PLOTS][key]['modelled_name']}")]
        right.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="green", ax=ax)
        ymin, ymax = ax.get_ylim()
        ax.vlines(x=max(left['event_frame']),
                  ymin=ymin,
                  ymax=ymax,
                  colors=['red'],
                  ls='--',
                  lw=2,
                  label='_nolegend_')
        ax.vlines(x=max(right['event_frame']),
                  ymin=ymin,
                  ymax=ymax,
                  colors=['green'],
                  ls='--',
                  lw=2,
                  label='_nolegend_')
        ax.set_xlabel("")
        ax.set_ylabel(
            self.configs[KEY_PLOT_MAPPING][KEY_PLOT_MAPPING_DATA_TYPE][
                max(left['data_type'])]['y_label'],
            fontsize=self.SMALL_SIZE)
        ax.legend(['Left', 'Right'])


class SeparatelyPicturePlot(BasicPlotter):

    def __init__(self, configs: gaitalytics.utils.ConfigProvider, plot_path: str, format: str):
        super().__init__(configs)
        self.plot_path = plot_path
        self.format = format

    def plot(self, results: DataFrame, plot_groups: List[PlotGroup]):
        for group in plot_groups:
            keys = self._get_valid_data_keys(group)
            figures = self._plot(results, keys)
            for fig in figures:
                fig.savefig(fname=f"{self.plot_path}/{fig.gca().get_title()}.{self.format}", format=self.format)
                plt.close(fig)

    def _plot(self, results: DataFrame, keys: List[str]) -> List[plt.Figure]:
        figures = []
        for key in keys:
            fig, ax = plt.subplots()
            self._plot_side_by_side_figure(ax, key, results)
            ax.legend().remove()
            fig.legend(["Left", "Right"])
            figures.append(fig)
        return figures


class PdfPlotter(BasicPlotter):

    def __init__(self, configs: gaitalytics.utils.ConfigProvider, plot_path: str, filename: str = "overview.pdf", cols: int = 4,
                 rows: int = 3):
        super().__init__(configs)
        self.plot_path = plot_path
        self.cols = cols
        self.rows = rows
        self.filename = filename

    def plot(self, results: DataFrame, data_types: List[gaitalytics.utils.PointDataType]):
        with PdfPages(f'{self.plot_path}/{self.filename}') as pdf:
            for data_type in data_types:
                figures = self._plot_data_type(data_type, results)
                for figure in figures:
                    figure.set_size_inches(11.69, 8.27)
                    pdf.savefig(figure)
                    plt.close(figure)

            d = pdf.infodict()
            d['CreationDate'] = datetime.today()
            d['ModDate'] = datetime.today()

    def _add_footer_header(self):
        ## TODO headers footers
        pass

    @staticmethod
    def _create_figure(data_type: gaitalytics.utils.PointDataType) -> Figure:
        figure = plt.figure()
        figure.suptitle(data_type.name)
        figure.subplots_adjust(hspace=0.3, wspace=0.4)
        return figure

    def _style_subplot(self, ax: Axes) -> Axes:
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(self.SMALL_SIZE)
        return ax

    def _plot_data_type(self, data_type, results):
        keys = self._get_valid_data_keys(data_type)
        total_plots = len(keys)
        total_plots_pages = (self.rows * self.cols)
        figures = [self._create_figure(data_type)]
        page_num = 0
        for plot_number in range(1, total_plots + 1):
            position = (plot_number % total_plots_pages)
            position = total_plots_pages if (position == 0) else position
            ax = self._style_subplot(figures[page_num].add_subplot(self.rows, self.cols, position))
            self._plot_side_by_side_figure(ax, keys[plot_number - 1], results)
            if position % total_plots_pages == 0:
                handels, labels = ax.get_legend_handles_labels()
                figures[page_num].legend(handels, ['Left', 'Right'])
                figures.append(self._create_figure(data_type))
                page_num += 1
            ax.legend().remove()
        return figures


KEY_PLOT_MAPPING_DATA_TYPE = 'data_types'
KEY_PLOT_MAPPING_PLOTS = 'plots'
KEY_PLOT_MAPPING = 'model_mapping_plot'
