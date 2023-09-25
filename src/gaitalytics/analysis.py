from abc import ABC, abstractmethod
from typing import Dict

import numpy as np
from pandas import DataFrame, concat
from scipy import signal

import gaitalytics.utils
import logging

logger = logging.getLogger(__name__)
class AbstractAnalysis(ABC):
    def __init__(self, data_list: Dict[str, gaitalytics.utils.BasicCyclePoint],
                 configs: gaitalytics.utils.ConfigProvider):
        self._data_list: Dict[str, gaitalytics.utils.BasicCyclePoint] = data_list
        self._configs = configs

    def analyse(self, **kwargs) -> DataFrame:
        pass


class AbstractCycleAnalysis(AbstractAnalysis, ABC):

    def __init__(self, data_list: Dict[str, gaitalytics.utils.BasicCyclePoint],
                 configs: gaitalytics.utils.ConfigProvider,
                 data_type: gaitalytics.utils.PointDataType):
        super().__init__(data_list, configs)
        self._point_data_type = data_type

    @abstractmethod
    def _do_analysis(self, data: DataFrame) -> DataFrame:
        pass

    def _filter_keys(self, key: str) -> bool:
        """ Check if its the right point data """
        return f".{self._point_data_type.name}." in key

    def analyse(self, **kwargs) -> DataFrame:
        logger.info(f"analyse: {self._point_data_type}")
        by_phase = kwargs.get("by_phase", True)
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
                        event_frame = raw_point.event_frames.iloc[row][
                            gaitalytics.utils.BasicCyclePoint.FOOT_OFF]
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


class JointForcesCycleAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs, gaitalytics.utils.PointDataType.Forces)

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
        results['forces_mean'] = rom_mean
        results['forces_max'] = rom_max
        results['forces_min'] = rom_min
        results['forces_sd'] = data.std(axis=1)
        results['forces_amplitude'] = rom_max - rom_min
        return results


class JointMomentsCycleAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs, gaitalytics.utils.PointDataType.Moments)

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

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs, gaitalytics.utils.PointDataType.Power)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            splits = key.split(".")
            if splits[3].lower() in splits[0]:
                return gaitalytics.utils.AxesNames.z.name is splits[2]
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

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs, gaitalytics.utils.PointDataType.Angles)

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


class CMosAnalysis(AbstractCycleAnalysis):

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs, gaitalytics.utils.PointDataType.Marker)

    def _filter_keys(self, key: str) -> bool:
        if super()._filter_keys(key):
            useful = self._configs.MARKER_MAPPING.cmos.name in key
            return useful
        return False

    def _do_analysis(self, data: DataFrame) -> DataFrame:
        results = DataFrame(index=data.index)

        results['cmos_mean'] = data.mean(axis=1)
        results['cmos_max'] = data.max(axis=1)
        results['cmos_min'] = data.min(axis=1)
        results['cmos_sd'] = data.std(axis=1)

        return results


class MosAnalysis(AbstractAnalysis):

    def analyse(self, **kwargs) -> DataFrame:
        left_cmos_ap = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_cmos,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]
        left_cmos_ml = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_cmos,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]

        right_cmos_ap = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_cmos,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        right_cmos_ml = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_cmos,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]

        left_ap = self._extract_mos_frames(left_cmos_ap, "left", "ap")
        left_ml = self._extract_mos_frames(left_cmos_ml, "left", "ml")
        right_ap = self._extract_mos_frames(right_cmos_ap, "right", "ap")
        right_ml = self._extract_mos_frames(right_cmos_ml, "right", "ml")
        result = left_ap.merge(left_ml, on=gaitalytics.utils.BasicCyclePoint.CYCLE_NUMBER)
        result = result.merge(right_ap, on=gaitalytics.utils.BasicCyclePoint.CYCLE_NUMBER)
        result = result.merge(right_ml, on=gaitalytics.utils.BasicCyclePoint.CYCLE_NUMBER)


        result['metric'] = "Mos"
        return result.pivot(columns="metric")

    @staticmethod
    def _extract_mos_frames(cmos: gaitalytics.utils.BasicCyclePoint.CYCLE_NUMBER, side, direction):
        hs_label = f"{direction}_hs_{side}"
        to_label = f"{direction}_to_{side}"
        hs_contra_label = f"{direction}_hs_contra_{side}"
        to_contra_label = f"{direction}_to_contra_{side}"
        column_label = [hs_label, to_label, hs_contra_label, to_contra_label]

        result = DataFrame(index=cmos.data_table.index)
        result[hs_label] = cmos.data_table[0].to_list()
        for cycle_number in cmos.event_frames.index.to_list():
            to_frame = cmos.event_frames[gaitalytics.utils.BasicCyclePoint.FOOT_OFF].loc[cycle_number]
            hs_contra_frame = cmos.event_frames[gaitalytics.utils.BasicCyclePoint.FOOT_STRIKE_CONTRA].loc[cycle_number]
            to_contra_frame = cmos.event_frames[gaitalytics.utils.BasicCyclePoint.FOOT_OFF_CONTRA].loc[cycle_number]
            result.loc[cycle_number, to_label] = cmos.data_table.loc[cycle_number, to_frame]
            result.loc[cycle_number, hs_contra_label] = cmos.data_table.loc[cycle_number, hs_contra_frame]
            result.loc[cycle_number, to_contra_label] = cmos.data_table.loc[cycle_number, to_contra_frame]
        return result


class SpatioTemporalAnalysis(AbstractAnalysis):

    def __init__(self, data_list: Dict, configs: gaitalytics.utils.ConfigProvider, body_height: float = 1800,
                 frequency: int = 100):
        super().__init__(data_list, configs)
        self._frequency = frequency
        self._body_height = body_height

    def analyse(self, **kwargs) -> DataFrame:
        subject = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].subject
        step_length = self._calculate_length(subject)
        durations = self._calculate_durations()

        step_height = self._calculate_step_height(subject)
        step_width = self._calculate_step_width(subject)
        limb_circumduction = self._calculate_limb_circumduction()

        double_support_duration = self._calculate_double_support_duration()
        single_support_duration = self._calculate_single_support_duration()

        result = step_length.merge(durations, on="cycle_number")
        result = result.merge(step_height, on="cycle_number")
        result = result.merge(step_width, on="cycle_number")
        result = result.merge(limb_circumduction, on="cycle_number")
        result = result.merge(double_support_duration, on ="cycle_number")
        result = result.merge(single_support_duration, on ="cycle_number")
        result['metric'] = "Spatiotemporal"
        return result.pivot(columns="metric")

    def _calculate_step_width(self, subject: gaitalytics.utils.SubjectMeasures) -> DataFrame:

        right_heel_x_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].data_table
        left_heel_x_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].data_table
        right_heel_x_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.LEFT)].data_table
        left_heel_x_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.LEFT)].data_table

        right = self._calculate_step_width_side(right_heel_x_right, left_heel_x_right, subject.body_height, "right")
        left = self._calculate_step_width_side(left_heel_x_left, right_heel_x_left, subject.body_height, "left")

        return concat([left, right], axis=1)

    @staticmethod
    def _calculate_step_width_side(context_heel_x: DataFrame, contra_heel_x: DataFrame, body_height: float,
                                   side: str) -> DataFrame:
        # TODO: Medial marker
        column_label = f"step_width_{side}"
        width = DataFrame(index=context_heel_x.index, columns=[column_label])
        for cycle_number in context_heel_x.index.to_series():
            width_c = abs(context_heel_x.loc[cycle_number][1] - contra_heel_x.loc[cycle_number][1])
            width.loc[cycle_number][column_label] = width_c / body_height
        return width






    def _calculate_limb_circumduction(self) -> DataFrame:
        #subject.
        right_malleoli_x_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_med_malleoli,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        left_malleoli_x_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_med_malleoli,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.x,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]

        left = self._calculate_limb_circumduction_side(left_malleoli_x_left, "left")
        right = self._calculate_limb_circumduction_side(right_malleoli_x_right, "right")

        return concat([left, right], axis=1)

    #@staticmethod
   # def _calculate_limb_circumduction_side(context_malleoli_x: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
       # context_malleoli_x.data_table
        #context_malleoli_x.event_frames
        #
       # column_label = f"limb_circumduction_{side}"
      # limb_circumduction = DataFrame(index=context_malleoli_x.data_table.index, columns=[column_label])
      # for cycle_number in context_malleoli_x.data_table.index.to_series():
     #       id_foot_off = context_malleoli_x.event_frames.loc[cycle_number]['Foot_Off']
     #       id_heel_strike_end = context_malleoli_x.frames.loc[cycle_number]['end_frame'] - context_malleoli_x.frames.loc[cycle_number]['start_frame'] -1
     #       if side == "right":
    #            context_malleoli_x.data_table = context_malleoli_x.data_table*(-1)
    #        limb_circumduction.loc[cycle_number][column_label] = max(context_malleoli_x.data_table.iloc[cycle_number, id_foot_off:id_heel_strike_end]) - context_malleoli_x.data_table.loc[cycle_number][id_foot_off]
    #    return limb_circumduction

  #  @staticmethod
   # def _calculate_limb_circumduction_side(context_malleoli_x: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
     #   column_label = f"limb_circumduction_{side}"
      #  limb_circumduction = DataFrame(index=context_malleoli_x.data_table.index, columns=[column_label])
       # for cycle_number in context_malleoli_x.data_table.index.to_series():
       #     id_foot_off = context_malleoli_x.event_frames.loc[cycle_number]['Foot_Off']
      #      id_heel_strike_end = context_malleoli_x.frames.loc[cycle_number]['end_frame'] - context_malleoli_x.frames.loc[cycle_number]['start_frame'] -1
      #      if side == "right":
      #          context_malleoli_x.data_table = context_malleoli_x.data_table*(-1)
       #     limb_circumduction.loc[cycle_number][column_label] = max(context_malleoli_x.data_table.iloc[cycle_number, id_foot_off:id_heel_strike_end]) - context_malleoli_x.data_table.loc[cycle_number][id_foot_off]
      #  return limb_circumduction

    @staticmethod
    def _calculate_limb_circumduction_side(context_malleoli_x: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
        column_label = f"limb_circumduction_{side}"
        limb_circumduction = DataFrame(index=context_malleoli_x.data_table.index, columns=[column_label])
        data = context_malleoli_x.data_table
        if side =="right":
            data = data * -1
        for cycle_number in context_malleoli_x.data_table.index.to_series():
            id_foot_off = context_malleoli_x.event_frames.loc[cycle_number]['Foot_Off']
            id_heel_strike_end = context_malleoli_x.frames.loc[cycle_number]['end_frame'] - context_malleoli_x.frames.loc[cycle_number]['start_frame']
            max_data = max(data.iloc[cycle_number -1, id_foot_off:id_heel_strike_end])
            data_TO = data.loc[cycle_number][id_foot_off]
            limb_circumduction.loc[cycle_number][column_label] = max_data - data_TO

        return limb_circumduction

    # limb_circumduction.loc[cycle_number][column_label] = max(context_malleoli_x.data_table.iloc[cycle_number, id_foot_off:id_heel_strike_end]) - context_malleoli_x.data_table.loc[cycle_number][id_foot_off]

    def _calculate_double_support_duration(self) -> DataFrame:
        # subject.
        right_heel_y_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        left_heel_y_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]

        left = self._calculate_double_support_duration_side(left_heel_y_right, "left")
        right = self._calculate_double_support_duration_side(right_heel_y_right, "right")

        return concat([left, right], axis=1)

    def _calculate_double_support_duration_side(self, progression: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
        dsd_1 = f"double_support_duration_1_{side}"
        dsd_2 = f"double_support_duration_2_{side}"
        columns = [dsd_1, dsd_2]
        durations = DataFrame(index=progression.data_table.index, columns=columns)
        for cycle_number in progression.data_table.index.to_series():

            id_foot_off_contra = progression.event_frames.loc[cycle_number]['Foot_Off_Contra']
            time_foot_off_contra = (id_foot_off_contra + 1) / self._frequency

            id_heel_strike_contra = progression.event_frames.loc[cycle_number]['Foot_Strike_Contra']
            time_heel_strike_contra = (id_heel_strike_contra + 1) / self._frequency

            id_toe_off = progression.event_frames.loc[cycle_number]['Foot_Off']
            time_toe_off = (id_toe_off + 1) / self._frequency

            durations.loc[cycle_number][dsd_1] = time_foot_off_contra
            durations.loc[cycle_number][dsd_2] = time_toe_off - time_heel_strike_contra
        return durations

    def _calculate_single_support_duration(self) -> DataFrame:
        # subject.
        right_heel_y_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        left_heel_y_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]

        left = self._calculate_single_support_duration_side(left_heel_y_left, "left")
        right = self._calculate_single_support_duration_side(right_heel_y_right, "right")

        return concat([left, right], axis=1)

    def _calculate_single_support_duration_side(self, progression: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
        ssd = f"single_support_duration_{side}"
        columns = [ssd]
        durations = DataFrame(index=progression.data_table.index, columns=columns)
        for cycle_number in progression.data_table.index.to_series():

            id_foot_off_contra = progression.event_frames.loc[cycle_number]['Foot_Off_Contra']
            time_foot_off_contra = (id_foot_off_contra + 1) / self._frequency

            id_heel_strike_contra = progression.event_frames.loc[cycle_number]['Foot_Strike_Contra']
            time_heel_strike_contra = (id_heel_strike_contra + 1) / self._frequency

            durations.loc[cycle_number][ssd] = time_heel_strike_contra - time_foot_off_contra
        return durations







    def _calculate_step_height(self, subject: gaitalytics.utils.SubjectMeasures) -> DataFrame:
        right_heel_z = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.z,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].data_table
        left_heel_z = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.z,
                                                        gaitalytics.utils.GaitEventContext.LEFT)].data_table

        right = self._calculate_step_height_side(right_heel_z, subject.body_height, "right")
        left = self._calculate_step_height_side(left_heel_z, subject.body_height, "left")
        return concat([left, right], axis=1)

    @staticmethod
    def _calculate_step_height_side(heel_z: DataFrame, body_height: float, side: str) -> DataFrame:
        column_label = f"step_height_{side}"
        height = DataFrame(index=heel_z.index, columns=[column_label])
        height[column_label] = (heel_z.max(axis=1) - heel_z.min(axis=1)) / body_height
        return height

    def _calculate_durations(self):
        right_heel_progression = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        left_heel_progression = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)]
        right_durations = self._side_duration_calculation(right_heel_progression, "right")
        left_durations = self._side_duration_calculation(left_heel_progression, "left")

        return concat([left_durations, right_durations], axis=1)

    def _side_duration_calculation(self, progression: gaitalytics.utils.BasicCyclePoint, side: str) -> DataFrame:
        c_dur_label = f"cycle_duration_s_{side}"
        s_dur_label = f"step_duration_s_{side}"
        sw_dur_label = f"swing_duration_p_{side}"
        st_dur_label = f"stance_duration_p_{side}"
        columns = [c_dur_label, s_dur_label, sw_dur_label, st_dur_label]
        durations = DataFrame(index=progression.data_table.index, columns=columns)
        for cycle_number in progression.data_table.index.to_series():
            toe_off = progression.event_frames.loc[cycle_number][gaitalytics.utils.BasicCyclePoint.FOOT_OFF]
            cycle_data = progression.data_table.loc[cycle_number][~progression.data_table.loc[cycle_number].isna()]

            durations.loc[cycle_number][c_dur_label] = len(cycle_data) / self._frequency
            durations.loc[cycle_number][s_dur_label] = len(cycle_data[toe_off: -1]) / self._frequency
        swing_percent = durations[s_dur_label] / durations[c_dur_label]
        durations[sw_dur_label] = swing_percent
        durations[st_dur_label] = 1 - durations[sw_dur_label]
        return durations

    def _calculate_length(self, subject: gaitalytics.utils.SubjectMeasures) -> DataFrame:
        right_heel_progression_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].data_table
        left_heel_progression_right = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)].data_table

        left_heel_progression_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)].data_table
        right_heel_progression_left = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_heel,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.y,
                                                        gaitalytics.utils.GaitEventContext.LEFT)].data_table

        right = self._side_step_length_calculation(right_heel_progression_right,
                                                   left_heel_progression_right, subject.body_height, "right")
        left = self._side_step_length_calculation(left_heel_progression_left,
                                                  right_heel_progression_left, subject.body_height, "left")

        results = concat([left, right], axis=1)
        ## Todo: check stride length
        results['stride_length'] = results["step_length_right"] + results["step_length_left"]

        return results

    @staticmethod
    def _side_step_length_calculation(context_heel_progression: DataFrame,
                                      contra_heel_progression: DataFrame, body_height: float, side: str) -> np.array:
        # TODO: checks step definition
        s_len_label = f"step_length_{side}"
        step_length = DataFrame(index=context_heel_progression.index, columns=[s_len_label])

        for cycle_number in context_heel_progression.index.to_series():
            context_hs_pos = context_heel_progression.loc[cycle_number][1]
            contra_hs_pos = contra_heel_progression.loc[cycle_number][1]
            step_length.loc[cycle_number][s_len_label] = abs(context_hs_pos - contra_hs_pos) / body_height

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

    def __init__(self, data_list: Dict[str, gaitalytics.utils.BasicCyclePoint],
                 configs: gaitalytics.utils.ConfigProvider):
        super().__init__(data_list, configs)

    def analyse(self, **kwargs) -> DataFrame:
        right_toe = self._data_list[
            gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.right_meta_2,
                                                        gaitalytics.utils.PointDataType.Marker,
                                                        gaitalytics.utils.AxesNames.z,
                                                        gaitalytics.utils.GaitEventContext.RIGHT)]
        left_toe = self._data_list[gaitalytics.utils.ConfigProvider.define_key(self._configs.MARKER_MAPPING.left_meta_2,
                                                                               gaitalytics.utils.PointDataType.Marker,
                                                                               gaitalytics.utils.AxesNames.z,
                                                                               gaitalytics.utils.GaitEventContext.LEFT)]

        right = self._calculate_minimal_clearance(right_toe.data_table, right_toe.event_frames, "right")
        left = self._calculate_minimal_clearance(left_toe.data_table, left_toe.event_frames, "left")
        result = concat([left, right], axis=1)
        result['metric'] = "MinimalToeClearance"
        return result.pivot(columns="metric")

    @staticmethod
    def _calculate_minimal_clearance(toe: DataFrame, event_frames: DataFrame, side: str) -> DataFrame:
        s_mtc_label = f"minimal_toe_clearance_{side}"
        s_mtc_cycle_label = f"minimal_toe_clearance_swing_p_{side}"
        s_tc_hs_label = f"toe_clearance_heel_strike_{side}"
        toe_clearance = DataFrame(index=toe.index, columns=[s_mtc_label, s_mtc_cycle_label, s_tc_hs_label])
        for cycle_number in toe.index.to_series():
            toe_off_frame = event_frames.loc[cycle_number][gaitalytics.utils.BasicCyclePoint.FOOT_OFF]
            swing_phase_data = toe.loc[cycle_number][toe_off_frame: -1]
            mid_swing_index = round(len(swing_phase_data) / 2)
            peaks = signal.find_peaks(swing_phase_data[0:mid_swing_index], distance=len(swing_phase_data))
            toe_clear_min = min(swing_phase_data[peaks[0][0]:-1])
            tc_percent = np.where(swing_phase_data[peaks[0][0]:-1] == toe_clear_min)[0] / len(swing_phase_data)
            tc_clear_hs = max(swing_phase_data[mid_swing_index:-1])
            toe_clearance.loc[cycle_number][s_mtc_label] = toe_clear_min
            toe_clearance.loc[cycle_number][s_mtc_cycle_label] = tc_percent
            toe_clearance.loc[cycle_number][s_tc_hs_label] = tc_clear_hs
        return toe_clearance


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
