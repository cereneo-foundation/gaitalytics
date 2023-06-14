from abc import ABC, abstractmethod
from enum import Enum
from math import ceil
from statistics import mean
from typing import Dict, Set

import numpy as np
import pandas
import pandas as pd
from pandas import DataFrame

from gait_analysis.cycle.extraction import RawCyclePoint, BasicCyclePoint
from gait_analysis.utils.c3d import PointDataType, AxesNames, GaitEventContext
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.utils import define_cycle_point_file_name, get_meta_data_filename


class NormalisedCyclePoint(BasicCyclePoint):

    def __init__(self, translated_label: Enum, direction: AxesNames, data_type: PointDataType,
                 context: GaitEventContext):
        super().__init__(translated_label, direction, data_type, context)
        self._data_table = None

    @property
    def data_table(self) -> pd.DataFrame:
        return self._data_table

    @data_table.setter
    def data_table(self, data_table: pd.DataFrame):
        self._data_table = data_table

    def get_event_frame(self) -> int:
        return mean(self.event_frames[self.EVENT_FRAME_NUMBER])

    def _create_table(self, data: np.array):
        column_names = [i for i in range(1, len(data)+1)]
        df = pd.DataFrame(data=[data], columns=np.array(column_names))
        df.index.name = self.CYCLE_NUMBER
        return df

    def add_cycle_data(self, data: np.array, cycle_number: int):
        if self.data_table is None:
            self.data_table = self._create_table(data)
        else:
            self.data_table.loc[cycle_number] = data

    def to_csv(self, path: str, prefix: str):
        output = pd.merge(self.event_frames, self.data_table, on=self.CYCLE_NUMBER)
        filename = define_cycle_point_file_name(self, prefix)
        output.to_csv(f"{path}/{filename}")

    @classmethod
    def from_csv(cls, configs: ConfigProvider, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context] = get_meta_data_filename(filename)
        translated = configs.get_translated_label(label, data_type)
        point = NormalisedCyclePoint(translated, data_type, direction, context)
        data_table = pandas.read_csv(f"{path}/{filename}", index_col=cls.CYCLE_NUMBER)
        point.event_frames = DataFrame(data_table[cls.EVENT_FRAME_NUMBER])
        data_table = data_table.drop(cls.EVENT_FRAME_NUMBER, axis=1)
        point.data_table = data_table

        return point


class BufferedNormalisedCyclePoint(NormalisedCyclePoint):
    def __init__(self, configs: ConfigProvider, path: str, filename: str):
        self._configs = configs
        self._filename = filename
        self._path = path
        self._loaded = False

    def _load_file(self):
        if not self._loaded:
            point = NormalisedCyclePoint.from_csv(self._configs, self._path, self._filename)
            self._event_frames = point.event_frames
            self._translated_label = point.translated_label
            self._direction = point.direction
            self._context = point.context
            self._data_type = point.data_type
            self._data_table = point.data_table
            self._loaded = True

    @property
    def data_table(self) -> pd.DataFrame:
        self._load_file()
        return super().data_table

    @data_table.setter
    def data_table(self, data_table: pd.DataFrame):
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

    def normalise(self, r_data_list: Dict[str, RawCyclePoint]) -> Dict[str, NormalisedCyclePoint]:
        n_data_list = {}
        for data_key in r_data_list:
            r_cycle_point = r_data_list[data_key]
            if r_cycle_point.data_type in self._data_type_fiter:
                n_cycle_point = NormalisedCyclePoint(r_cycle_point.translated_label,
                                                     r_cycle_point.direction, r_cycle_point.data_type,
                                                     r_cycle_point.context)
                for cycle_key in r_cycle_point.data:
                    cycle_data = r_cycle_point.data[cycle_key]

                    interpolated_data = self._run_algorithm(cycle_data, self._number_frames)
                    n_cycle_point.add_cycle_data(interpolated_data, cycle_key)

                    norm_event_frame = self._define_event_frame(
                        r_cycle_point.event_frames.loc[cycle_key][BasicCyclePoint.EVENT_FRAME_NUMBER],
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
