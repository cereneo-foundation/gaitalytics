from btk import btkAcquisition
from pyCGM2.Tools import btkTools
import numpy as np
from gait_analysis.utils import SideEnum

C3D_METADATA_PROCESSING_LABEL = "PROCESSING"
C3D_METADATA_PROCESSING_BODYMASS_LABEL = "Bodymass"
C3D_METADATA_PROCESSING_HEIGHT_LABEL = "Height"
C3D_METADATA_PROCESSING_LEG_LENGTH_LABEL = "LegLength"
C3D_METADATA_PROCESSING_KNEE_WIDTH_LABEL = "KneeWidth"
C3D_METADATA_PROCESSING_ANKLE_WIDTH_LABEL = "AnkleWidth"


class AnthropomorphicCalculator:

    def __init__(self, acq_static: btkAcquisition):
        """
        Calculates anthropomorphic metrics (Body height, body weight, leg length, knee width, ankle width)
        from given calibration acquisition
        :param acq_static: calibration acquisition
        """
        self._metrics = {C3D_METADATA_PROCESSING_BODYMASS_LABEL: 0,
                         C3D_METADATA_PROCESSING_HEIGHT_LABEL: 0,
                         f"{SideEnum.LEFT.value}{C3D_METADATA_PROCESSING_LEG_LENGTH_LABEL}": 0,
                         f"{SideEnum.RIGHT.value}{C3D_METADATA_PROCESSING_LEG_LENGTH_LABEL}": 0,
                         f"{SideEnum.LEFT.value}{C3D_METADATA_PROCESSING_KNEE_WIDTH_LABEL}": 0,
                         f"{SideEnum.RIGHT.value}{C3D_METADATA_PROCESSING_KNEE_WIDTH_LABEL}": 0,
                         f"{SideEnum.LEFT.value}{C3D_METADATA_PROCESSING_ANKLE_WIDTH_LABEL}": 0,
                         f"{SideEnum.RIGHT.value}{C3D_METADATA_PROCESSING_ANKLE_WIDTH_LABEL}": 0}

        self._calculate_height(acq_static)
        self._calculate_weight(acq_static)
        self._calculate_leg_length(acq_static, SideEnum.LEFT)
        self._calculate_leg_length(acq_static, SideEnum.RIGHT)

    def store_in_acquisition(self, acq: btkAcquisition):
        """
        stores calculated anthropomorphic metric into given acquisition
        :param acq: acquisition to store in
        """
        for label in self._metrics:
            btkTools.smartSetMetadata(acq,
                                      C3D_METADATA_PROCESSING_LABEL,
                                      label,
                                      0,
                                      self._metrics[label])

    def _calculate_height(self, acq_static: btkAcquisition) -> None:
        """
        Calculates the body height of a subject with head or c7 marker
        :param acq_static: calibration c3d file
        """
        try:
            self._metrics[C3D_METADATA_PROCESSING_HEIGHT_LABEL] = int(
                round(np.mean(acq_static.GetPoint("GLAB").GetValues()[:, 2])) * 1.005)
            # TODO need a nice factor to determine height from forehead
        except RuntimeError:
            # I no GLAB use t2
            self._metrics[C3D_METADATA_PROCESSING_HEIGHT_LABEL] = int(
                round(np.mean(acq_static.GetPoint("T2").GetValues()[:, 2])) * 1.05)
            # TODO need a nice factor to determine height from forehead

    def _calculate_weight(self, acq_static: btkAcquisition):
        """
        Calculates weights from force plates
        :param acq_static: calibration c3d file
        """
        wl = np.mean(acq_static.GetAnalogs().GetItem(2).GetValues())
        wr = np.mean(acq_static.GetAnalogs().GetItem(8).GetValues())
        self._metrics[C3D_METADATA_PROCESSING_BODYMASS_LABEL] = np.abs((wl + wr) / 9.81)

    def _calculate_leg_length(self, acq_static: btkAcquisition, side: SideEnum = SideEnum.LEFT):
        """
        Calculates leg length from leg markers
        :param acq_static: calibration c3d file
        :param side: side to calculate
        """
        upper_leg_length = self._calculate_point_distance(acq_static, f"{side.value}ASI", f"{side.value}KNE")
        lower_leg_length = self._calculate_point_distance(acq_static, f"{side.value}KNE", f"{side.value}ANK")
        self._metrics[f"{side.value}{C3D_METADATA_PROCESSING_LEG_LENGTH_LABEL}"] = abs(
            upper_leg_length + lower_leg_length)

    def _calculate_knee_width(self, acq_static: btkAcquisition, side: SideEnum = SideEnum.LEFT):
        """
        Calculates knee width from markers depending on side
        :param acq_static: calibration c3d file
        :param side: side to calculate
        """
        knee_width = self._calculate_point_distance(acq_static, f"{side.value}KNE", f"{SideEnum.value}KNM")
        self._metrics[f"{side.value}{C3D_METADATA_PROCESSING_KNEE_WIDTH_LABEL}"] = abs(knee_width)

    def _calculate_ankle_width(self, acq_static: btkAcquisition, side: SideEnum = SideEnum.LEFT):
        """
        Calculates ankle width from markers depending on side
        :param acq_static: calibration c3d file
        :param side: side to calculate
        """
        ankle_width = self._calculate_point_distance(acq_static, f"{side.value}ANK", f"{SideEnum.value}MED")
        self._metrics[f"{side.value}{C3D_METADATA_PROCESSING_ANKLE_WIDTH_LABEL}"] = abs(ankle_width)

    @staticmethod
    def _calculate_point_distance(acq_static: btkAcquisition, point_a_label, point_b_label) -> float:
        """
       Calculates distance between two markers
       :param acq_static: calibration c3d file
       :param point_a_label: label of first point
       :param point_b_label: label of second point
       """
        point_a_vector = np.mean(acq_static.GetPoint(point_a_label).GetValues(), 0)
        point_b_vector = np.mean(acq_static.GetPoint(point_b_label).GetValues(), 0)
        translational_vector = point_a_vector - point_b_vector
        distance = np.sqrt(translational_vector[0] ** 2 + translational_vector[1] ** 2 + translational_vector[2] ** 2)
        return distance
