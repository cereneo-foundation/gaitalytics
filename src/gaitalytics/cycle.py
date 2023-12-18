from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List

import numpy as np
from pandas import DataFrame

import gaitalytics.events
import gaitalytics.utils
import gaitalytics.files


# Cycle Builder
class CycleBuilder(ABC):

    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
        self.eventAnomalyChecker = event_anomaly_checker

    def build_cycles(self, file_handler: gaitalytics.files.FileHandler) -> gaitalytics.utils.GaitCycleList:
        if file_handler.get_events_size() < 1:
            raise AttributeError("No Events in File")
        else:
            [detected, detail_tuple] = self.eventAnomalyChecker.check_events(file_handler)
            if detected:
                raise RuntimeError(detail_tuple)

        return self._build(file_handler)

    @abstractmethod
    def _build(self, file_handler: gaitalytics.files.FileHandler) -> gaitalytics.utils.GaitCycleList:
        pass


class EventCycleBuilder(CycleBuilder):
    def __init__(self,
                 event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker,
                 event: gaitalytics.utils.GaitEventLabel):
        super().__init__(event_anomaly_checker)
        self.event_label = event.value

    def _build(self, file_handler: gaitalytics.files.FileHandler) -> gaitalytics.utils.GaitCycleList:
        gait_cycles = gaitalytics.utils.GaitCycleList()
        numbers = {gaitalytics.utils.GaitEventContext.LEFT.value: 0,
                   gaitalytics.utils.GaitEventContext.RIGHT.value: 0}
        for event_index in range(0, file_handler.get_events_size()):
            start_event = file_handler.get_event(event_index)
            context = start_event.context

            label = start_event.label
            if label == self.event_label:
                try:
                    [end_event, unused_events] = gaitalytics.events.find_next_event(file_handler,
                                                                                    label,
                                                                                    context,
                                                                                    event_index)
                    if end_event is not None:
                        numbers[context] = numbers[context] + 1
                        cycle = gaitalytics.utils.GaitCycle(numbers[context],
                                                            gaitalytics.utils.GaitEventContext(context),
                                                            start_event.frame, end_event.frame,
                                                            unused_events)
                        gait_cycles.add_cycle(cycle)
                except IndexError as err:
                    pass  # If events do not match in the end this will be raised
        return gait_cycles


class HeelStrikeToHeelStrikeCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, gaitalytics.utils.GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: gaitalytics.events.AbstractEventAnomalyChecker):
        super().__init__(event_anomaly_checker, gaitalytics.utils.GaitEventLabel.FOOT_OFF)


# Cycle Extractor
class CycleDataExtractor:
    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        self._configs = configs

    def extract_data(self,
                     cycles: gaitalytics.utils.GaitCycleList,
                     file_handler: gaitalytics.files.FileHandler) -> Dict[str, gaitalytics.utils.BasicCyclePoint]:
        subject = file_handler.get_subject_measures()
        data_list: Dict[str, gaitalytics.utils.BasicCyclePoint] = {}
        for point_index in range(0, file_handler.get_points_size()):
            cycle_counts_left = len(cycles.left_cycles.values())
            cycle_counts_right = len(cycles.right_cycles.values())
            cycle_counts = 0
            if cycle_counts_left > cycle_counts_right:
                cycle_counts = cycle_counts_right
            else:
                cycle_counts = cycle_counts_left

            longest_cycle_left = cycles.get_longest_cycle_length(gaitalytics.utils.GaitEventContext.LEFT)
            longest_cycle_right = cycles.get_longest_cycle_length(gaitalytics.utils.GaitEventContext.RIGHT)

            point = file_handler.get_point(point_index)

            for direction_index in range(0, len(point.values[0])):
                label = point.label
                data_type = point.type
                translated_label = self._configs.get_translated_label(label, data_type)
                if translated_label is not None:
                    direction = gaitalytics.utils.AxesNames(direction_index)
                    left = self._create_point_cycle(cycle_counts, longest_cycle_left, translated_label,
                                                    direction, data_type, gaitalytics.utils.GaitEventContext.LEFT,
                                                    subject)
                    right = self._create_point_cycle(cycle_counts, longest_cycle_right, translated_label,
                                                     direction, data_type,
                                                     gaitalytics.utils.GaitEventContext.RIGHT,
                                                     subject)

                    for cycle_number in range(1, cycles.get_number_of_cycles() + 1):
                        if len(cycles.right_cycles) + 1 > cycle_number:
                            self._extract_cycle(right, cycles.right_cycles[cycle_number],
                                                point.values[:, direction_index])
                        if len(cycles.left_cycles) + 1 > cycle_number:
                            self._extract_cycle(left, cycles.left_cycles[cycle_number],
                                                point.values[:, direction_index])

                    key_left = gaitalytics.utils.ConfigProvider.define_key(translated_label, data_type, direction,
                                                                           gaitalytics.utils.GaitEventContext.LEFT)
                    key_right = gaitalytics.utils.ConfigProvider.define_key(translated_label, data_type, direction,
                                                                            gaitalytics.utils.GaitEventContext.RIGHT)
                    data_list[key_left] = left
                    data_list[key_right] = right

        return data_list

    @staticmethod
    def _create_point_cycle(cycle_counts: int,
                            longest_cycle,
                            label: Enum,
                            direction: gaitalytics.utils.AxesNames,
                            data_type: gaitalytics.utils.PointDataType,
                            context: gaitalytics.utils.GaitEventContext,
                            subject: gaitalytics.utils.SubjectMeasures) -> gaitalytics.utils.TestCyclePoint:
        cycle = gaitalytics.utils.TestCyclePoint(cycle_counts, longest_cycle,
                                                 gaitalytics.utils.BasicCyclePoint.TYPE_RAW)
        cycle.direction = direction
        cycle.context = context
        cycle.translated_label = label
        cycle.data_type = data_type
        cycle.subject = subject
        return cycle

    @staticmethod
    def _extract_cycle(cycle_point: gaitalytics.utils.TestCyclePoint,
                       cycle: gaitalytics.utils.GaitCycle, values: np.array):
        cycle_point.data_table.loc[cycle.number][0:cycle.length] = values[cycle.start_frame: cycle.end_frame]
        events = np.array(list(cycle.unused_events.values()))
        events = events - cycle.start_frame
        cycle_point.event_frames.loc[cycle.number] = events
        cycle_point.frames.loc[cycle.number] = [cycle.start_frame, cycle.end_frame]


# Normalisation
class TimeNormalisationAlgorithm(ABC):

    def __init__(self, number_frames: int = 100):
        self._number_frames = number_frames
        self._data_type_fiter = {gaitalytics.utils.PointDataType.Marker,
                                 gaitalytics.utils.PointDataType.Angles,
                                 gaitalytics.utils.PointDataType.Forces,
                                 gaitalytics.utils.PointDataType.Moments,
                                 gaitalytics.utils.PointDataType.Power,
                                 gaitalytics.utils.PointDataType.Scalar,
                                 gaitalytics.utils.PointDataType.Reaction}

    def normalise(self,
                  r_data_list: Dict[str, gaitalytics.utils.BasicCyclePoint]) -> \
            Dict[str, gaitalytics.utils.BasicCyclePoint]:
        n_data_list = {}
        for data_key in r_data_list:
            r_cycle_point = r_data_list[data_key]
            if r_cycle_point.data_type in self._data_type_fiter:
                n_cycle_point = gaitalytics.utils.TestCyclePoint(len(r_cycle_point.data_table),
                                                                 self._number_frames,
                                                                 gaitalytics.utils.BasicCyclePoint.TYPE_NORM)
                n_cycle_point.cycle_point_type = gaitalytics.utils.BasicCyclePoint.TYPE_NORM
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


class CyclePointLoader:

    def __init__(self, configs: gaitalytics.utils.ConfigProvider, dir_path: str):
        self._raw_cycle_data = {}
        self._norm_cycle_data = {}
        file_names = os.listdir(dir_path)
        postfix = gaitalytics.utils.BasicCyclePoint.TYPE_RAW
        raw_file_names = self._filter_filenames(file_names, postfix)
        subject = gaitalytics.utils.SubjectMeasures.from_file(f"{dir_path}/subject.yml")
        self._raw_cycle_data = self._init_buffered_points(configs, dir_path, raw_file_names, subject)

        postfix = gaitalytics.utils.BasicCyclePoint.TYPE_NORM
        norm_file_names = self._filter_filenames(file_names, postfix)
        self._norm_cycle_data = self._init_buffered_points(configs, dir_path, norm_file_names, subject)

    @staticmethod
    def _init_buffered_points(configs: gaitalytics.utils.ConfigProvider,
                              dir_path: str,
                              file_names: List[str],
                              subject: gaitalytics.utils.SubjectMeasures) -> \
            Dict[str, gaitalytics.utils.BasicCyclePoint]:
        cycle_data: Dict[str, gaitalytics.utils.BasicCyclePoint] = {}
        for file_name in file_names:
            point = gaitalytics.utils.BufferedCyclePoint(configs, dir_path, file_name, subject)
            foo, key, foo = gaitalytics.utils.get_key_from_filename(file_name)
            cycle_data[key] = point
        return cycle_data

    @classmethod
    def _filter_filenames(cls, file_names, postfix) -> List[str]:
        r = re.compile(f".*{gaitalytics.utils.FILENAME_DELIMITER}{postfix}.*\.csv")
        return list(filter(r.match, file_names))

    def get_raw_cycle_points(self) -> Dict[str, gaitalytics.utils.BasicCyclePoint]:
        return self._raw_cycle_data

    def get_norm_cycle_points(self) -> Dict[str, gaitalytics.utils.BasicCyclePoint]:
        return self._norm_cycle_data
