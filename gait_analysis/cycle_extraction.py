from __future__ import annotations

from abc import ABC, abstractmethod
from math import ceil
from typing import Dict

import numpy as np
from btk import btkAcquisition

from gait_analysis.api import GaitCycleList, GaitCycle, BasicCyclePoint, GaitEventLabel, ConfigProvider
from gait_analysis.events import EventAnomalyChecker, find_next_event
from gait_analysis.c3d import AxesNames, PointDataType, GaitEventContext


# Cycle Builder
class CycleBuilder(ABC):

    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
        self.eventAnomalyChecker = event_anomaly_checker

    def build_cycles(self, aqc: btkAcquisition) -> GaitCycleList:
        [detected, detail_tuple] = self.eventAnomalyChecker.check_events(aqc)
        if detected:
            raise RuntimeError(detail_tuple)

        return self._build(aqc)

    @abstractmethod
    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        pass


class EventCycleBuilder(CycleBuilder):
    def __init__(self, event_anomaly_checker: EventAnomalyChecker, event: GaitEventLabel):
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
    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
        super().__init__(event_anomaly_checker, GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
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
                    cycle.unused_event.GetFrame() - cycle.start_frame, cycle.number)


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
