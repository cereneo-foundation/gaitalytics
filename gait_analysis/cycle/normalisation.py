from abc import ABC, abstractmethod
from math import ceil
from typing import Dict, Set

import numpy as np

from gait_analysis.cycle.extraction import BasicCyclePoint
from gait_analysis.utils.c3d import PointDataType


class TimeNormalisationAlgorithm(ABC):

    def __init__(self, number_frames: int = 100,
                 data_type_filter: Set[PointDataType] = {PointDataType.Angles,
                                                         PointDataType.Forces,
                                                         PointDataType.Moments,
                                                         PointDataType.Power,
                                                         PointDataType.Scalar,
                                                         PointDataType.Reaction}):
        self._number_frames = number_frames
        self._data_type_fiter = data_type_filter

    def normalise(self, r_data_list: Dict[str, BasicCyclePoint]) -> Dict[str, BasicCyclePoint]:
        n_data_list = {}
        for data_key in r_data_list:
            r_cycle_point = r_data_list[data_key]
            if r_cycle_point.data_type in self._data_type_fiter:
                n_cycle_point = BasicCyclePoint(BasicCyclePoint.TYPE_NORM, r_cycle_point.translated_label,
                                                r_cycle_point.direction, r_cycle_point.data_type,
                                                r_cycle_point.context)
                for cycle_key in r_cycle_point.data_table:
                    cycle_data = r_cycle_point.data_table.iloc[cycle_key].to_list()

                    interpolated_data = self._run_algorithm(cycle_data, self._number_frames)
                    n_cycle_point.add_cycle_data(interpolated_data, cycle_key)

                    norm_event_frame = self._define_event_frame(
                        r_cycle_point.event_frames.iloc[cycle_key][BasicCyclePoint.EVENT_FRAME_NUMBER],
                        len(cycle_data),
                        self._number_frames)
                    n_cycle_point.add_event_frame(norm_event_frame, cycle_key)
                    n_data_list[data_key] = n_cycle_point
        return n_data_list

    @abstractmethod
    def _run_algorithm(self, data: np.array,
                       number_frames: int = 100) -> np.array:
        pass

    @abstractmethod
    def _define_event_frame(self, event_frame: int, frame_number_cycle: int, number_frames: int = 100) -> int:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _define_event_frame(self, event_frame: int, frame_number_cycle: int, number_frames: int = 100) -> int:
        return ceil(event_frame / frame_number_cycle * number_frames)

    def _run_algorithm(self, data: np.array, number_frames: int = 100) -> np.array:
        times = np.arange(0, len(data), 1)
        times_new = np.linspace(0, len(data), num=100)
        return np.interp(times_new, times, data)
