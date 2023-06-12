from abc import ABC, abstractmethod
from enum import Enum
from math import ceil
from statistics import mean
from typing import Dict, Set

import numpy as np
import pandas
import pandas as pd

from gait_analysis.cycle.extraction import RawCyclePoint, BasicCyclePoint, define_key
from gait_analysis.utils.c3d import PointDataType, AxesNames, GaitEventContext
from gait_analysis.utils.config import ConfigProvider


class NormalisedCyclePoint(BasicCyclePoint):

    def __init__(self, label: str, translated_label: Enum, direction: AxesNames, data_type: PointDataType,
                 context: GaitEventContext):
        super().__init__(label, translated_label, direction, data_type, context)
        self._data_table = None

    @property
    def data_table(self) -> pd.DataFrame:
        return self._data_table

    @data_table.setter
    def data_table(self, data_table: pd.DataFrame):
        self._data_table = data_table

    def get_event_frame(self) -> int:
        return mean(self.event_frames[self.EVENT_FRAME_NUMBER])

    @staticmethod
    def _create_table(data: np.array):
        column_names = []
        for index in range(0, len(data)):
            column_names.append(index)
        df = pd.DataFrame(data=[data], columns=np.array(column_names))
        df.index.name = "cycle_number"
        return df

    def add_cycle_data(self, data: np.array, cycle_number: int):
        if self.data_table is None:
            self.data_table = self._create_table(data)
        else:
            self.data_table.loc[cycle_number] = data

    def to_csv(self, path: str, prefix: str):
        key = define_key(self.label, self.translated_label, self.data_type, self.direction, self.context)
        output = pd.merge(self.event_frames, self.data_table, on="cycle_number")
        output.to_csv(f"{path}/{prefix}-{key}-normalised.csv")

    @classmethod
    def from_csv(cls, configs: ConfigProvider, path: str, filename: str) -> BasicCyclePoint:
        [label, data_type, direction, context] = cls._get_meta_data_filename(filename)
        translated = configs.get_translated_label(label, direction, data_type)
        label = label if translated is None else translated.value
        point = NormalisedCyclePoint(label, translated, data_type, direction, context)
        data_table = pandas.read_csv(f"{path}/{filename}", index_col="cycle_number")

        data_table.drop("events_between")
        point.data_table = data_table
        point.event_frames = data_table["events_between"].to_dict()
        return point


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
                n_cycle_point = NormalisedCyclePoint(r_cycle_point.label, r_cycle_point.translated_label,
                                                     r_cycle_point.direction, r_cycle_point.data_type, r_cycle_point.context)
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
