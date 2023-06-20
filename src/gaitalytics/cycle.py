from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from enum import Enum
from math import ceil
from typing import Dict, List

import numpy as np
from btk import btkAcquisition, btkEvent
from pandas import DataFrame, concat, read_csv

from .c3d import AxesNames, PointDataType, GaitEventContext, GaitEventLabel
from .events import AbstractEventAnomalyChecker, find_next_event
from .utils import ConfigProvider


# Cycle Builder
class CycleBuilder(ABC):

    def __init__(self, event_anomaly_checker: AbstractEventAnomalyChecker):
        self.eventAnomalyChecker = event_anomaly_checker

    def build_cycles(self, aqc: btkAcquisition) -> GaitCycleList:
        if aqc.GetEventNumber() < 1:
            raise AttributeError("No Events in File")
        else:
            [detected, detail_tuple] = self.eventAnomalyChecker.check_events(aqc)
            if detected:
                raise RuntimeError(detail_tuple)

        return self._build(aqc)

    @abstractmethod
    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        pass


class EventCycleBuilder(CycleBuilder):
    def __init__(self, event_anomaly_checker: AbstractEventAnomalyChecker, event: GaitEventLabel):
        super().__init__(event_anomaly_checker)
        self.event_label = event.value

    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        gait_cycles = GaitCycleList()
        numbers = {GaitEventContext.LEFT.value: 0,
                   GaitEventContext.RIGHT.value: 0}
        for event_index in range(0, acq.GetEventNumber()):
            start_event = acq.GetEvent(event_index)
            context = start_event.GetContext()

            label = start_event.GetLabel()
            if label == self.event_label:
                try:
                    [end_event, unused_events] = find_next_event(acq, label, context, event_index)
                    if end_event is not None:
                        numbers[context] = numbers[context] + 1
                        cycle = GaitCycle(numbers[context], GaitEventContext(context),
                                          start_event.GetFrame(), end_event.GetFrame(),
                                          unused_events)
                        gait_cycles.add_cycle(cycle)
                except IndexError as err:
                    pass  # If events do not match in the end this will be raised
        return gait_cycles


class HeelStrikeToHeelStrikeCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, GaitEventLabel.FOOT_OFF)


# Cycle Extractor
class CycleDataExtractor:
    def __init__(self, configs: ConfigProvider):
        self._configs = configs

    def extract_data(self, cycles: GaitCycleList, acq: btkAcquisition) -> Dict[str, BasicCyclePoint]:
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
                    cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number, cycle.unused_event.GetLabel())


# Normalisation
class TimeNormalisationAlgorithm(ABC):

    def __init__(self, number_frames: int = 100):
        self._number_frames = number_frames
        self._data_type_fiter = {PointDataType.Angles,
                                 PointDataType.Forces,
                                 PointDataType.Moments,
                                 PointDataType.Power,
                                 PointDataType.Scalar,
                                 PointDataType.Reaction}

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
                    n_cycle_point.add_event_frame(norm_event_frame,
                                                  cycle_key,
                                                  r_cycle_point.event_frames.iloc[cycle_key][
                                                      BasicCyclePoint.EVENT_LABEL])
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


class GaitCycle:

    def __init__(self, number: int, context: GaitEventContext, start_frame: int, end_frame: int,
                 unused_event: btkEvent):
        self.number = number
        self.context = context
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.unused_event = unused_event


class GaitCycleList:

    def __init__(self):
        self._left_cycles = {}
        self._right_cycles = {}

    def add_cycle(self, cycle: GaitCycle):
        if cycle.context == GaitEventContext.LEFT:
            self._left_cycles[cycle.number] = cycle
        else:
            self._right_cycles[cycle.number] = cycle

    @property
    def left_cycles(self) -> {int: GaitCycle}:
        return self._left_cycles

    @left_cycles.setter
    def left_cycles(self, cycles: {int: GaitCycle}):
        self._left_cycles = cycles

    @property
    def right_cycles(self) -> {int: GaitCycle}:
        return self._right_cycles

    @right_cycles.setter
    def right_cycles(self, cycles: {int: GaitCycle}):
        self._right_cycles = cycles

    def get_number_of_cycles(self) -> int:
        l_num = list(self._left_cycles.keys())[-1]
        r_num = list(self._left_cycles.keys())[-1]
        return l_num if l_num >= r_num else r_num


class BasicCyclePoint:
    EVENT_FRAME_NUMBER = "events_between"
    EVENT_LABEL = "events_label"
    CYCLE_NUMBER = "cycle_number"
    TYPE_RAW = "raw"
    TYPE_NORM = "normalised"

    def __init__(self, cycle_point_type: str, translated_label: Enum, direction: AxesNames, data_type: PointDataType,
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

    def add_event_frame(self, event_frame: int, cycle_number: int, event_label: str):
        if self.event_frames is None:
            prep_dict = {cycle_number: [event_frame, event_label]}
            self.event_frames = DataFrame.from_dict(data=prep_dict, orient="index",
                                                    columns=[self.EVENT_FRAME_NUMBER, self.EVENT_LABEL])
            self.event_frames.index.name = self.CYCLE_NUMBER
        else:
            self.event_frames.loc[cycle_number] = [event_frame, event_label]

    def get_mean_event_frame(self) -> float:
        return self.event_frames[self.EVENT_FRAME_NUMBER].mean()

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

    @staticmethod
    def define_cycle_point_file_name(cycle_point, prefix: str, postfix: str) -> str:
        key = ConfigProvider.define_key(cycle_point.translated_label, cycle_point.data_type, cycle_point.direction,
                                        cycle_point.context)

        return f"{prefix}{CyclePointLoader.FILENAME_DELIMITER}{key}{CyclePointLoader.FILENAME_DELIMITER}{postfix}.csv"

    def to_csv(self, path: str, prefix: str):
        output = self.event_frames.merge(self.data_table, on=self.CYCLE_NUMBER)
        filename = self.define_cycle_point_file_name(self, prefix, self.cycle_point_type)
        output.to_csv(f"{path}/{filename}")

    @classmethod
    def from_csv(cls, configs: ConfigProvider, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context, cycle_point_type,
         prefix] = CyclePointLoader.get_meta_data_filename(filename)

        translated = configs.get_translated_label(label, data_type)
        point = BasicCyclePoint(cycle_point_type, translated, direction, data_type, context)
        data_table = read_csv(f"{path}/{filename}", index_col=cls.CYCLE_NUMBER)
        point.event_frames = DataFrame([data_table[cls.EVENT_FRAME_NUMBER], data_table[cls.EVENT_LABEL]]).T
        data_table = data_table.drop([cls.EVENT_FRAME_NUMBER, cls.EVENT_LABEL], axis=1)
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


class CyclePointLoader:
    FILENAME_DELIMITER = "-"

    def __init__(self, configs: ConfigProvider, dir_path: str):
        self._raw_cycle_data = {}
        self._norm_cycle_data = {}
        file_names = os.listdir(dir_path)
        postfix = BasicCyclePoint.TYPE_RAW
        raw_file_names = self._filter_filenames(file_names, postfix)

        self._raw_cycle_data = self._init_buffered_points(configs, dir_path, raw_file_names)

        postfix = BasicCyclePoint.TYPE_NORM
        norm_file_names = self._filter_filenames(file_names, postfix)
        self._norm_cycle_data = self._init_buffered_points(configs, dir_path, norm_file_names)

    def _init_buffered_points(self, configs, dir_path, file_names) -> Dict[str, BasicCyclePoint]:
        cycle_data: Dict[str, BasicCyclePoint] = {}
        for file_name in file_names:
            point = BufferedCyclePoint(configs, dir_path, file_name)
            foo, key, foo = self.get_key_from_filename(file_name)
            cycle_data[key] = point
        return cycle_data

    @classmethod
    def get_key_from_filename(cls, filename: str) -> [str, str, str]:
        return filename.split(cls.FILENAME_DELIMITER)

    @classmethod
    def get_meta_data_filename(cls, filename: str) -> [str, PointDataType, AxesNames, GaitEventContext, str, str]:
        prefix, key, postfix = cls.get_key_from_filename(filename)
        meta_data = key.split(".")
        label = meta_data[0]
        data_type = PointDataType[meta_data[1]]
        direction = AxesNames[meta_data[2]]
        context = GaitEventContext(meta_data[3])
        return [label, data_type, direction, context, postfix, prefix]

    @classmethod
    def _filter_filenames(cls, file_names, postfix) -> List[str]:
        r = re.compile(f".*{cls.FILENAME_DELIMITER}{postfix}.*\.csv")
        return list(filter(r.match, file_names))

    def get_raw_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._raw_cycle_data

    def get_norm_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._norm_cycle_data
