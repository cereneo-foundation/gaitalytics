from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from pandas import DataFrame, concat

from gait_analysis.cycle.extraction import RawCyclePoint
from gait_analysis.utils.c3d import PointDataType, AxesNames, GaitEventContext
from gait_analysis.utils.config import ConfigProvider


class BaseRawCycleAnalysis(ABC):

    def __init__(self, data_list: Dict[str, RawCyclePoint], data_type: PointDataType):
        self._data_list = data_list
        self._point_data_type = data_type

    @abstractmethod
    def _do_analysis(self, data: Dict[int, np.array]) -> DataFrame:
        pass

    def _filter_keys(self, key: str, ) -> bool:
        """ Check if its the right point data """
        return f".{self._point_data_type.name}." in key

    def analyse(self) -> DataFrame:
        results = None
        for key in self._data_list:  # TODO change quick fix
            if self._filter_keys(key):
                raw_point = self._data_list[key]
                data = raw_point.data
                result = self._do_analysis(data)
                result['metric'] = key
                result['data_type'] = raw_point.data_type

                if results is None:
                    results = result
                else:
                    results = concat([results, result])
        return results


class JointAnglesCycleAnalysis(BaseRawCycleAnalysis):

    def __init__(self, data_list: Dict[str, RawCyclePoint]):
        super().__init__(data_list, PointDataType.Angles)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            return splits[3].lower() in splits[0]
        return False

    def _do_analysis(self, data: Dict[int, np.array]) -> DataFrame:
        max_rom = np.zeros(len(data))
        min_rom = np.zeros(len(data))
        for cycle_number in data:
            max_rom[cycle_number - 1] = max(data[cycle_number])
            min_rom[cycle_number - 1] = min(data[cycle_number])
            angular_velocity = np.diff(data[cycle_number])
            max_rom[cycle_number - 1] = max(angular_velocity)

        amplitude_rom = max_rom - min_rom

        raw_results = DataFrame({"cycle_number": data.keys()})
        raw_results['rom_min'] = min_rom
        raw_results['rom_max'] = max_rom
        raw_results['rom_amplitude'] = amplitude_rom
        raw_results['angle_velo_max'] = max_rom
        return raw_results


class SpatioTemporalAnalysis(BaseRawCycleAnalysis):

    def __init__(self, configs: ConfigProvider, data_list: Dict[str, RawCyclePoint], frequency: int = 100):
        super().__init__(data_list, PointDataType.Angles)
        self._configs = configs
        self._frequency = frequency

    def analyse(self) -> DataFrame:
        step_length = self._calculate_step_length()
        durations = self._calculate_durations()
        return step_length.merge(durations, on="cycle_number")

    def _calculate_durations(self):
        right_heel_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.RIGHT)]
        left_heel_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.LEFT)]
        right_cycle_duration, right_step_duration, right_swing_duration, right_stance_duration = self._side_duration_calculation(
            right_heel_progression)
        left_cycle_duration, left_step_duration, left_swing_duration, left_stance_duration = self._side_duration_calculation(
            left_heel_progression)

        left = DataFrame.from_dict(
            {"cycle_duration_left": left_cycle_duration,
             "step_duration_left": left_step_duration,
             "swing_duration_left": left_swing_duration,
             "stance_duration_left": left_stance_duration,
             "cycle_number": left_heel_progression.data.keys()})
        right = DataFrame.from_dict(
            {"cycle_duration_right": right_cycle_duration,
             "step_duration_right": right_step_duration,
             "swing_duration_right": right_swing_duration,
             "stance_duration_right": right_stance_duration,
             "cycle_number": right_heel_progression.data.keys()})
        return left.merge(right, how="cross", on="cycle_number")

    def _side_duration_calculation(self, progression):
        cycle_duration = np.zeros(len(progression.data))
        step_duration = np.zeros(len(progression.data))
        for i in progression.data:
            toe_off = progression.event_frames.loc[i]["events_between"]
            cycle_duration[i - 1] = len(progression.event_frames.loc[i]) / 100
            step_duration[i - 1] = len(progression.data[i][toe_off: -1]) / 100
        swing_duration = step_duration / cycle_duration * 100
        stance_duration = 100 - swing_duration
        return cycle_duration, step_duration, swing_duration, stance_duration

    def _calculate_step_length(self) -> DataFrame:
        right_heel_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.RIGHT)]
        left_toe_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_meta_2, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.RIGHT)]

        left_heel_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.LEFT)]
        right_toe_progression = self._data_list[
            ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_meta_2, PointDataType.Marker, AxesNames.y,
                                      GaitEventContext.LEFT)]

        step_length_right = self._side_step_length_calculation(left_toe_progression, right_heel_progression)
        step_length_left = self._side_step_length_calculation(right_toe_progression, left_heel_progression)

        left = DataFrame.from_dict(
            {"step_length_left": step_length_left, "cycle_number": right_heel_progression.data.keys()})
        left.index.name = "cycle_number"
        right = DataFrame.from_dict(
            {"step_length_right": step_length_right, "cycle_number": right_heel_progression.data.keys()})
        right.index.name = "cycle_number"
        return left.merge(right, how="cross", on="cycle_number")

    def _side_step_length_calculation(self, toe_progression, heel_progression):
        step_length = np.zeros(len(heel_progression.data))
        for i in heel_progression.data:
            toe_off = heel_progression.event_frames.loc[i]["events_between"]
            step_length[i - 1] = max(
                abs(heel_progression.data[i][toe_off: -1] - toe_progression.data[i][toe_off: -1]))
        return step_length

    def _do_analysis(self, data: Dict[int, np.array]) -> DataFrame:
        cycle_duration = np.zeros(len(data))  # sek
        step_duration = np.zeros(len(data))  # sek
        stance_duration = np.zeros(len(data))  # %GC
        swing_duration = np.zeros(len(data))  # %GC
        drag_duration_gc = np.zeros(len(data))  # %GC
        drag_duration_swing = np.zeros(len(data))  # %swing
        single_stance_duration = np.zeros(len(data))  # %GC
        double_stance_duration = np.zeros(len(data))  # %GC
        step_length = np.zeros(len(data))  # %BH
        stride_length = np.zeros(len(data))  # %BH
        step_width = np.zeros(len(data))  # %BH
        stride_speed = np.zeros(len(data))  # m/s
        stride_length_com = np.zeros(len(data))  # %BH
        stride_speed_com = np.zeros(len(data))  # m/s
        length_foot_trajectory = np.zeros(len(data))  # %BH
        length_com_trajectory = np.zeros(len(data))  # %BH
        step_height = np.zeros(len(data))  # %BH
        lateral_movement_during_swing = np.zeros(len(data))  # BH%
        max_hip_vertical_amplitude = np.zeros(len(data))  # BH%

        min_rom = np.zeros(len(data))
        for cycle_number in data:
            cycle_duration = np.zeros(len(data))  # sek
            step_duration = np.zeros(len(data))  # sek
            stance_duration = np.zeros(len(data))  # %GC
            swing_duration = np.zeros(len(data))  # %GC
            drag_duration_gc = np.zeros(len(data))  # %GC
            drag_duration_swing = np.zeros(len(data))  # %swing
            single_stance_duration = np.zeros(len(data))  # %GC
            double_stance_duration = np.zeros(len(data))  # %GC
            step_length = np.zeros(len(data))  # %BH
            stride_length = np.zeros(len(data))  # %BH
            step_width = np.zeros(len(data))  # %BH
            stride_speed = np.zeros(len(data))  # m/s
            stride_length_com = np.zeros(len(data))  # %BH
            stride_speed_com = np.zeros(len(data))  # m/s
            length_foot_trajectory = np.zeros(len(data))  # %BH
            length_com_trajectory = np.zeros(len(data))  # %BH
            step_height = np.zeros(len(data))  # %BH
            lateral_movement_during_swing = np.zeros(len(data))  # BH%
            max_hip_vertical_amplitude = np.zeros(len(data))  # BH%

        raw_results = DataFrame({"cycle_number": data.keys()})
        raw_results['min'] = min_rom
        return raw_results
