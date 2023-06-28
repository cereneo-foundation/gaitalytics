from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import List, Dict

import numpy as np
import yaml
from btk import btkAcquisition, btkEvent
from pandas import DataFrame, read_csv

FILENAME_DELIMITER = "-"


def min_max_norm(data):
    scale_min = -1
    scale_max = 1
    max_data = max(data)
    min_data = min(data)
    diff = max_data - min_data
    return [((entry - min_data) * (scale_max - scale_min) / diff) + scale_min for entry in data]


class ConfigProvider:
    _MARKER_MAPPING = "marker_set_mapping"
    _MODEL_MAPPING = "model_mapping"

    def __init__(self, file_path: str):
        self._read_configs(file_path)
        self.MARKER_MAPPING = Enum('MarkerMapping', self._config[self._MARKER_MAPPING])
        self.MODEL_MAPPING = Enum('ModelMapping', self._config[self._MODEL_MAPPING])

    def get_translated_label(self, label: str, point_type: PointDataType) -> Enum | None:
        try:
            if point_type.value == PointDataType.Marker.value:
                return self.MARKER_MAPPING(label)
            else:
                return self.MODEL_MAPPING(label)
        except ValueError as e:
            try:
                if point_type.value == PointDataType.Marker.value:
                    return self.MARKER_MAPPING[label]
                else:
                    return self.MODEL_MAPPING[label]
            except KeyError as e:
                return None

    def _read_configs(self, file_path: str):
        with open(file_path, 'r') as f:
            self._config = yaml.safe_load(f)

    @staticmethod
    def define_key(translated_label: Enum, point_type: PointDataType,
                   direction: AxesNames,
                   side: GaitEventContext) -> str:
        if translated_label is not None:
            return f"{translated_label.name}.{point_type.name}.{direction.name}.{side.value}"


class SubjectMeasures(yaml.YAMLObject):
    yaml_tag = u'!subject'
    yaml_loader = yaml.SafeLoader

    def __init__(self, body_mass: float, body_height: float, left_leg_length: float, right_leg_length: float, subject :str):
        self.body_mass = body_mass
        self.body_height = body_height
        self.left_leg_length = left_leg_length
        self.right_leg_length = right_leg_length
        self.subject = subject

    def to_file(self, path_out: str):
        with open(f"{path_out}/subject.yml", "w") as f:
            yaml.dump(self, f)

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as f:
            measures = yaml.safe_load(f)
            return measures


def extract_subject(acq: btkAcquisition) -> SubjectMeasures:
    body_mass = acq.GetMetaData().GetChild("PROCESSING").GetChild("Bodymass").GetInfo().ToDouble()[0]
    body_height = acq.GetMetaData().GetChild("PROCESSING").GetChild("Height").GetInfo().ToDouble()[0]
    left_leg_length = acq.GetMetaData().GetChild("PROCESSING").GetChild("LLegLength").GetInfo().ToDouble()[0]
    right_leg_length = acq.GetMetaData().GetChild("PROCESSING").GetChild("RLegLength").GetInfo().ToDouble()[0]
    name = acq.GetMetaData().GetChild("SUBJECTS").GetChild("NAMES").GetInfo().ToString()[0].strip()
    subject = SubjectMeasures(body_mass, body_height, left_leg_length, right_leg_length, name)
    return subject


class PointDataType(Enum):
    Marker = 0
    Angles = 1
    Forces = 2
    Moments = 3
    Power = 4
    Scalar = 5
    Reaction = 6


class AxesNames(Enum):
    x = 0
    y = 1
    z = 2


class GaitEventContext(Enum):
    """
    Representation of gait event contexts. At the moment mainly left and right
    """
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def get_contrary_context(cls, context: str):
        if context == cls.LEFT.value:
            return cls.RIGHT
        return cls.LEFT


def get_key_from_filename(filename: str) -> [str, str, str]:
    return filename.split(FILENAME_DELIMITER)


def get_meta_data_filename(filename: str) -> [str, PointDataType,
                                              AxesNames,
                                              GaitEventContext, str, str]:
    prefix, key, postfix = get_key_from_filename(filename)
    meta_data = key.split(".")
    label = meta_data[0]
    data_type = PointDataType[meta_data[1]]
    direction = AxesNames[meta_data[2]]
    context = GaitEventContext(meta_data[3])
    postfix = postfix.split(".")[0]
    return [label, data_type, direction, context, postfix, prefix]


class GaitEventLabel(Enum):
    FOOT_STRIKE = "Foot Strike"
    FOOT_OFF = "Foot Off"

    @classmethod
    def get_contrary_event(cls, event_label: str):
        if event_label == cls.FOOT_STRIKE.value:
            return cls.FOOT_OFF
        return cls.FOOT_STRIKE

    @classmethod
    def get_type_id(cls, event_label: str):
        if event_label == cls.FOOT_STRIKE.value:
            return 1
        return 2


class GaitCycle:

    def __init__(self, number: int, context: GaitEventContext, start_frame: int, end_frame: int,
                 unused_events: List[btkEvent]):
        self.number: int = number
        self.context: GaitEventContext = context
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
        if cycle.context == GaitEventContext.LEFT:
            self.left_cycles[cycle.number] = cycle
        else:
            self.right_cycles[cycle.number] = cycle

    def get_longest_cycle_length(self, side: GaitEventContext) -> int:
        if side == GaitEventContext.LEFT:
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
        self._direction: AxesNames | None = None
        self._context: GaitEventContext | None = None
        self._data_type: PointDataType | None = None
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
    def direction(self) -> AxesNames:
        return self._direction

    @direction.setter
    def direction(self, direction: AxesNames):
        self._direction = direction

    @property
    def context(self) -> GaitEventContext:
        return self._context

    @context.setter
    def context(self, context: GaitEventContext):
        self._context = context

    @property
    def data_type(self) -> PointDataType:
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: PointDataType):
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
        key = ConfigProvider.define_key(cycle_point.translated_label, cycle_point.data_type,
                                        cycle_point.direction,
                                        cycle_point.context)

        return f"{prefix}{FILENAME_DELIMITER}{key}{FILENAME_DELIMITER}{postfix}.csv"

    def to_csv(self, path: str, prefix: str):
        output = self.frames.merge(self.event_frames, on=self.CYCLE_NUMBER)
        output = output.merge(self.data_table, on=self.CYCLE_NUMBER)
        filename = self.define_cycle_point_file_name(self, prefix, self.cycle_point_type)
        output.to_csv(f"{path}/{filename}")

    @classmethod
    def from_csv(cls, configs: ConfigProvider,
                 path: str,
                 filename: str,
                 subject: SubjectMeasures) -> BasicCyclePoint:
        [label, data_type, direction, context, cycle_point_type, prefix] = get_meta_data_filename(filename)

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
    def __init__(self, configs: ConfigProvider,
                 path: str,
                 filename: str,
                 subject: SubjectMeasures):
        super().__init__()
        self._configs = configs
        self._filename = filename
        self._path = path
        self._loaded = False

        [label, data_type, direction, context, cycle_point_type, prefix] = get_meta_data_filename(filename)
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
