from abc import ABC, abstractmethod

import numpy as np
import scipy as sc
from matplotlib import pyplot as plt

import gaitalytics.utils
import gaitalytics.files


class BaseOutputModeller(ABC):

    def __init__(self, label: str, point_type: gaitalytics.utils.PointDataType):
        self._label = label
        self._type = point_type

    def create_point(self, file_handler: gaitalytics.files.FileHandler, **kwargs):
        result = self._calculate_point(file_handler, **kwargs)
        point = gaitalytics.utils.Point()
        point.type = self._type
        point.values = result
        point.label = self._label
        file_handler.add_point(point)

    @abstractmethod
    def _calculate_point(self, file_handler: gaitalytics.files.FileHandler, **kwargs) -> np.ndarray:
        pass


class COMModeller(BaseOutputModeller):

    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(configs.MARKER_MAPPING.com.value, gaitalytics.utils.PointDataType.Marker)
        self._configs = configs

    def _calculate_point(self, file_handler: gaitalytics.files.FileHandler, **kwargs):
        l_hip_b = file_handler.get_point(self._configs.MARKER_MAPPING.left_back_hip.value).values
        r_hip_b = file_handler.get_point(self._configs.MARKER_MAPPING.right_back_hip.value).values
        l_hip_f = file_handler.get_point(self._configs.MARKER_MAPPING.left_front_hip.value).values
        r_hip_f = file_handler.get_point(self._configs.MARKER_MAPPING.right_front_hip.value).values
        return (l_hip_b + r_hip_b + l_hip_f + r_hip_f) / 4


class XCOMModeller(BaseOutputModeller):
    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(configs.MARKER_MAPPING.xcom.value, gaitalytics.utils.PointDataType.Marker)
        self._configs = configs

    def _calculate_point(self, file_handler: gaitalytics.files.FileHandler, **kwargs):
        com = file_handler.get_point(self._configs.MARKER_MAPPING.com.value).values
        belt_speed = kwargs.get("belt_speed", 1)
        dominant_leg_length = kwargs.get("dominant_leg_length", 1)
        return self._calculate_xcom(belt_speed, com, dominant_leg_length)

    def _calculate_xcom(self, belt_speed: float, com: np.ndarray, dominant_leg_length: float):
        com_v = self._calculate_point_velocity(com)
        sos = sc.signal.butter(2, 5,'low', fs= 100, output='sos')
        com_v[:, 0] = sc.signal.sosfilt(sos, com_v[:, 0])
        com_v[:, 1] = sc.signal.sosfilt(sos, com_v[:, 1])
        com_v[:, 2] = sc.signal.sosfilt(sos, com_v[:, 2])
        # to meter
        dominant_leg_length = (dominant_leg_length / 1000)
        com = com / 1000

        # from mm/(s/100) to m/s
        com_v = com_v * 100 / 1000

        # due to minus is progression
        belt_speed = belt_speed * -1

        sqrt_leg_speed = np.sqrt(sc.constants.g / dominant_leg_length)
        com_x_v = com[:, 0] + (com_v[:, 0] / sqrt_leg_speed)
        # minus because progression axes is minus
        com_y_v = com[:, 1] + ((belt_speed + com_v[:, 1]) / sqrt_leg_speed)
        com_z_v = com[:, 2] + (com_v[:, 2] / sqrt_leg_speed)
        x_com = np.array([com_x_v, com_y_v, com_z_v]).T
        x_com = x_com * 1000

        return x_com

    # return com * 1000
    @staticmethod
    def _calculate_point_velocity(com: np.ndarray):
        com_v = np.diff(com, axis=0)
        com_v = np.insert(com_v, 0, 0, axis=0)
        for c in range(len(com_v[0])):
            com_v[0, c] = com_v[1, c]
        return com_v


class CMoSModeller(BaseOutputModeller):

    def __init__(self, configs: gaitalytics.utils.ConfigProvider, **kwargs):
        self._configs = configs
        super().__init__(configs.MARKER_MAPPING.cmos.value, gaitalytics.utils.PointDataType.Marker)

    def _calculate_point(self, file_handler: gaitalytics.files.FileHandler, **kwargs) -> np.ndarray:
        x_com = file_handler.get_point(self._configs.MARKER_MAPPING.xcom.value).values

        lat_malleoli_left = file_handler.get_point(self._configs.MARKER_MAPPING.left_lat_malleoli.value).values
        lat_malleoli_right = file_handler.get_point(self._configs.MARKER_MAPPING.right_lat_malleoli.value).values
        med_malleoli_left = file_handler.get_point(self._configs.MARKER_MAPPING.left_med_malleoli.value).values
        med_malleoli_right = file_handler.get_point(self._configs.MARKER_MAPPING.right_med_malleoli.value).values
        heel_left = file_handler.get_point(self._configs.MARKER_MAPPING.left_heel.value).values
        heel_right = file_handler.get_point(self._configs.MARKER_MAPPING.right_heel.value).values
        foot_left = file_handler.get_point(self._configs.MARKER_MAPPING.left_meta_2.value).values
        foot_right = file_handler.get_point(self._configs.MARKER_MAPPING.right_meta_2.value).values

        return self._calculate_cMoS(x_com,
                                    lat_malleoli_left,
                                    lat_malleoli_right,
                                    med_malleoli_left,
                                    med_malleoli_right,
                                    foot_left,
                                    foot_right,
                                    heel_left,
                                    heel_right,
                                    file_handler,
                                    **kwargs)

    def _calculate_cMoS(self,
                        x_com: np.ndarray,
                        lat_malleoli_left: np.ndarray,
                        lat_malleoli_right: np.ndarray,
                        med_malleoli_left: np.ndarray,
                        med_malleoli_right: np.ndarray,
                        foot_left: np.ndarray,
                        foot_right: np.ndarray,
                        heel_left: np.ndarray,
                        heel_right: np.ndarray,
                        file_handler: gaitalytics.files.FileHandler,
                        **kwargs) -> np.ndarray:
        def mos_non_event(x_com_v, frame_index, side):
            return [0, 0, 0]

        def mos_double_support(x_com_v, frame_index, side):
            x_com_frame = x_com_v[frame_index]
            left_boundary = lat_malleoli_left[frame_index, 0]
            right_boundary = lat_malleoli_right[frame_index, 0]
            if side == gaitalytics.utils.GaitEventContext.LEFT:
                front_boundary = foot_left[frame_index, 1]
                back_boundary = heel_right[frame_index, 1]
            else:
                front_boundary = foot_right[frame_index, 1]
                back_boundary = heel_left[frame_index, 1]

            ap = self._calculate_mos(x_com_frame[1], front_boundary, back_boundary)
            ml = self._calculate_mos(x_com_frame[0], right_boundary, left_boundary)

            return [ml, ap, 0]

        def mos_single_stance(x_com_v, frame_index, side):
            x_com_frame = x_com_v[frame_index]
            if side == gaitalytics.utils.GaitEventContext.LEFT:
                front_boundary = foot_right[frame_index, 1]
                back_boundary = heel_right[frame_index, 1]
                left_boundary = med_malleoli_right[frame_index, 0]
                right_boundary = lat_malleoli_right[frame_index, 0]
            else:
                front_boundary = foot_left[frame_index, 1]
                back_boundary = heel_left[frame_index, 1]
                left_boundary = lat_malleoli_left[frame_index, 0]
                right_boundary = med_malleoli_left[frame_index, 0]

            ap = self._calculate_mos(x_com_frame[1], front_boundary, back_boundary)
            ml = self._calculate_mos(x_com_frame[0], left_boundary, right_boundary)

            return [ml, ap, 0]

        show_plot = kwargs.get("show_plot", False)
        mos = np.zeros((len(x_com), 3))
        event_i = 0
        next_event = file_handler.get_event(event_i)
        current_context = None
        mos_function = mos_non_event
        for frame_i in range(len(x_com)):
            if frame_i == 1420:
                print(frame_i)

            if frame_i == next_event.frame:
                current_context = gaitalytics.utils.GaitEventContext(next_event.context)
                if next_event.label == gaitalytics.utils.GaitEventLabel.FOOT_STRIKE.value:
                    mos_function = mos_double_support
                else:
                    mos_function = mos_single_stance
                event_i += 1
                if event_i < file_handler.get_events_size():
                    next_event = file_handler.get_event(event_i)
            mos[frame_i] = mos_function(x_com, frame_i, current_context)
        mos = mos
        if show_plot:
            self._show(mos, x_com, file_handler)

        return mos

    @staticmethod
    def _calculate_mos(x_com, minus_boundary, plus_boundary):
        minus_diff = (minus_boundary - x_com) * -1
        plus_diff = plus_boundary - x_com
        return min([minus_diff, plus_diff])

    def _show(self, mos, x_com, file_handler):
        com = file_handler.get_point(self._configs.MARKER_MAPPING.com.value).values
        fig, axs = plt.subplots(2, 1, figsize=(8, 6))
        (ax1, ax2) = axs  # Unpack the subplots axes
        x_com = x_com
        from_frame = 1420
        to_frame = 1534

        plot_mosml = ax1.plot(mos[from_frame:to_frame, 0], color='blue', label='MOSml')
        ax1_2 = ax1.twinx()
        ax1_3 = ax1.twinx()
        plot_xcomml = ax1_2.plot(x_com[from_frame:to_frame, 0], color='green', label='xCOMml', linestyle='dashed')
        plot_comml = ax1_3.plot(com[from_frame:to_frame, 0], color='brown', label='COMml', linestyle='-.')
        ax1.set(xlabel="frame", ylabel="mos")
        ax1_2.set(ylabel="xcom")
        ax1_3.set(ylabel="com")
        ax1_3.spines["right"].set_position(("axes", 1.2))
        ax1.axhline(0, color="gray", linestyle=":")
        ax1.axvline(0, linestyle=":", color='gray')
        ax1.axvline(18, linestyle=":", color='gray')
        ax1.axvline(57, linestyle=":", color='gray')
        ax1.axvline(74, linestyle=":", color='gray')
        ax1.axvline(to_frame - from_frame-1, linestyle=":", color='gray')

        plot_mosap = ax2.plot(mos[from_frame:to_frame, 1], color='red', label='MOSap')
        ax2_2 = ax2.twinx()
        ax2_3 = ax2.twinx()
        plot_xcomap = ax2_2.plot(x_com[from_frame:to_frame, 1], color='green', label='xCOMap', linestyle='dashed')
        plot_comap = ax2_3.plot(com[from_frame:to_frame, 1], color='brown', label='COMap', linestyle='-.')

        ax2_3.spines["right"].set_position(("axes", 1.2))
        ax2.set(xlabel="frame", ylabel="mos")
        ax2_2.set(ylabel="xcom")
        ax2_3.set(ylabel="com")
        ax2.axvline(0, linestyle=":", color='gray')
        ax2.axhline(0, color="gray", linestyle=":")
        ax2.axvline(18, linestyle=":", color='gray')
        ax2.axvline(57, linestyle=":", color='gray')
        ax2.axvline(74, linestyle=":", color='gray')
        ax2.axvline(to_frame-from_frame-1, linestyle=":", color='gray')

        lns = plot_mosml + plot_xcomml + plot_comml + plot_mosap + plot_xcomap + plot_comap
        labels = [l.get_label() for l in lns]
        plt.legend(lns, labels, loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=6)
        # Adjust the spacing between subplots
        plt.tight_layout()
        plt.show()
