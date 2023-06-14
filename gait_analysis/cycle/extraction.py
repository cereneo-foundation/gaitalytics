from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict

import numpy as np
from btk import btkAcquisition
from pandas import DataFrame

import gait_analysis.utils.utils
from gait_analysis.cycle.builder import GaitCycleList, GaitCycle
from gait_analysis.utils.c3d import AxesNames, PointDataType, GaitEventContext
from gait_analysis.utils.config import ConfigProvider


class BasicCyclePoint(ABC):
    EVENT_FRAME_NUMBER = "events_between"
    CYCLE_NUMBER = "cycle_number"

    def __init__(self, translated_label: Enum, direction: AxesNames, data_type: PointDataType,
                 context: GaitEventContext):
        self._event_frames = None
        self._translated_label = translated_label
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
    def translated_label(self) -> Enum:
        return self._translated_label

    @translated_label.setter
    def translated_label(self, value: Enum):
        self._translated_label = value

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

    @abstractmethod
    def add_cycle_data(self, data: np.array, cycle_number: int):
        pass

    @abstractmethod
    def to_csv(self, path: str, prefix: str):
        pass

    @abstractmethod
    def from_csv(self, configs: ConfigProvider, path: str, filename: str) -> BasicCyclePoint:
        pass


class RawCyclePoint(BasicCyclePoint):
    """
    Stores data cuts of all cycles with label of the point, axes of the point, context of the event and events in cycles
    """

    def __init__(self, translated_label: Enum, direction: AxesNames, data_type: PointDataType,
                 context: GaitEventContext):
        super().__init__(translated_label, direction, data_type, context)
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
        filename = gait_analysis.utils.utils.define_cycle_point_file_name(self, prefix)
        with open(f"{path}/{filename}", 'w', newline='') as file:
            writer = csv.writer(file)
            field = ["cycle_number", "event_between"]
            writer.writerow(field)
            for cycle_number in self._data:
                event_frame = self.event_frames.loc[cycle_number]
                row = np.array([cycle_number, event_frame[self.EVENT_FRAME_NUMBER]])
                row = np.concatenate((row.T, self._data[cycle_number]))
                writer.writerow(row)

    @classmethod
    def from_csv(cls, configs, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context] = gait_analysis.utils.utils.get_meta_data_filename(filename)
        translation = configs.get_translated_label(label, data_type)
        point = RawCyclePoint(translation, direction, data_type, context)
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


class BufferedRawCyclePoint(RawCyclePoint):
    def __init__(self, configs: ConfigProvider, path: str, filename: str):
        self._configs = configs
        self._filename = filename
        self._path = path
        self._loaded = False


    def _load_file(self):
        if not self._loaded:
            point = RawCyclePoint.from_csv(self._configs, self._path, self._filename)
            self._event_frames = point.event_frames
            self._translated_label = point.translated_label
            self._direction = point.direction
            self._context = point.context
            self._data_type = point.data_type
            self._data = point.data
            self._loaded = True

    @property
    def data(self) -> Dict[int, np.array]:
        self._load_file()
        return super().data

    @data.setter
    def data(self, data: Dict[int, np.array]):
        self._load_file()
        super().data = data

    def add_cycle_data(self, data: np.array, cycle_number: int):
        self._load_file()
        super().add_cycle_data(data, cycle_number)

    @property
    def data_type(self) -> PointDataType:
        self._load_file()
        return super().data_type

    @data_type.setter
    def data_type(self, value: PointDataType):
        self._load_file()
        super().data_type = value

    @property
    def context(self) -> GaitEventContext:
        self._load_file()
        return super().context

    @context.setter
    def context(self, value: GaitEventContext):
        self._load_file()
        super().context = value

    @property
    def direction(self) -> AxesNames:
        self._load_file()
        return super().direction

    @direction.setter
    def direction(self, value: AxesNames):
        self._load_file()
        super().direction = value

    @property
    def translated_label(self) -> Enum:
        self._load_file()
        return super().translated_label

    @translated_label.setter
    def translated_label(self, value: Enum):
        self._load_file()
        super().translated_label = value

    @property
    def event_frames(self) -> DataFrame:
        self._load_file()
        return super().event_frames

    @event_frames.setter
    def event_frames(self, value: DataFrame):
        self._load_file()
        super().event_frames = value

    def add_event_frame(self, event_frame: int, cycle_number: int):
        self._load_file()
        super().add_event_frame(event_frame, cycle_number)

    def to_csv(self, path: str, prefix: str):
        self._load_file()
        super().to_csv(path, prefix)


class CycleDataExtractor:
    def __init__(self, configs: ConfigProvider):
        self._configs = configs

    def extract_data(self, cycles: GaitCycleList, acq: btkAcquisition) -> Dict[str, RawCyclePoint]:
        data_list = {}
        for cycle_number in range(1, cycles.get_number_of_cycles() + 1):
            for point_index in range(0, acq.GetPointNumber()):
                point = acq.GetPoint(point_index)
                if len(cycles.right_cycles) + 1 > cycle_number:
                    self._extract_cycle(data_list, point, cycles.right_cycles[cycle_number])
                if len(cycles.left_cycles) + 1 > cycle_number:
                    self._extract_cycle(data_list, point, cycles.left_cycles[cycle_number])
        return data_list

    def _extract_cycle(self, data_list, point, cycle: GaitCycle):
        raw_data = point.GetValues()[cycle.start_frame: cycle.end_frame]
        for direction_index in range(0, len(raw_data[0])):
            label = point.GetLabel()
            direction = AxesNames(direction_index)
            data_type = PointDataType(point.GetType())
            translated_label = self._configs.get_translated_label(label, data_type)
            if translated_label is not None:
                key = ConfigProvider.define_key(translated_label, data_type, direction, cycle.context)
                if key not in data_list:
                    data_list[key] = RawCyclePoint(
                        translated_label,
                        direction,
                        data_type,
                        cycle.context)
                data_list[key].add_cycle_data(
                    raw_data[:, direction_index], cycle.number)
                data_list[key].add_event_frame(
                    cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number)
