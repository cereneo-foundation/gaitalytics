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

    @staticmethod
    @abc.abstractmethod
    def get_translator() -> dict:
        pass


class HBMToCGM2Mapper(AbstractToCGM2Mapper):
    @staticmethod
    def get_translator() -> dict:
        return {"RASI": "RASIS",
                "LASI": "LASIS",
                "RPSI": "RPSIS",
                "LPSI": "LPSIS",
                "LTHI": "LLTHI",
                "LKNE": "LLEK",
                "LKNM": "LMEK",
                "LTIB": "LLSHA",
                "LANK": "LLM",
                "LMED": "LMM",
                "LFMH": "LMT2",  # TODO: not same
                "LVMH": "LMT5",
                "RTHI": "RLTHI",
                "RKNE": "RLEK",
                "RKNM": "RMEK",
                "RTIB": "RLSHA",
                "RANK": "RLM",
                "RMED": "RMM",
                "RFMH": "RMT2",  # TODO: not same
                "RVMH": "RMT5",
                "CLAV": "JN",
                "T2": "C7"}  # cf Armand et al.2013 https://doi.org/10.1016/j.gaitpost.2013.06.016}

    @classmethod
    def calculate_missing_markers(cls, acq: btkAcquisition):
        """ Maps hmb trunk model to cgm2
        Iterates through point names and maps hbm trunk to cgm2 names. Further calculates missing points from existing
        Args:
            acq: acquisition read from btk c3d
        """
        cls._calc_toe(acq, "L")
        cls._calc_toe(acq, "R")

    @classmethod
    def _calc_toe(cls, acq: btkAcquisition, side: str = "L"):
        """ creates LTOE or RTOE marker for cmg2.
        calculates the mean values for LHEE, LFMH and LVMH resp. RHEE, RFMH and RVMH.
        Args:
           acq: acquisition read from btk c3d
           site: Left ("L") or Right ("R") side.
       """
        hee = acq.GetPoint(f"{side}HEE")
        fmh = acq.GetPoint(f"{side}FMH")
        vmh = acq.GetPoint(f"{side}VMH")
        toe_values = mean([hee.GetValues(), fmh.GetValues(), vmh.GetValues()], axis=0)
        toe = btkPoint(f"{side}TOE", acq.GetPointFrameNumber())
        toe.SetValues(toe_values)
        acq.AppendPoint(toe)
