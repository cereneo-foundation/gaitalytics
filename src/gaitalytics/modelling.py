from abc import ABC, abstractmethod

import numpy as np
from btk import btkAcquisition, btkPoint
from matplotlib import pyplot as plt

import gaitalytics.utils


class BaseOutputModeller(ABC):

    def __init__(self, label: str, point_type: gaitalytics.utils.PointDataType):
        self._label = label
        self._type = point_type

    def create_point(self, acq: btkAcquisition):
        result = self._calculate_point(acq)
        point = btkPoint(self._type.value)
        point.SetValues(result)
        point.SetLabel(self._label)
        acq.AppendPoint(point)

    @abstractmethod
    def _calculate_point(self, acq: btkAcquisition) -> np.ndarray:
        pass


class COMModeller(BaseOutputModeller):

    def __init__(self, configs: gaitalytics.utils.ConfigProvider):
        super().__init__(configs.MARKER_MAPPING.com.value, gaitalytics.utils.PointDataType.Scalar)
        self._configs = configs

    def _calculate_point(self, acq: btkAcquisition):
        l_hip_b = acq.GetPoint(self._configs.MARKER_MAPPING.left_back_hip.value).GetValues()
        r_hip_b = acq.GetPoint(self._configs.MARKER_MAPPING.right_back_hip.value).GetValues()
        l_hip_f = acq.GetPoint(self._configs.MARKER_MAPPING.left_front_hip.value).GetValues()
        r_hip_f = acq.GetPoint(self._configs.MARKER_MAPPING.right_front_hip.value).GetValues()
        return (l_hip_b + r_hip_b + l_hip_f + r_hip_f) / 4


class CMoSModeller(BaseOutputModeller):

    def __init__(self, side: gaitalytics.utils.GaitEventContext, configs: gaitalytics.utils.ConfigProvider,
                 dominant_leg_length: float, belt_speed: float):
        self._configs = configs
        self._dominant_leg_length = dominant_leg_length
        self._belt_speed = belt_speed
        self._side = side
        if side == gaitalytics.utils.GaitEventContext.LEFT:
            label = self._configs.MARKER_MAPPING.left_cmos.value
        else:
            label = self._configs.MARKER_MAPPING.right_cmos.value
        super().__init__(label, gaitalytics.utils.PointDataType.Marker)

    def _calculate_point(self, acq: btkAcquisition) -> np.ndarray:
        com = acq.GetPoint(self._configs.MARKER_MAPPING.com.value).GetValues()
        if self._side == gaitalytics.utils.GaitEventContext.LEFT:
            lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.left_lat_malleoli.value).GetValues()
            contra_lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.right_lat_malleoli.value).GetValues()
            meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.left_meta_2.value).GetValues()
            contra_meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.right_meta_2.value).GetValues()
        else:
            lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.right_lat_malleoli.value).GetValues()
            contra_lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.left_lat_malleoli.value).GetValues()
            meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.right_meta_2.value).GetValues()
            contra_meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.left_meta_2.value).GetValues()
        return self.cMoS(com, lat_malleoli, contra_lat_malleoli, meta_2, contra_meta_2, self._dominant_leg_length,
                         self._belt_speed, acq, self._side)

    def cMoS(self, com: np.ndarray,
             lat_malleoli_marker: np.ndarray,
             lat_malleoli_marker_contra: np.ndarray,
             second_meta_head_marker: np.ndarray,
             second_meta_head_marker_contra: np.ndarray,
             dominant_leg_length: float,
             belt_speed: float,
             acq: btkAcquisition,
             side: gaitalytics.utils.GaitEventContext,
             show: bool = True) -> np.ndarray:
        # AP axis is inverted
        com[:, 1] *= -1
        second_meta_head_marker[:, 1] *= -1
        second_meta_head_marker_contra[:, 1] *= -1

        if side == gaitalytics.utils.GaitEventContext.LEFT:
            contra_side = gaitalytics.utils.GaitEventContext.RIGHT
        else:
            contra_side = gaitalytics.utils.GaitEventContext.LEFT
        distance_from_x_com_to_bos = np.zeros((len(com), 3))

        # preparing events for the MOS calculation
        events_labels = []
        events_frames = []
        events_foot = []
        for k in range(acq.GetEventNumber()):
            event = acq.GetEvent(k)
            events_labels.append(event.GetLabel())
            events_frames.append(event.GetFrame())
            events_foot.append(event.GetContext())

        mos = []
        itr = 0
        cycle_event = None
        com_v = calculate_point_velocity(com)
        x_com = calculate_xcom(belt_speed, com, com_v, dominant_leg_length)
        # data route
        for i in range(0, len(com)):
            if itr < acq.GetEventNumber():
                if events_frames[itr] == i:
                    type_of_event = events_labels[itr]
                    foot = events_foot[itr]
                    cycle_event = f"{foot} {type_of_event}"
                    # determining the event to know the base of support we have to use for the calculation
                    itr += 1
            else:
                break

            # still miss the treadmill speed (need velocity of belt in AP and ML axis too)
            # x_com = [COM[i, 0], COM[i, 1]]
            # calculating the distance between the x_com and the BOS
            # 4 cases : Left Heel Strike, Left Toe Off, Right Heel Strike, Right Toe Off
            """
                        MOSant
                            ^
                            |
                MOSlat <-- COM --> MOSmed       (for left foot ahead, invert lat and med otherwise)
                            |
                        MOSpost

            """
            ## AP
            if cycle_event == f"{contra_side.value} Foot Off":
                mos = [x_com[i, 0] - lat_malleoli_marker[i, 0],
                       second_meta_head_marker[i, 1] - x_com[i, 1]]
            elif cycle_event == f"{side.value} Foot Off":
                mos = [lat_malleoli_marker_contra[i, 0] - x_com[i, 0],
                       second_meta_head_marker_contra[i, 1] - x_com[i, 1]]
            elif cycle_event == f"{side.value} Foot Strike":
                mos = [x_com[i, 0] - lat_malleoli_marker[i, 0],
                       second_meta_head_marker[i, 1] - x_com[i, 1]]
            elif cycle_event == f"{contra_side.value} Foot Strike":
                mos = [lat_malleoli_marker_contra[i, 0] - x_com[i, 0],
                       second_meta_head_marker_contra[i, 1] - x_com[i, 1]]
            else:
                mos = [0, 0]

            if side == gaitalytics.utils.GaitEventContext.LEFT:
                mos[0] = mos[0] * -1

            distance_from_x_com_to_bos[i, 0] = mos[0]
            distance_from_x_com_to_bos[i, 1] = mos[1]
        if show:
            self._show(distance_from_x_com_to_bos, side.value)
        return distance_from_x_com_to_bos

    def _show(self, distance_from_xCOM_to_BOS, side):
        # if show==True:
        # fig, ax1 = plt.subplots()
        freq = 100
        index_minute = 60 * freq
        time = np.arange(0, len(distance_from_xCOM_to_BOS) / freq, 1 / freq)
        fig, axs = plt.subplots(1, 2, figsize=(8, 6))
        fig.suptitle(side)
        (ax1, ax2) = axs  # Unpack the subplots axes

        ax1.plot(time[0:index_minute], distance_from_xCOM_to_BOS[0:index_minute, 0], color='orange', label='MOSlat')
        ax1.plot(time[index_minute:], distance_from_xCOM_to_BOS[index_minute:, 0], color='green', label='MOSlat>1min')

        ax2.plot(time[0:index_minute], distance_from_xCOM_to_BOS[0:index_minute, 1], color='orange', label='MOSap')
        ax2.plot(time[index_minute:], distance_from_xCOM_to_BOS[index_minute:, 1], color='green', label='MOSap>1min')

        ax1.legend()
        ax2.legend()
        # Adjust the spacing between subplots
        plt.tight_layout()
        plt.show()


def calculate_point_velocity(com: np.ndarray):
    com_v = np.diff(com, axis=0)
    com_v = np.insert(com_v, 0, 0, axis=0)
    for c in range(len(com_v[0])):
        com_v[0, c] = com_v[1, c]
    return com_v


def calculate_xcom(belt_speed: float, com: np.ndarray, com_v: np.ndarray, dominant_leg_length: float):
    sqrt_leg_speed = np.sqrt(9.81 / dominant_leg_length)
    com_x_v = com[:, 0] + (com_v[:, 0] / sqrt_leg_speed)
    com_y_v = com[:, 1] + (belt_speed + com_v[:, 1]) / sqrt_leg_speed
    com_z_v = com[:, 2] + (com_v[:, 2] / sqrt_leg_speed)
    x_com = np.array([com_x_v, com_y_v, com_z_v]).T
    # calculating the x_com

    return x_com
