from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from pandas import DataFrame, concat

from . import utils, cycle, c3d


class AbstractAnalysis(ABC):
    def __init__(self, data_list: Dict[str, cycle.BasicCyclePoint]):
        self._data_list: Dict[str, cycle.BasicCyclePoint] = data_list

    def analyse(self) -> DataFrame:
        pass


class AbstractCycleAnalysis(AbstractAnalysis, ABC):

    def __init__(self, data_list: Dict[str, cycle.BasicCyclePoint], data_type: c3d.PointDataType):
        super().__init__(data_list)
        self._point_data_type = data_type

    @abstractmethod
    def _do_analysis(self, data: DataFrame) -> DataFrame:
        pass

    def _filter_keys(self, key: str) -> bool:
        """ Check if its the right point data """
        return f".{self._point_data_type.name}." in key

    def analyse(self, by_phase=True) -> DataFrame:
        results = None
        for key in self._data_list:  # TODO change quick fix
            if self._filter_keys(key):
                raw_point = self._data_list[key]
                data = raw_point.data_table
                if not by_phase:
                    result = self._do_analysis(data)
                    result['metric'] = key
                else:
                    standing = data.copy()
                    swinging = data.copy()
                    for row in range(len(data)):
                        event_frame = raw_point.event_frames.iloc[row][cycle.BasicCyclePoint.EVENT_FRAME_NUMBER]
                        swinging.iloc[row, 1:event_frame] = float("Nan")
                        standing.iloc[row, event_frame + 1: -1] = float("Nan")
                    result1 = self._do_analysis(standing)
                    result1['metric'] = f"{key}.standing"
                    result2 = self._do_analysis(swinging)
                    result2['metric'] = f"{key}.swinging"
                    result = concat([result1, result2])

                if results is None:
                    results = result
                else:
                    results = concat([results, result])
        return results.pivot(columns="metric")


class JointMomentsCycleAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict):
        super().__init__(data_list, c3d.PointDataType.Moments)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            return splits[3].lower() in splits[0]
        return False

    def _do_analysis(self, data: DataFrame) -> DataFrame:
        results = DataFrame(index=data.index)
        rom_max = data.max(axis=1)
        rom_min = data.min(axis=1)
        rom_mean = data.mean(axis=1)
        results['moments_mean'] = rom_mean
        results['moments_max'] = rom_max
        results['moments_min'] = rom_min
        results['moments_sd'] = data.std(axis=1)
        results['power_amplitude'] = rom_max - rom_min
        return results


class JointPowerCycleAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict):
        super().__init__(data_list, c3d.PointDataType.Power)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            if splits[3].lower() in splits[0]:
                return c3d.AxesNames.z.name is splits[2]
        return False

    def _do_analysis(self, data: DataFrame) -> DataFrame:
        results = DataFrame(index=data.index)
        rom_max = data.max(axis=1)
        rom_min = data.min(axis=1)
        rom_mean = data.mean(axis=1)
        results['power_mean'] = rom_mean
        results['power_max'] = rom_max
        results['power_min'] = rom_min
        results['power_sd'] = data.std(axis=1)
        results['power_amplitude'] = rom_max - rom_min
        return results


class JointAnglesCycleAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict):
        super().__init__(data_list, c3d.PointDataType.Angles)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            return splits[3].lower() in splits[0]
        return False

    def _do_analysis(self, data: DataFrame) -> DataFrame:
        results = DataFrame(index=data.index)
        rom_max = data.max(axis=1)
        rom_min = data.min(axis=1)
        rom_mean = data.mean(axis=1)
        results['rom_mean'] = rom_mean
        results['rom_max'] = rom_max
        results['rom_min'] = rom_min
        results['rom_sd'] = data.std(axis=1)
        results['rom_amplitude'] = rom_max - rom_min
        velocity = data.diff(axis=1)
        results['angle_velocity_max'] = velocity.max(axis=1)
        results['angle_velocity_min'] = velocity.min(axis=1)
        results['angle_velocity_sd'] = velocity.std(axis=1)
        return results


class SpatioTemporalAnalysis(AbstractAnalysis):

    def __init__(self, configs: utils.ConfigProvider, data_list: Dict, body_height: float = 1800, frequency: int = 100):
        super().__init__(data_list)
        self._configs = configs
        self._frequency = frequency
        self._body_height = body_height

    def analyse(self) -> DataFrame:
        step_length = self._calculate_length()
        durations = self._calculate_durations()

        step_height = self._calculate_step_height()
        step_width = self._calculate_step_width()
        result = step_length.merge(durations, on="cycle_number")
        result = result.merge(step_height, on="cycle_number")
        result = result.merge(step_width, on="cycle_number")
        result['metric'] = "Spatiotemporal"
        return result.pivot(columns="metric")

    def _calculate_step_width(self) -> DataFrame:
        right_heel_x_right = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                                             c3d.PointDataType.Marker,
                                                                             c3d.AxesNames.x,
                                                                             c3d.GaitEventContext.RIGHT)].data_table
        left_heel_x_right = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                                            c3d.PointDataType.Marker,
                                                                            c3d.AxesNames.x,
                                                                            c3d.GaitEventContext.RIGHT)].data_table
        right_heel_x_left = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                                            c3d.PointDataType.Marker,
                                                                            c3d.AxesNames.x,
                                                                            c3d.GaitEventContext.LEFT)].data_table
        left_heel_x_left = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                                           c3d.PointDataType.Marker,
                                                                           c3d.AxesNames.x,
                                                                           c3d.GaitEventContext.LEFT)].data_table

        right = self._calculate_step_width_side(right_heel_x_right, left_heel_x_right, "right")
        left = self._calculate_step_width_side(left_heel_x_left, right_heel_x_left, "left")

        return concat([left, right], axis=1)

    @staticmethod
    def _calculate_step_width_side(context_heel_x: DataFrame, contra_heel_x: DataFrame, side: str) -> DataFrame:
        column_label = f"step_width_{side}"
        width = DataFrame(index=context_heel_x.index, columns=[column_label])
        for cycle_number in context_heel_x.index.to_series():
            width_c = abs(context_heel_x.loc[cycle_number][1] - contra_heel_x.loc[cycle_number][1])
            width.loc[cycle_number][column_label] = width_c
        return width

    def _calculate_step_height(self) -> DataFrame:
        right_heel_z = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                                       c3d.PointDataType.Marker,
                                                                       c3d.AxesNames.z,
                                                                       c3d.GaitEventContext.RIGHT)].data_table
        left_heel_z = self._data_list[utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                                      c3d.PointDataType.Marker,
                                                                      c3d.AxesNames.z,
                                                                      c3d.GaitEventContext.LEFT)].data_table

        right = self._calculate_step_height_side(right_heel_z, "right")
        left = self._calculate_step_height_side(left_heel_z, "left")
        return concat([left, right], axis=1)

    @staticmethod
    def _calculate_step_height_side(heel_z: DataFrame, side: str) -> DataFrame:
        column_label = f"step_height_{side}"
        height = DataFrame(index=heel_z.index, columns=[column_label])
        height[column_label] = heel_z.max(axis=1) - heel_z.min(axis=1)
        return height

    def _calculate_durations(self):
        right_heel_progression = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.RIGHT)]
        left_heel_progression = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.LEFT)]
        right_durations = self._side_duration_calculation(right_heel_progression, "right")
        left_durations = self._side_duration_calculation(left_heel_progression, "left")

        return concat([left_durations, right_durations], axis=1)

    def _side_duration_calculation(self, progression: DataFrame, side: str) -> DataFrame:
        c_dur_label = f"cycle_duration_s_{side}"
        s_dur_label = f"step_duration_s_{side}"
        sw_dur_label = f"swing_duration_p_{side}"
        st_dur_label = f"stance_duration_p_{side}"
        columns = [c_dur_label, s_dur_label, sw_dur_label, st_dur_label]
        durations = DataFrame(index=progression.data_table.index, columns=columns)
        for cycle_number in progression.data_table.index.to_series():
            toe_off = progression.event_frames.loc[cycle_number][cycle.BasicCyclePoint.EVENT_FRAME_NUMBER]
            cycle_data = progression.data_table.loc[cycle_number][~progression.data_table.loc[cycle_number].isna()]

            durations.loc[cycle_number][c_dur_label] = len(cycle_data) / self._frequency
            durations.loc[cycle_number][s_dur_label] = len(cycle_data[toe_off: -1]) / self._frequency
        swing_percent = durations[s_dur_label] / durations[c_dur_label]
        durations[sw_dur_label] = swing_percent
        durations[st_dur_label] = 100 - durations[sw_dur_label]
        return durations

    def _calculate_length(self) -> DataFrame:
        right_heel_progression_right = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.RIGHT)].data_table
        left_heel_progression_right = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.RIGHT)].data_table

        left_heel_progression_left = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.LEFT)].data_table
        right_heel_progression_left = self._data_list[
            utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                            c3d.PointDataType.Marker,
                                            c3d.AxesNames.y,
                                            c3d.GaitEventContext.LEFT)].data_table

        right = self._side_step_length_calculation(right_heel_progression_right,
                                                   left_heel_progression_right, "right")
        left = self._side_step_length_calculation(left_heel_progression_left,
                                                  right_heel_progression_left, "left")

        results = concat([left, right], axis=1)
        results['stride_length'] = results["step_length_right"] + results["step_length_left"]

        return results

    @staticmethod
    def _side_step_length_calculation(context_heel_progression: DataFrame,
                                      contra_heel_progression: DataFrame, side: str) -> np.array:
        s_len_label = f"step_length_{side}"
        step_length = DataFrame(index=context_heel_progression.index, columns=[s_len_label])

        for cycle_number in context_heel_progression.index.to_series():
            context_hs_pos = context_heel_progression.loc[cycle_number][1]
            contra_hs_pos = contra_heel_progression.loc[cycle_number][1]
            step_length.loc[cycle_number][s_len_label] = abs(context_hs_pos - contra_hs_pos)

        return step_length

    # drag_duration_gc = np.zeros(len(data))  # %GC
    # drag_duration_swing = np.zeros(len(data))  # %swing
    # single_stance_duration = np.zeros(len(data))  # %GC
    # double_stance_duration = np.zeros(len(data))  # %GC
    # stride_speed = np.zeros(len(data))  # m/s
    # stride_length_com = np.zeros(len(data))  # %BH
    # stride_speed_com = np.zeros(len(data))  # m/s
    # length_foot_trajectory = np.zeros(len(data))  # %BH
    # length_com_trajectory = np.zeros(len(data))  # %BH
    # lateral_movement_during_swing = np.zeros(len(data))  # BH%
    # max_hip_vertical_amplitude = np.zeros(len(data))  # BH%


class MinimalClearingDifference(AbstractAnalysis):

    def __int__(self, data_list: Dict[str, cycle.BasicCyclePoint]):
        super().__init__(data_list)

    def analyse(self) -> DataFrame:
        pass

class AbstractNormalisedAnalysis(ABC):

    def __init__(self, data_list: {}):
        self.data_list = data_list

    @abstractmethod
    def _do_analysis(self, table: DataFrame) -> DataFrame:
        pass

    def analyse(self) -> DataFrame:
        results = None
        for key in self.data_list:
            table = self.data_list[key].data_table
            result = self._do_analysis(table)
            result['metric'] = key
            result['event_frame'] = self.data_list[key].get_mean_event_frame()
            result['data_type'] = self.data_list[key].data_type
            if results is None:
                results = result
            else:
                results = concat([results, result])
        return results


class DescriptiveNormalisedAnalysis(AbstractNormalisedAnalysis):

    def _do_analysis(self, table: DataFrame) -> DataFrame:
        frame_number = np.arange(1, 101, 1)  # Could be something like myRange = range(1,1000,1)
        result = DataFrame(index=frame_number)
        result.index.name = "frame_number"
        result['mean'] = table.mean(axis=0).to_list()
        result['sd'] = table.std(axis=0).to_list()
        result['max'] = table.max(axis=0).to_list()
        result['min'] = table.min(axis=0).to_list()
        result['median'] = table.median(axis=0).to_list()
        result['sd_up'] = result.apply(lambda row: row['mean'] + row['sd'], axis=1)
        result['sd_down'] = result.apply(lambda row: row['mean'] - row['sd'], axis=1)
        return result
