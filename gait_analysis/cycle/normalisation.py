from abc import ABC, abstractmethod
from typing import List

import numpy as np
from btk import btkAcquisition, btkPoint

from gait_analysis.cycle.builder import GaitCycle
from pandas import DataFrame


class NormalisedPoint:
    _HEADER_PREFIX_FRAME = "Frame "
    _HEADER_PREFIX_CYCLE = "Cycle "

    def __init__(self, label: str, direction: str, side: str):
        self.label = label
        self.direction = direction
        self.side = side

    def _create_table(self, data: np.ndarray):
        column_names = []
        for index in range(0, len(data)):
            column_names.append(f"{self._HEADER_PREFIX_FRAME}{index}")
        return DataFrame(data=data, columns=column_names)

    def add_cycle_data(self, data: np.ndarray, cycle_number: int):
        data_frame = self._create_table(data)
        if self.table is not None:
            self.table.append(data_frame)
        else:
            self.table = data_frame


class TimeNormalisationAlgorithm(ABC):

    def __init__(self):

        pass

    def _define_key(self, point: btkPoint, direction_index: int, side: str) -> str:
        return f"{point.GetLabel()}.{direction_index}.{side}"

    def normalise(self, acq: btkAcquisition, cycles: List[GaitCycle]) -> {}:
        list_of_data = {}
        for point_index in range(0, acq.GetPointNumber()):
            for side in cycles:
                interpolated_data_dict = {}
                point = acq.GetPoint(point_index)
                for cycle in cycles[side]:
                    interpolated_data = self._run_algorithm(point.GetValues(), cycle.start_frame, cycle.end_frame)
                    for direction_index in range(0, len(interpolated_data)):
                        if not self._define_key(point, direction_index, side) in list_of_data:
                            list_of_data[self._define_key(point, direction_index, side)] = NormalisedPoint(
                                point.GetLabel(), direction_index, side)
                        list_of_data[self._define_key(point, direction_index, side)].add_cycle_data(
                            interpolated_data[direction_index].tolist(), cycle.number)

                point.GetLabel()

    @abstractmethod
    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        times = np.arange(0, end_frame - start_frame, 1)
        times_new = np.linspace(0, end_frame - start_frame, num=100)

        interpolated_data = []
        # Create an interpolation function
        for i in range(0, len(data[0])):
            interpolated_data.append(np.interp(times_new, times, data[start_frame:end_frame, i]))

        return np.array(interpolated_data)
