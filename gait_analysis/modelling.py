from abc import ABC, abstractmethod

import numpy as np
from btk import btkAcquisition, btkPoint

from . import c3d, utils


class BaseOutputModeller(ABC):

    def __init__(self, label: str, point_type: c3d.PointDataType):
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

    def __init__(self, configs: utils.ConfigProvider):
        super().__init__(configs.MARKER_MAPPING.com.value, c3d.PointDataType.Scalar)
        self._configs = configs

    def _calculate_point(self, acq: btkAcquisition):
        l_hip_b = acq.GetPoint(self._configs.MARKER_MAPPING.left_back_hip.value).GetValues()
        r_hip_b = acq.GetPoint(self._configs.MARKER_MAPPING.right_back_hip.value).GetValues()
        l_hip_f = acq.GetPoint(self._configs.MARKER_MAPPING.left_front_hip.value).GetValues()
        r_hip_f = acq.GetPoint(self._configs.MARKER_MAPPING.right_front_hip.value).GetValues()
        return (l_hip_b + r_hip_b + l_hip_f + r_hip_f) / 4


class MLcMoSModeller(BaseOutputModeller):

    def __init__(self, configs: utils.ConfigProvider, dominant_leg_length: float, belt_speed: float):
        self._configs = configs
        self._dominant_leg_length = dominant_leg_length
        self._belt_speed = belt_speed
        super().__init__("MLcMoS", c3d.PointDataType.Scalar)

    def _calculate_point(self, acq: btkAcquisition) -> np.ndarray:
        freq = acq.GetPointFrequency()
        com = acq.GetPoint(self._configs.MARKER_MAPPING.com.value).GetValues()
        l_grf = acq.GetPoint(self._configs.MODEL_MAPPING.left_GRF.value).GetValues()
        r_grf = acq.GetPoint(self._configs.MODEL_MAPPING.right_GRF.value).GetValues()
        l_lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.left_lateral_malleoli.value).GetValues()
        r_lat_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.right_lateral_malleoli.value).GetValues()
        l_med_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.left_medial_malleoli.value).GetValues()
        r_med_malleoli = acq.GetPoint(self._configs.MARKER_MAPPING.right_medial_malleoli.value).GetValues()
        l_meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.left_meta_2.value).GetValues()
        r_meta_2 = acq.GetPoint(self._configs.MARKER_MAPPING.right_meta_2.value).GetValues()
        l_meta_5 = acq.GetPoint(self._configs.MARKER_MAPPING.left_meta_5.value).GetValues()
        r_meta_5 = acq.GetPoint(self._configs.MARKER_MAPPING.right_meta_5.value).GetValues()
        l_heel = acq.GetPoint(self._configs.MARKER_MAPPING.left_heel.value).GetValues()
        r_heel = acq.GetPoint(self._configs.MARKER_MAPPING.right_heel.value).GetValues()
        return self.ML_cMoS(com, freq, r_grf, l_grf, freq, r_lat_malleoli, l_lat_malleoli, r_med_malleoli,
                            l_med_malleoli,
                            r_meta_2, l_meta_2, r_meta_5, l_meta_5, r_heel, l_heel, freq, self._dominant_leg_length,
                            self._belt_speed)

    def ML_cMoS(self, COM, COM_freq, vGRF_Right, vGRF_Left, vGRF_freq, Lat_Malleoli_Marker_Right,
                Lat_Malleoli_Marker_Left,
                Med_Malleoli_Marker_Right, Med_Malleoli_Marker_Left, Second_Meta_Head_Marker_Right,
                Second_Meta_Head_Marker_Left, Fifth_Meta_Head_Marker_Right, Fifth_Meta_Head_Marker_Left,
                Heel_Marker_Right, Heel_Marker_Left, Marker_freq, dominant_leg_length, belt_speed,
                show=False) -> np.ndarray:
        # TODO Adam: Do your magic
        """MLcMoS estimation.

        This function estimates and plot the continuous mediolateral margin of stability from processed (i.e., reconstructed, filled, filtered, ...)
        COM, vGRF and markers time series data. The cMoS is defined as the continuous distance between the boundary of the base of support and the
        extrapolated position of the body COM.

        Parameters (input)
        ----------
        COM                                     : 3D array_like
                                                processed center of mass [anteroposterior, mediolateral,  vertical] displacement time series [m]
        COM_freq                                : float (constant)
                                                sampling frequency of COM [Hz] (usually the same as Marker_freq)
        vGRF_Right                              : 1D array_like
                                                processed right vertical ground reaction forces time series [N] (needed only to segment the gait cycle)
        vGRF_Left                               : 1D array_like
                                                processed left vertical ground reaction forces time series [N] (needed only to segment the gait cycle)
        vGRF_freq                               : float (constant)
                                                sampling frequency of vGRF_Right and vGRF_Left [Hz]
        Lat_Malleoli_Marker_Right               : 3D array_like
                                                processed right lateral malleoli marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Lat_Malleoli_Marker_Left                : 3D array_like
                                                processed left lateral malleoli marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Med_Malleoli_Marker_Right               : 3D array_like
                                                processed right medial malleoli marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Med_Malleoli_Marker_Left                : 3D array_like
                                                processed left medial malleoli marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Second_Meta_Head_Marker_Right           : 3D array_like
                                                processed right second metatarsal head marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Second_Meta_Head_Marker_Left            : 3D array_like
                                                processed left second metatarsal head marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Fifth_Meta_Head_Marker_Right            : 3D array_like
                                                processed right fifth metatarsal head marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Fifth_Meta_Head_Marker_Left             : 3D array_like
                                                processed left fifth metatarsal head marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Heel_Marker_Right                       : 3D array_like
                                                processed right heel marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Heel_Marker_Left                        : 3D array_like
                                                processed left heel marker [anteroposterior, mediolateral,  vertical] displacement time series [m] (used to calculate the BOS perimeter)
        Marker_freq                             : float (constant)
                                                sampling frequency of Lat_Malleoli_Marker_Right, Lat_Malleoli_Marker_Left, Med_Malleoli_Marker_Right, Med_Malleoli_Marker_Left,
                                                Second_Meta_Head_Marker_Right, Second_Meta_Head_Marker_Left, Fifth_Meta_Head_Marker_Right, Fifth_Meta_Head_Marker_Left, Heel_Marker_Right, and Heel_Marker_Left [Hz]
        dominant_leg_lenth                      : float (constant)
                                                length of the dominant leg [m] (used to calculate the pendulum length, cf. supitz et al. 2013)
        belt_speed                              : float (constant)
                                                velocity of the treadmill belt [m/s] (used to calculate the extrapolated position of the COM, cf. supitz et al. 2013)
        show                                    : bool, optional (default = False)
                                                True (1) plots data and results in a plotly interactive figures
                                                False (0) to not plot

        Returns (output)
        -------
        cMOS                                    : float
                 mean mediolateral continuous margin of stability [m]
        """
        return np.ndarray([])
