from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from pandas import DataFrame, concat

from gait_analysis.cycle.extraction import BasicCyclePoint
from gait_analysis.utils.c3d import PointDataType, AxesNames, GaitEventContext
from gait_analysis.utils.config import ConfigProvider


class BaseRawCycleAnalysis(ABC):

    def __init__(self, data_list: Dict, data_type: PointDataType):
        self._data_list = data_list
        self._point_data_type = data_type

    @abstractmethod
    def _do_analysis(self, data: DataFrame) -> DataFrame:
        pass

    def _filter_keys(self, key: str, ) -> bool:
        """ Check if its the right point data """
        return f".{self._point_data_type.name}." in key

    def analyse(self) -> DataFrame:
        results = None
        for key in self._data_list:  # TODO change quick fix
            if self._filter_keys(key):
                raw_point = self._data_list[key]
                data = raw_point.data_table
                result = self._do_analysis(data)
                result['metric'] = key
                result['data_type'] = raw_point.data_type

                if results is None:
                    results = result
                else:
                    results = concat([results, result])
        return results


class JointAnglesCycleAnalysis(BaseRawCycleAnalysis):

    def __init__(self, data_list: Dict):
        super().__init__(data_list, PointDataType.Angles)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            return splits[3].lower() in splits[0]
        return False

    def _do_analysis(self, data: DataFrame) -> DataFrame:
        results = DataFrame(index=data.index)
        rom_max = data.max(axis=1)
        rom_min = data.min(axis=1)
        results['rom_max'] = rom_max
        results['rom_min'] = rom_min
        results['rom_sd'] = data.std(axis=1)
        results['rom_amplitude'] = amplitude_rom = rom_max - data.min(axis=1)
        velocity = data.diff(axis=1)
        results['angle_velocity_max'] = velocity.max(axis=1)
        results['angle_velocity_min'] = velocity.min(axis=1)
        results['angle_velocity_sd'] = velocity.std(axis=1)
        return results


class SpatioTemporalAnalysis(BaseRawCycleAnalysis):

    def __init__(self, configs: ConfigProvider, data_list: Dict, frequency: int = 100):
        super().__init__(data_list, PointDataType.Angles)
        self._configs = configs
        self._frequency = frequency

    def analyse(self) -> DataFrame:

        step_length = self._calculate_step_length()
        durations = self._calculate_durations()
        result = step_length.merge(durations, on="cycle_number")
        result['data_type'] = "SpatioTemporal"
        result['metric'] = "SpatioTemporal"
        return result

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

        left = DataFrame(index=left_heel_progression.data_table.index)
        left["cycle_duration_left"] = left_cycle_duration
        left["step_duration_left"] = left_step_duration
        left["swing_duration_left"] = left_swing_duration
        left["stance_duration_left"] = left_stance_duration

        right = DataFrame(index=right_heel_progression.data_table.index)
        right["cycle_duration_right"] = right_cycle_duration
        right["step_duration_right"] = right_step_duration
        right["swing_duration_right"] = right_swing_duration
        right["stance_duration_right"] = right_stance_duration

        return concat([left, right], axis=1)

    def _side_duration_calculation(self, progression):
        cycle_duration = np.zeros(len(progression.data_table))
        step_duration = np.zeros(len(progression.data_table))
        for cycle_number in progression.data_table.index.to_series():
            toe_off = progression.event_frames.loc[cycle_number][BasicCyclePoint.EVENT_FRAME_NUMBER]
            cycle_data = progression.data_table.loc[cycle_number][~progression.data_table.loc[cycle_number].isna()]
            cycle_duration[cycle_number - 1] = len(cycle_data) / self._frequency
            step_duration[cycle_number - 1] = len(cycle_data[toe_off: -1]) / self._frequency
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
        left = DataFrame(index=left_heel_progression.data_table.index)
        left["step_length_left"] = step_length_left

        right = DataFrame(index=right_heel_progression.data_table.index)
        right["step_length_right"] = step_length_right

        return concat([left, right], axis=1)

    def _side_step_length_calculation(self, toe_progression, heel_progression):
        step_length = np.zeros(len(heel_progression.data_table))
        for cycle_number in heel_progression.data_table.index.to_series():
            toe_off = heel_progression.event_frames.loc[cycle_number][BasicCyclePoint.EVENT_FRAME_NUMBER]
            step_length[cycle_number - 1] = max(
                abs(heel_progression.data_table.loc[cycle_number][toe_off: -1] - toe_progression.data_table.loc[
                                                                                     cycle_number][toe_off: -1]))
        return step_length / 10  # mm to cm

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

        raw_results = DataFrame({"cycle_number": data.keys()})
        raw_results['min'] = min_rom
        return raw_results
