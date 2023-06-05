from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from btk import btkAcquisition, btkPoint

from gait_analysis.cycle.builder import GaitCycleList, GaitCycle
from gait_analysis.event.utils import GaitEventContext
from gait_analysis.utils.c3d import AxesNames, PointDataType


class BasicCyclePoint(ABC):
    def __init__(self, label: str, direction: AxesNames, data_type: PointDataType, context: GaitEventContext):
        self._event_frames = {}
        self._label = label
        self._direction = direction
        self._context = context
        self._data_type = data_type

    @property
    def data_type(self) -> PointDataType:
        return self._data_type

    @data_type.setter
    def data_type(self, value: PointDataType):
        self._data_type = value

    @property
    def context(self) -> GaitEventContext:
        return self._context

    @context.setter
    def context(self, value: GaitEventContext):
        self._context = value

    @property
    def direction(self) -> AxesNames:
        return self._direction

    @direction.setter
    def direction(self, value: AxesNames):
        self._direction = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = value

    def get_event_frames(self) -> Dict[int, int]:
        return self._event_frames

    def add_event_frame(self, event_frame: int, cycle_number: int):
        self._event_frames[cycle_number] = event_frame

    @abstractmethod
    def add_cycle_data(self, data: np.ndarray, cycle_number: int):
        pass


class RawCyclePoint(BasicCyclePoint):
    """
    Stores data cuts of all cycles with label of the point, axes of the point, context of the event and events in cycles
    """

    def __init__(self, label: str, direction: AxesNames, data_type: PointDataType, context: GaitEventContext):
        super().__init__(label, direction, data_type, context)
        self._data = {}
        self._event_frames = {}

    def get_data(self) -> Dict[int, np.ndarray]:
        return self._data

    def add_cycle_data(self, data: np.ndarray, cycle_number: int):
        self._data[cycle_number] = data


class CycleDataExtractor:

    @classmethod
    def _define_key(cls, point: btkPoint, direction_index: int, side: str) -> str:
        return f"{point.GetLabel()}.{AxesNames.get_axes_by_index(direction_index).name}.{side}"

    def extract_data(self, cycles: GaitCycleList, acq: btkAcquisition) -> Dict[str, RawCyclePoint]:
        data_list = {}
        for cycle_number in range(1, cycles.get_number_of_cycles()+1):
            for point_index in range(0, acq.GetPointNumber()):
                point = acq.GetPoint(point_index)
                self._extract_cycle(data_list, point, cycles.right_cycles[cycle_number])
                self._extract_cycle(data_list, point, cycles.left_cycles[cycle_number])
        return data_list

    def _extract_cycle(self, data_list, point, cycle: GaitCycle):
        raw_data = point.GetValues()[cycle.start_frame: cycle.end_frame]
        for direction_index in range(0, len(raw_data[0])):
            key = self._define_key(point, direction_index, cycle.context.value)
            if key not in data_list:
                data_list[key] = RawCyclePoint(
                    point.GetLabel(),
                    AxesNames.get_axes_by_index(direction_index),
                    PointDataType.get_type_by_index(point.GetType()),
                    GaitEventContext.get_context(cycle.context.value))
            data_list[key].add_cycle_data(
                raw_data[:, direction_index], cycle.number)
            data_list[key].add_event_frame(
                cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number)
