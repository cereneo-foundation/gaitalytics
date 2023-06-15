from __future__ import annotations

import csv

from enum import Enum
from typing import Dict

import numpy as np
from btk import btkAcquisition
from pandas import DataFrame, concat, read_csv

from gait_analysis.utils.utils import define_cycle_point_file_name, get_meta_data_filename
from gait_analysis.cycle.builder import GaitCycleList, GaitCycle
from gait_analysis.utils.c3d import AxesNames, PointDataType, GaitEventContext
from gait_analysis.utils.config import ConfigProvider


class BasicCyclePoint:
    EVENT_FRAME_NUMBER = "events_between"
    CYCLE_NUMBER = "cycle_number"
    TYPE_RAW = "raw"
    TYPE_NORM = "normalised"

    def __init__(self, cycle_point_type: str,  translated_label: Enum, direction: AxesNames, data_type: PointDataType,
                 context: GaitEventContext):
        self._cycle_point_type = cycle_point_type
        self._data_table: DataFrame = None
        self._event_frames = None
        self._translated_label = translated_label
        self._direction = direction
        self._context = context
        self._data_type = data_type

    @property
    def cycle_point_type(self) -> str:
        return self._cycle_point_type

    @cycle_point_type.setter
    def cycle_point_type(self, cycle_point_type: str):
        self._cycle_point_type = cycle_point_type

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

    def get_mean_event_frame(self) -> int:
        return self.event_frames.mean(axis=1)

    @property
    def data_table(self) -> DataFrame:
        return self._data_table

    @data_table.setter
    def data_table(self, value: DataFrame):
        self._data_table = value

    def add_cycle_data(self, data: np.array, cycle_number: int):

        if self.data_table is None:
            self.data_table = self._create_table(data, cycle_number)
        else:
            if self.cycle_point_type == self.TYPE_RAW:
                self.data_table = concat([self.data_table, self._create_table(data, cycle_number)], axis=0)
            else:
                self.data_table.loc[cycle_number] = data

    def _create_table(self, data: np.array, cycle_number: int):
        df = DataFrame.from_dict({cycle_number: data}, orient="index")
        df.index.name = self.CYCLE_NUMBER
        return df

    def to_csv(self, path: str, prefix: str):
        output = self.event_frames.merge(self.data_table, on=self.CYCLE_NUMBER)
        filename = define_cycle_point_file_name(self, prefix, self.cycle_point_type)
        output.to_csv(f"{path}/{filename}")

    @classmethod
    def from_csv(cls, configs: ConfigProvider, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context, cycle_point_type, prefix] = get_meta_data_filename(filename)
        translated = configs.get_translated_label(label, data_type)
        point = BasicCyclePoint(cycle_point_type, translated, direction, data_type, context)
        data_table = read_csv(f"{path}/{filename}", index_col=cls.CYCLE_NUMBER)
        point.event_frames = DataFrame(data_table[cls.EVENT_FRAME_NUMBER])
        data_table = data_table.drop(cls.EVENT_FRAME_NUMBER, axis=1)
        point.data_table = data_table

        return point


class BufferedCyclePoint(BasicCyclePoint):
    def __init__(self, configs: ConfigProvider, path: str, filename: str):
        self._configs = configs
        self._filename = filename
        self._path = path
        self._loaded = False

    def _load_file(self):
        if not self._loaded:
            point = BasicCyclePoint.from_csv(self._configs, self._path, self._filename)
            self._cycle_point_type = point.cycle_point_type
            self._event_frames = point.event_frames
            self._translated_label = point.translated_label
            self._direction = point.direction
            self._context = point.context
            self._data_type = point.data_type
            self._data_table = point.data_table
            self._loaded = True

    @property
    def data_table(self) -> DataFrame:
        self._load_file()
        return super().data_table

    @data_table.setter
    def data_table(self, data_table: DataFrame):
        self._load_file()
        super().data_table = data_table

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
                    data_list[key] = BasicCyclePoint(
                        BasicCyclePoint.TYPE_RAW,
                        translated_label,
                        direction,
                        data_type,
                        cycle.context)
                data_list[key].add_cycle_data(
                    raw_data[:, direction_index], cycle.number)
                data_list[key].add_event_frame(
                    cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number)
