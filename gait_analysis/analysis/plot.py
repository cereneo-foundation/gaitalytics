import math
from abc import ABC, abstractmethod
from configparser import ConfigParser

from matplotlib import pyplot as plt
from pandas import DataFrame

SETTINGS_SECTION_NAME = 'model_mapping'


class BasicPlotter(ABC):

    def __init__(self, configs: dict):
        self.configs = configs

    def plot(self, results: DataFrame) -> plt.Figure:
        figures = []
        for key in self.configs[SETTINGS_SECTION_NAME]:
            fig, ax = plt.subplots()
            left = results[(results.metric == f"L{self.configs[SETTINGS_SECTION_NAME][key]['modelled_name']}")]
            left.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="red", ax=ax)

            right = results[(results.metric == f"R{self.configs[SETTINGS_SECTION_NAME][key]['modelled_name']}")]
            right.plot(x="frame_number", y=['mean'], yerr='sd', kind='line', color="green", ax=ax)

            ymin, ymax = ax.get_ylim()
            ax.vlines(x=[left['event_frame'][0],
                         right['event_frame'][0]],
                      ymin=ymin,
                      ymax=ymax,
                      colors=['red', 'green'],
                      ls='--',
                      lw=2)

            ax.get_legend().remove()
            ax.set_ylabel("Degree")
            ax.set_xlabel("Frame")

            fig.legend(["Left", "Right"])
            fig.suptitle(self.configs[SETTINGS_SECTION_NAME][key]['plot_name'])
            figures.append(fig)
        return figures
        # plt.fill_between(x=left.frame_number.values,
        #                y1=left.sd_up.values,
        #               y2=left.sd_down.values)
