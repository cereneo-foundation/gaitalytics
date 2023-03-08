import abc

from btk import btkAcquisition, btkPoint
from numpy import mean
from gait_analysis.utils.c3d import SideEnum


class AbstractToCGM2Mapper(abc.ABC):
    """
    Abstract clas do define different biomechanical model mappers
    """

    @classmethod
    @abc.abstractmethod
    def calculate_missing_markers(cls, acq: btkAcquisition):
        pass


class HBMToCGM2Mapper(AbstractToCGM2Mapper):

    @classmethod
    def calculate_missing_markers(cls, acq: btkAcquisition):
        """Maps hmb trunk model to cgm2
        Iterates through point names and maps hbm trunk to cgm2 names. Further calculates missing points from existing
        :param acq: loaded acquisition
        """
        cls._calc_toe(acq, SideEnum.LEFT)
        cls._calc_toe(acq, SideEnum.RIGHT)

    @classmethod
    def _calc_toe(cls, acq: btkAcquisition, side: SideEnum = SideEnum.LEFT):
        """creates LTOE or RTOE marker for cmg2.
        calculates the mean values for LHEE, LFMH and LVMH resp. RHEE, RFMH and RVMH.

        :param acq: loaded acquisition
        :param side: Left ("L") or Right ("R") side.
        """

        hee = acq.GetPoint(f"{side.value}HEE")
        fmh = acq.GetPoint(f"{side.value}FMH")
        vmh = acq.GetPoint(f"{side.value}VMH")
        toe_values = mean([hee.GetValues(), fmh.GetValues(), vmh.GetValues()], axis=0)
        toe = btkPoint(f"{side.value}TOE", acq.GetPointFrameNumber())
        toe.SetValues(toe_values)
        acq.AppendPoint(toe)
