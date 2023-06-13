from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from pandas import DataFrame, concat

from gait_analysis.cycle.extraction import RawCyclePoint
from gait_analysis.utils.c3d import PointDataType


class BaseRawAnalysis(ABC):

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
        for key in self._data_list:# TODO change quick fix
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


class SpatioTemporalAnalysis(BaseRawAnalysis):

    def __init__(self, data_list: Dict[str, RawCyclePoint]):
        super().__init__(data_list, PointDataType.Angles)

    def analyse(self) -> DataFrame:
        pass


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


class JointAnglesAnalysis(BaseRawAnalysis):

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

        amplitude_rom = max_rom - min_rom

        raw_results = DataFrame({"cycle_number": data.keys()})
        raw_results['rom_min'] = min_rom
        raw_results['rom_max'] = max_rom
        raw_results['rom_amplitude'] = amplitude_rom
        return raw_results


class JointAngularVelocityAnalysis(BaseRawAnalysis):

    def __init__(self, data_list: Dict[str, RawCyclePoint]):
        super().__init__(data_list, PointDataType.Angles)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            return splits[3].lower() in splits[0]
        return False

    def _do_analysis(self, data: Dict[int, np.array]) -> DataFrame:
        max_rom = np.zeros(len(data))
        for cycle_number in data:
            angular_velocity = np.diff(data[cycle_number])
            max_rom[cycle_number - 1] = max(angular_velocity)

        raw_results = DataFrame({"cycle_number": data.keys()})

        raw_results['angle_velo_max'] = max_rom

        return raw_results
