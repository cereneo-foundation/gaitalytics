import abc

from pandas import DataFrame
from btk import btkAcquisition, btkPoint
from numpy import mean


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
        cls._calc_toe(acq, "L")
        cls._calc_toe(acq, "R")

    @classmethod
    def _calc_toe(cls, acq: btkAcquisition, side: str = "L"):
        """creates LTOE or RTOE marker for cmg2.
        calculates the mean values for LHEE, LFMH and LVMH resp. RHEE, RFMH and RVMH.

        :param acq: loaded acquisition
        :param side: Left ("L") or Right ("R") side.
        """

        hee = acq.GetPoint(f"{side}HEE")
        fmh = acq.GetPoint(f"{side}FMH")
        vmh = acq.GetPoint(f"{side}VMH")
        toe_values = mean([hee.GetValues(), fmh.GetValues(), vmh.GetValues()], axis=0)
        toe = btkPoint(f"{side}TOE", acq.GetPointFrameNumber())
        toe.SetValues(toe_values)
        acq.AppendPoint(toe)
