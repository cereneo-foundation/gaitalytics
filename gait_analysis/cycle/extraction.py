from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from btk import btkAcquisition
from pandas import DataFrame

from gait_analysis.cycle.builder import GaitCycleList, GaitCycle, define_key
from gait_analysis.event.utils import GaitEventContext
from gait_analysis.utils.c3d import AxesNames, PointDataType
from gait_analysis.utils.config import MarkerModelConfig


def define_key(configs: MarkerModelConfig, label: str, point_type: PointDataType, direction: AxesNames,
               side: GaitEventContext) -> str:
    return f"{label}.{point_type.name}.{direction.name}.{side.value}"


class BasicCyclePoint(ABC):
    EVENT_FRAME_NUMBER = "events_between"
    CYCLE_NUMBER = "cycle_number"

    def __init__(self, label: str, direction: AxesNames, data_type: PointDataType, context: GaitEventContext):
        self._event_frames = None
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

    @property
    def event_frames(self) -> DataFrame:
        return self._event_frames

    @event_frames.setter
    def event_frames(self, event_frames: DataFrame):
        self._event_frames = event_frames

    def add_event_frame(self, event_frame: int, cycle_number: int):
        if self.event_frames is None:
            prep_dict = {cycle_number: [event_frame]}
            self.event_frames = DataFrame.from_dict(data=prep_dict, orient="index", columns=[self.EVENT_FRAME_NUMBER])
            self.event_frames.index.name = self.CYCLE_NUMBER
        else:
            self.event_frames.loc[cycle_number] = event_frame

    @staticmethod
    def _get_meta_data_filename(filename: str) -> [str, PointDataType, AxesNames, GaitEventContext]:
        meta_data = filename.split("_")[1].split(".")
        label = meta_data[0]
        data_type = PointDataType[meta_data[1]]
        direction = AxesNames[meta_data[2]]
        context = GaitEventContext.get_context(meta_data[3])
        return [label, data_type, direction, context]

    @abstractmethod
    def add_cycle_data(self, data: np.array, cycle_number: int):
        pass

    @abstractmethod
    def to_csv(self, path: str, prefix: str):
        pass

    @abstractmethod
    def from_csv(self, path: str, filename: str) -> BasicCyclePoint:
        pass


class RawCyclePoint(BasicCyclePoint):
    """
    Stores data cuts of all cycles with label of the point, axes of the point, context of the event and events in cycles
    """

    def __init__(self, label: str, direction: AxesNames, data_type: PointDataType, context: GaitEventContext):
        super().__init__(label, direction, data_type, context)
        self._data = {}

    @property
    def data(self) -> Dict[int, np.array]:
        return self._data

    @data.setter
    def data(self, data: Dict[int, np.array]):
        self._data = data

    def add_cycle_data(self, data: np.array, cycle_number: int):
        self._data[cycle_number] = data

    def to_csv(self, path: str, prefix: str):
        key = define_key(self.label, self.data_type, self.direction, self.context)
        with open(f'{path}/{prefix}_{key}_raw.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            field = ["cycle_number", "event_between"]
            writer.writerow(field)
            for cycle_number in self._data:
                event_frame = self.event_frames.loc[cycle_number]
                row = np.array([cycle_number, event_frame[self.EVENT_FRAME_NUMBER]])
                row = np.concatenate((row.T, self._data[cycle_number]))
                writer.writerow(row)

    @classmethod
    def from_csv(cls, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context] = cls._get_meta_data_filename(filename)
        point = RawCyclePoint(label, direction, data_type, context)
        with open(f'{path}/{filename}', 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                cycle_number = int(float(row[0]))
                event_between = int(float(row[1]))
                data = [float(row[index]) for index in range(2, len(row)) if row]
                point.add_event_frame(event_between, cycle_number)
                point.add_cycle_data(data, cycle_number)

        return point


class CycleDataExtractor:
    def __init__(self, configs: MarkerModelConfig):
        self._configs = configs

    def extract_data(self, cycles: GaitCycleList, acq: btkAcquisition) -> Dict[str, RawCyclePoint]:
        data_list = {}
        for cycle_number in range(1, cycles.get_number_of_cycles() + 1):
            for point_index in range(0, acq.GetPointNumber()):
                point = acq.GetPoint(point_index)
                self._extract_cycle(data_list, point, cycles.right_cycles[cycle_number])
                self._extract_cycle(data_list, point, cycles.left_cycles[cycle_number])
        return data_list

    @staticmethod
    def _extract_cycle(data_list, point, cycle: GaitCycle):
        raw_data = point.GetValues()[cycle.start_frame: cycle.end_frame]
        for direction_index in range(0, len(raw_data[0])):
            label = point.GetLabel()
            direction = AxesNames.get_axes_by_index(direction_index)
            data_type = PointDataType.get_type_by_index(point.GetType())

            key = define_key(label, data_type, direction, cycle.context)
            if key not in data_list:
                data_list[key] = RawCyclePoint(
                    label,
                    direction,
                    data_type,
                    cycle.context)
            data_list[key].add_cycle_data(
                raw_data[:, direction_index], cycle.number)
            data_list[key].add_event_frame(
                cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number)
