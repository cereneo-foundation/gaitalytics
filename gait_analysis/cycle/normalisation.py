from abc import ABC, abstractmethod
from typing import List

import numpy as np
from btk import btkAcquisition, btkPoint

from gait_analysis.cycle.builder import GaitCycle
from gait_analysis.utils.c3d import AxesNames
from pandas import DataFrame


class NormalisedPoint:

    def __init__(self, label: str, direction: str, data_type: int):
        self.label = label
        self.direction = direction
        self.table = None
        self.data_type = data_type
        self.event_frames = []

    def _create_table(self, data: np.ndarray):
        column_names = []
        for index in range(0, len(data)):
            column_names.append(index)
        return DataFrame(data=[data], columns=np.array(column_names))

    def add_cycle_data(self, data: np.ndarray, cycle_number: int):
        if self.table is not None:
            self.table.loc[cycle_number] = data
        else:
            data_frame = self._create_table(data)
            self.table = data_frame

    def add_event_frame(self, event_frame: int):
        self.event_frames.append(event_frame)


class TimeNormalisationAlgorithm(ABC):

    def __init__(self):

        pass

    @classmethod
    def _define_key(cls, point: btkPoint, direction_index: int) -> str:
        return f"{point.GetLabel()}.{AxesNames.get_axes_by_index(direction_index).name}"

    def normalise(self, acq: btkAcquisition, cycles: List[GaitCycle]) -> {}:
        data_list = {}
        for point_index in range(0, acq.GetPointNumber()):
            point = acq.GetPoint(point_index)
            if point.GetType() > 0:
                for side in cycles:
                    if point.GetLabel()[0] == side[0]:  # TODO: Name convention maybe different in other models
                        for cycle in cycles[side]:
                            interpolated_data = self._run_algorithm(point.GetValues(), cycle.start_frame,
                                                                    cycle.end_frame)
                            for direction_index in range(0, len(interpolated_data)):
                                if not self._define_key(point, direction_index) in data_list:
                                    data_list[self._define_key(point, direction_index)] = NormalisedPoint(
                                        point.GetLabel(), direction_index, point.GetType())
                                data_list[self._define_key(point, direction_index)].add_cycle_data(
                                    interpolated_data[direction_index], cycle.number)
                                data_list[self._define_key(point, direction_index)].add_event_frame(
                                    self._define_event_frame(cycle))

        return data_list

    @abstractmethod
    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        pass

    @abstractmethod
    def _define_event_frame(self, cycle: GaitCycle, number_frames: int = 100) -> int:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _define_event_frame(self, cycle: GaitCycle, number_frames: int = 100) -> int:
        return (cycle.unusedEvents.GetFrame() - cycle.start_frame) / (cycle.end_frame - cycle.start_frame) * 100

    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        times = np.arange(0, end_frame - start_frame, 1)
        times_new = np.linspace(0, end_frame - start_frame, num=100)

        interpolated_data = []
        # Create an interpolation function
        for i in range(0, len(data[0])):
            interpolated_data.append(np.interp(times_new, times, data[start_frame:end_frame, i]))

        return np.array(interpolated_data)
