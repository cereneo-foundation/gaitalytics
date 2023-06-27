from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from enum import Enum
from math import ceil
from typing import Dict, List

import numpy as np
import yaml
from btk import btkAcquisition, btkEvent
from pandas import DataFrame, read_csv

import gaitalytics.c3d
import gaitalytics.events
import gaitalytics.utils

# Cycle Builder
class CycleBuilder(ABC):

    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
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
    def __init__(self,
                 event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker,
                 event: gaitalytics.c3d.GaitEventLabel):
        super().__init__(event_anomaly_checker)
        self.event_label = event.value

    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        gait_cycles = GaitCycleList()
        numbers = {gaitalytics.c3d.GaitEventContext.LEFT.value: 0,
                   gaitalytics.c3d.GaitEventContext.RIGHT.value: 0}
        for event_index in range(0, acq.GetEventNumber()):
            start_event = acq.GetEvent(event_index)
            context = start_event.GetContext()

            label = start_event.GetLabel()
            if label == self.event_label:
                try:
                    [end_event, unused_events] = gaitalytics.events.find_next_event(acq, label, context, event_index)
                    if end_event is not None:
                        numbers[context] = numbers[context] + 1
                        cycle = GaitCycle(numbers[context], gaitalytics.c3d.GaitEventContext(context),
                                          start_event.GetFrame(), end_event.GetFrame(),
                                          unused_events)
                        gait_cycles.add_cycle(cycle)
                except IndexError as err:
                    pass  # If events do not match in the end this will be raised
        return gait_cycles


class HeelStrikeToHeelStrikeCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, gaitalytics.c3d.GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, gaitalytics.c3d.GaitEventLabel.FOOT_OFF)


# Cycle Extractor
class CycleDataExtractor:
    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        self._configs = configs

    def extract_data(self, cycles: GaitCycleList, acq: btkAcquisition) -> Dict[str, BasicCyclePoint]:
        subject = gaitalytics.utils.extract_subject(acq)
        data_list: Dict[str, BasicCyclePoint] = {}
        for point_index in range(0, acq.GetPointNumber()):
            cycle_counts_left = len(cycles.left_cycles.values())
            cycle_counts_right = len(cycles.right_cycles.values())
            longest_cycle_left = cycles.get_longest_cycle_length(gaitalytics.c3d.GaitEventContext.LEFT)
            longest_cycle_right = cycles.get_longest_cycle_length(gaitalytics.c3d.GaitEventContext.RIGHT)

            point = acq.GetPoint(point_index)

            for direction_index in range(0, len(point.GetValues()[0])):
                label = point.GetLabel()
                data_type = gaitalytics.c3d.PointDataType(point.GetType())
                translated_label = self._configs.get_translated_label(label, data_type)
                if translated_label is not None:
                    direction = gaitalytics.c3d.AxesNames(direction_index)
                    left = self._create_point_cycle(cycle_counts_left, longest_cycle_left, translated_label,
                                                    direction, data_type, gaitalytics.c3d.GaitEventContext.LEFT,
                                                    subject)
                    right = self._create_point_cycle(cycle_counts_right, longest_cycle_right, translated_label,
                                                     direction, data_type, gaitalytics.c3d.GaitEventContext.RIGHT,
                                                     subject)

                    for cycle_number in range(1, cycles.get_number_of_cycles() + 1):
                        if len(cycles.right_cycles) + 1 > cycle_number:
                            self._extract_cycle(right, cycles.right_cycles[cycle_number],
                                                point.GetValues()[:, direction_index])
                        if len(cycles.left_cycles) + 1 > cycle_number:
                            self._extract_cycle(left, cycles.left_cycles[cycle_number],
                                                point.GetValues()[:, direction_index])

                    key_left = gaitalytics.utils.ConfigProvider.define_key(translated_label, data_type, direction,
                                                                           gaitalytics.c3d.GaitEventContext.LEFT)
                    key_right = gaitalytics.utils.ConfigProvider.define_key(translated_label, data_type, direction,
                                                                            gaitalytics.c3d.GaitEventContext.RIGHT)
                    data_list[key_left] = left
                    data_list[key_right] = right

        return data_list

    @staticmethod
    def _create_point_cycle(cycle_counts: int,
                            longest_cycle,
                            label: Enum,
                            direction: gaitalytics.c3d.AxesNames,
                            data_type: gaitalytics.c3d.PointDataType,
                            context: gaitalytics.c3d.GaitEventContext,
                            subject: SubjectMeasures) -> TestCyclePoint:
        cycle = TestCyclePoint(cycle_counts, longest_cycle, BasicCyclePoint.TYPE_RAW)
        cycle.direction = direction
        cycle.context = context
        cycle.translated_label = label
        cycle.data_type = data_type
        cycle.subject = subject
        return cycle

    @staticmethod
    def _extract_cycle(cycle_point: TestCyclePoint, cycle: GaitCycle, values: np.array):
        cycle_point.data_table.loc[cycle.number][0:cycle.length] = values[cycle.start_frame: cycle.end_frame]
        events = np.array(list(cycle.unused_events.values()))
        events = events - cycle.start_frame
        cycle_point.event_frames.loc[cycle.number] = events
        cycle_point.frames.loc[cycle.number] = [cycle.start_frame, cycle.end_frame]


# Normalisation
class TimeNormalisationAlgorithm(ABC):

    def __init__(self, number_frames: int = 100):
        self._number_frames = number_frames
        self._data_type_fiter = {gaitalytics.c3d.PointDataType.Angles,
                                 gaitalytics.c3d.PointDataType.Forces,
                                 gaitalytics.c3d.PointDataType.Moments,
                                 gaitalytics.c3d.PointDataType.Power,
                                 gaitalytics.c3d.PointDataType.Scalar,
                                 gaitalytics.c3d.PointDataType.Reaction}

    def normalise(self, r_data_list: Dict[str, BasicCyclePoint]) -> Dict[str, BasicCyclePoint]:
        n_data_list = {}
        for data_key in r_data_list:
            r_cycle_point = r_data_list[data_key]
            if r_cycle_point.data_type in self._data_type_fiter:
                n_cycle_point = TestCyclePoint(len(r_cycle_point.data_table),
                                               self._number_frames,
                                               BasicCyclePoint.TYPE_NORM)
                n_cycle_point.cycle_point_type = BasicCyclePoint.TYPE_NORM
                n_cycle_point.translated_label = r_cycle_point.translated_label
                n_cycle_point.direction = r_cycle_point.direction
                n_cycle_point.data_type = r_cycle_point.data_type
                n_cycle_point.context = r_cycle_point.context
                n_cycle_point.subject = r_cycle_point.subject
                n_cycle_point.frames = r_cycle_point.frames

                for cycle_key in r_cycle_point.data_table.index.to_list():
                    cycle_data = r_cycle_point.data_table.loc[cycle_key].to_list()

                    interpolated_data = self._run_algorithm(cycle_data, self._number_frames)
                    n_cycle_point.data_table.loc[cycle_key] = interpolated_data
                    events = self._define_event_frame(np.array(r_cycle_point.event_frames.loc[cycle_key].to_list()),
                                             len(cycle_data),
                                             self._number_frames)
                    n_cycle_point.event_frames.loc[cycle_key] = events
                n_data_list[data_key] = n_cycle_point
        return n_data_list

    @abstractmethod
    def _run_algorithm(self, data: np.array,
                       number_frames: int = 100) -> np.array:
        pass

    @abstractmethod
    def _define_event_frame(self, event_frames: np.array, frame_number_cycle: int, number_frames: int = 100) -> int:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _define_event_frame(self, event_frames: DataFrame, frame_number_cycle: int, number_frames: int = 100) -> int:
        events = event_frames / frame_number_cycle * number_frames
        return events.round()

    def _run_algorithm(self, data: np.array, number_frames: int = 100) -> np.array:
        data = np.array(data)
        data = data[np.logical_not(np.isnan(data))]
        times = np.arange(0, len(data), 1)
        times_new = np.linspace(0, len(data), num=number_frames)
        return np.interp(times_new, times, data)


class GaitCycle:

    def __init__(self, number: int, context: gaitalytics.c3d.GaitEventContext, start_frame: int, end_frame: int,
                 unused_events: List[btkEvent]):
        self.number: int = number
        self.context: gaitalytics.c3d.GaitEventContext = context
        self.start_frame: int = start_frame
        self.end_frame: int = end_frame
        self.length: int = end_frame - start_frame
        self.unused_events: Dict | None = None
        self._unused_events_to_dict(unused_events)

    def _unused_events_to_dict(self, unused_events: List[btkEvent]):
        if len(unused_events) <= 3:
            self.unused_events = {}
            for unused_event in unused_events:
                self.unused_events[f"{unused_event.GetLabel()}_{unused_event.GetContext()}"] = unused_event.GetFrame()

        else:
            raise ValueError("too much events in cycle")


class GaitCycleList:

    def __init__(self):
        self.left_cycles: Dict[int, GaitCycle] = {}
        self.right_cycles: Dict[int, GaitCycle] = {}

    def add_cycle(self, cycle: GaitCycle):
        if cycle.context == gaitalytics.c3d.GaitEventContext.LEFT:
            self.left_cycles[cycle.number] = cycle
        else:
            self.right_cycles[cycle.number] = cycle

    def get_longest_cycle_length(self, side: gaitalytics.c3d.GaitEventContext) -> int:
        if side == gaitalytics.c3d.GaitEventContext.LEFT:
            return self._longest_cycle(self.left_cycles)
        else:
            return self._longest_cycle(self.right_cycles)

    @staticmethod
    def _longest_cycle(cycles: Dict[int, GaitCycle]) -> int:
        length = 0
        for cycle in cycles.values():
            length = length if length > cycle.length else cycle.length
        return length

    def get_number_of_cycles(self) -> int:
        l_num = len(list(self.left_cycles.keys()))
        r_num = len(list(self.left_cycles.keys()))
        return l_num if l_num >= r_num else r_num


class SubjectMeasures(yaml.YAMLObject):
    yaml_tag = u'!subject'
    yaml_loader = yaml.SafeLoader

    def __init__(self, body_mass: float, body_height: float, left_leg_length: float, right_leg_length: float):
        self.body_mass = body_mass
        self.body_height = body_height
        self.left_leg_length = left_leg_length
        self.right_leg_length = right_leg_length

    def to_file(self, path_out: str):
        with open(f"{path_out}/subject.yml", "w") as f:
            yaml.dump(self, f)

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as f:
            measures = yaml.safe_load(f)
            return measures


class BasicCyclePoint(ABC):
    CYCLE_NUMBER = "cycle_number"
    TYPE_RAW = "raw"
    TYPE_NORM = "normalised"
    FOOT_OFF_CONTRA = "Foot_Off_Contra"
    FOOT_STRIKE_CONTRA = "Foot_Strike_Contra"
    FOOT_OFF = "Foot_Off"
    START_FRAME = "start_frame"
    END_FRAME = "end_frame"

    def __init__(self):
        self._cycle_point_type: str | None = None
        self._translated_label: Enum | None = None
        self._direction: gaitalytics.c3d.AxesNames | None = None
        self._context: gaitalytics.c3d.GaitEventContext | None = None
        self._data_type: gaitalytics.c3d.PointDataType | None = None
        self._data_table: DataFrame | None = None
        self._event_frames: DataFrame | None = None
        self._frames: DataFrame | None = None
        self._subject: SubjectMeasures | None = None

    @property
    def cycle_point_type(self) -> str:
        return self._cycle_point_type

    @cycle_point_type.setter
    def cycle_point_type(self, cycle_point_type: str):
        self._cycle_point_type = cycle_point_type

    @property
    def translated_label(self) -> Enum:
        return self._translated_label

    @translated_label.setter
    def translated_label(self, translated_label: Enum):
        self._translated_label = translated_label

    @property
    def direction(self) -> gaitalytics.c3d.AxesNames:
        return self._direction

    @direction.setter
    def direction(self, direction: gaitalytics.c3d.AxesNames):
        self._direction = direction

    @property
    def context(self) -> gaitalytics.c3d.GaitEventContext:
        return self._context

    @context.setter
    def context(self, context: gaitalytics.c3d.GaitEventContext):
        self._context = context

    @property
    def data_type(self) -> gaitalytics.c3d.PointDataType:
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: gaitalytics.c3d.PointDataType):
        self._data_type = data_type

    @property
    def data_table(self) -> DataFrame:
        return self._data_table

    @data_table.setter
    def data_table(self, data_table: DataFrame):
        self._data_table = data_table

    @property
    def event_frames(self) -> DataFrame:
        return self._event_frames

    @event_frames.setter
    def event_frames(self, event_frames: DataFrame):
        self._event_frames = event_frames

    @property
    def frames(self) -> DataFrame:
        return self._frames

    @frames.setter
    def frames(self, frames: DataFrame):
        self._frames = frames

    @property
    def subject(self) -> SubjectMeasures:
        return self._subject

    @subject.setter
    def subject(self, subject: SubjectMeasures):
        self._subject = subject

    def get_mean_event_frame(self) -> float:
        return self.event_frames[self.FOOT_OFF].mean()

    @staticmethod
    def define_cycle_point_file_name(cycle_point, prefix: str, postfix: str) -> str:
        key = gaitalytics.utils.ConfigProvider.define_key(cycle_point.translated_label, cycle_point.data_type,
                                                          cycle_point.direction,
                                                          cycle_point.context)

        return f"{prefix}{CyclePointLoader.FILENAME_DELIMITER}{key}{CyclePointLoader.FILENAME_DELIMITER}{postfix}.csv"

    def to_csv(self, path: str, prefix: str):
        output = self.frames.merge(self.event_frames, on=self.CYCLE_NUMBER)
        output = output.merge(self.data_table, on=self.CYCLE_NUMBER)
        filename = self.define_cycle_point_file_name(self, prefix, self.cycle_point_type)
        output.to_csv(f"{path}/{filename}")

    @classmethod
    def from_csv(cls, configs: gaitalytics.utils.ConfigProvider,
                 path: str,
                 filename: str,
                 subject: SubjectMeasures) -> BasicCyclePoint:
        [label, data_type, direction, context, cycle_point_type, prefix] = CyclePointLoader.get_meta_data_filename(
            filename)

        translated = configs.get_translated_label(label, data_type)
        point = BasicCyclePoint()
        point.cycle_point_type = cycle_point_type
        point.direction = direction
        point.context = context
        point.subject = subject
        point.translated_label = translated
        point.data_type = data_type
        data_table = read_csv(f"{path}/{filename}", index_col=cls.CYCLE_NUMBER)
        frame_labels = [cls.START_FRAME, cls.END_FRAME]
        event_labels = [cls.FOOT_OFF_CONTRA, cls.FOOT_STRIKE_CONTRA, cls.FOOT_OFF]
        point.frames = data_table[frame_labels]
        point.event_frames = data_table[event_labels]
        frame_labels.extend(event_labels)
        data_table = data_table.drop(frame_labels, axis=1)
        data_table.columns = data_table.columns.map(int)
        point.data_table = data_table

        return point


class TestCyclePoint(BasicCyclePoint):

    def __init__(self, number_of_cycles: int, longest_frames: int, cycle_point_type: str):
        super().__init__()
        cycle_numbers = np.arange(1, number_of_cycles + 1)
        columns = np.arange(0, longest_frames)
        self.data_table = DataFrame(columns=columns, index=cycle_numbers)
        self.data_table.index.name = self.CYCLE_NUMBER
        self.event_frames = DataFrame(columns=[self.FOOT_OFF_CONTRA, self.FOOT_STRIKE_CONTRA, self.FOOT_OFF],
                                      index=cycle_numbers)
        self.event_frames.index.name = self.CYCLE_NUMBER
        self.frames = DataFrame(columns=[self.START_FRAME, self.END_FRAME], index=cycle_numbers)
        self.frames.index.name = self.CYCLE_NUMBER
        self.cycle_point_type = cycle_point_type


class BufferedCyclePoint(BasicCyclePoint):
    def __init__(self, configs: gaitalytics.utils.ConfigProvider, path: str, filename: str, subject: SubjectMeasures):
        super().__init__()
        self._configs = configs
        self._filename = filename
        self._path = path
        self._loaded = False

        [label, data_type, direction, context, cycle_point_type, prefix] = CyclePointLoader.get_meta_data_filename(
            filename)
        translated = configs.get_translated_label(label, data_type)
        self.translated_label = translated
        self.direction = direction
        self.data_type = data_type
        self.cycle_point_type = cycle_point_type
        self.context = context
        self.subject = subject

    def _load_file(self):
        if not self._loaded:
            point = BasicCyclePoint.from_csv(self._configs, self._path, self._filename, self.subject)
            self._event_frames = point.event_frames
            self._frames = point.frames
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

    @property
    def event_frames(self) -> DataFrame:
        self._load_file()
        return super().event_frames

    @event_frames.setter
    def event_frames(self, value: DataFrame):
        self._load_file()
        super().event_frames = value

    @property
    def frames(self) -> DataFrame:
        self._load_file()
        return super().frames

    @frames.setter
    def frames(self, frames: DataFrame):
        self._load_file()
        super().frames = frames

    def to_csv(self, path: str, prefix: str):
        self._load_file()
        super().to_csv(path, prefix)


class CyclePointLoader:
    FILENAME_DELIMITER = "-"

    def __init__(self, configs: gaitalytics.utils.ConfigProvider, dir_path: str):
        self._raw_cycle_data = {}
        self._norm_cycle_data = {}
        file_names = os.listdir(dir_path)
        postfix = BasicCyclePoint.TYPE_RAW
        raw_file_names = self._filter_filenames(file_names, postfix)
        subject = SubjectMeasures.from_file(f"{dir_path}/subject.yml")
        self._raw_cycle_data = self._init_buffered_points(configs, dir_path, raw_file_names, subject)

        postfix = BasicCyclePoint.TYPE_NORM
        norm_file_names = self._filter_filenames(file_names, postfix)
        self._norm_cycle_data = self._init_buffered_points(configs, dir_path, norm_file_names, subject)

    def _init_buffered_points(self,
                              configs: gaitalytics.utils.ConfigProvider,
                              dir_path: str,
                              file_names: List[str],
                              subject: SubjectMeasures) -> Dict[str, BasicCyclePoint]:
        cycle_data: Dict[str, BasicCyclePoint] = {}
        for file_name in file_names:
            point = BufferedCyclePoint(configs, dir_path, file_name, subject)
            foo, key, foo = self.get_key_from_filename(file_name)
            cycle_data[key] = point
        return cycle_data

    @classmethod
    def get_key_from_filename(cls, filename: str) -> [str, str, str]:
        return filename.split(cls.FILENAME_DELIMITER)

    @classmethod
    def get_meta_data_filename(cls, filename: str) -> [str, gaitalytics.c3d.PointDataType, gaitalytics.c3d.AxesNames,
                                                       gaitalytics.c3d.GaitEventContext, str, str]:
        prefix, key, postfix = cls.get_key_from_filename(filename)
        meta_data = key.split(".")
        label = meta_data[0]
        data_type = gaitalytics.c3d.PointDataType[meta_data[1]]
        direction = gaitalytics.c3d.AxesNames[meta_data[2]]
        context = gaitalytics.c3d.GaitEventContext(meta_data[3])
        postfix = postfix.split(".")[0]
        return [label, data_type, direction, context, postfix, prefix]

    @classmethod
    def _filter_filenames(cls, file_names, postfix) -> List[str]:
        r = re.compile(f".*{cls.FILENAME_DELIMITER}{postfix}.*\.csv")
        return list(filter(r.match, file_names))

    def get_raw_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._raw_cycle_data

    def get_norm_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._norm_cycle_data
