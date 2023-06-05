from abc import ABC, abstractmethod
from math import ceil
from statistics import mean
from typing import Dict

import numpy as np
from btk import btkPoint
from pandas import DataFrame

from gait_analysis.cycle.extraction import RawCyclePoint, BasicCyclePoint
from gait_analysis.utils.c3d import AxesNames


class NormalisedCyclePoint(BasicCyclePoint):

    def __init__(self, rawPoint: RawCyclePoint):
        super().__init__(rawPoint.label, rawPoint.direction, rawPoint.data_type, rawPoint.context)
        self._data_table = None

    @property
    def data_table(self) -> DataFrame:
        return self._data_table

    @data_table.setter
    def data_table(self, data_table: DataFrame):
        self._data_table = data_table

    def get_event_frame(self) -> int:
        return mean(self.get_event_frames())


    @staticmethod
    def _create_table(data: np.ndarray):
        column_names = []
        for index in range(0, len(data)):
            column_names.append(index)
        return DataFrame(data=[data], columns=np.array(column_names))

    def add_cycle_data(self, data: np.ndarray, cycle_number: int):
        if self.data_table is None:
            self.data_table = self._create_table(data)
        else:
            self.data_table.loc[cycle_number - 1] = data


class TimeNormalisationAlgorithm(ABC):

    def __init__(self, number_frames: int = 100):
        self._number_frames = number_frames

    @classmethod
    def _define_key(cls, point: btkPoint, direction_index: int) -> str:
        return f"{point.GetLabel()}.{AxesNames.get_axes_by_index(direction_index).name}"

    def normalise(self, r_data_list: Dict[str, RawCyclePoint]) -> Dict[str, NormalisedCyclePoint]:
        n_data_list = {}
        for data_key in r_data_list:
            r_cycle_point = r_data_list[data_key]
            n_cycle_point = NormalisedCyclePoint(r_cycle_point)
            for cycle_key in r_cycle_point.get_data():
                cycle_data = r_cycle_point.get_data()[cycle_key]

                interpolated_data = self._run_algorithm(cycle_data, self._number_frames)
                n_cycle_point.add_cycle_data(interpolated_data, cycle_key)

                norm_event_frame = self._define_event_frame(r_cycle_point.get_event_frames()[cycle_key],
                                                            len(cycle_data),
                                                            self._number_frames)
                n_cycle_point.add_event_frame(norm_event_frame, cycle_key)
                n_data_list[data_key] = n_cycle_point
        return n_data_list

    @abstractmethod
    def _run_algorithm(self, data: np.ndarray,
                       number_frames: int = 100) -> np.ndarray:
        pass

    @abstractmethod
    def _define_event_frame(self, event_frame: int, frame_number_cycle: int, number_frames: int = 100) -> int:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _define_event_frame(self, event_frame: int, frame_number_cycle: int, number_frames: int = 100) -> int:
        return ceil(event_frame / frame_number_cycle * number_frames)

    def _run_algorithm(self, data: np.ndarray, number_frames: int = 100) -> np.ndarray:
        times = np.arange(0, len(data), 1)
        times_new = np.linspace(0, len(data), num=100)
        # Create an interpolation function
        return np.interp(times_new, times, data)
