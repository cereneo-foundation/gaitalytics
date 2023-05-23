from abc import ABC, abstractmethod
from typing import List

from matplotlib import pyplot as plt
from pandas import DataFrame
from gait_analysis.utils.c3d import DataType

SETTINGS_SECTION_NAME = 'model_mapping'


class BasicPlotter(ABC):

    def __init__(self, configs: dict):
        self.configs = configs

    def plot_figures_separately(self, results: DataFrame, data_type: DataType) -> List[plt.Figure]:
        figures = []
        for key in self.configs[SETTINGS_SECTION_NAME]:
            if self.configs[SETTINGS_SECTION_NAME][key]['data_type'] == data_type.value:
                fig, ax = plt.subplots()
                self._plot_side_by_side_figure(ax, key, results)

                fig.legend(["Left Event", "Right Event", "Left", "Right"])
                fig.suptitle(self.configs[SETTINGS_SECTION_NAME][key]['plot_name'])
                figures.append(fig)
        return figures
        # plt.fill_between(x=left.frame_number.values,
        #                y1=left.sd_up.values,
        #               y2=left.sd_down.values)

    def _plot_side_by_side_figure(self, ax, key, results):
        left = results[(results.metric == f"L{self.configs[SETTINGS_SECTION_NAME][key]['modelled_name']}")]
        left.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="red", ax=ax)
        right = results[(results.metric == f"R{self.configs[SETTINGS_SECTION_NAME][key]['modelled_name']}")]
        right.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="green", ax=ax)
        ymin, ymax = ax.get_ylim()
        ax.vlines(x=left['event_frame'][0],
                  ymin=ymin,
                  ymax=ymax,
                  colors=['red'],
                  ls='--',
                  lw=2)
        ax.vlines(x=right['event_frame'][0],
                  ymin=ymin,
                  ymax=ymax,
                  colors=['green'],
                  ls='--',
                  lw=2)
        ax.get_legend().remove()
        ax.set_ylabel("Degree")
        ax.set_xlabel("Frame")
