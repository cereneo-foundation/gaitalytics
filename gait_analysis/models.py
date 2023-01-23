import abc

from pandas import DataFrame
from btk import btkAcquisition, btkPoint
from numpy import mean


class AbstractToCGM2Mapper(abc.ABC):
    """
    Abstract clas do define different biomechanical model mappers
    """

    @abc.abstractmethod
    def map_to_cgm2(self, acq: btkAcquisition):
        pass

    @staticmethod
    def _map_marker_names(marker_name_from: str, name_mappings: tuple) -> str:
        """ Maps marker names
        Loops through tuples of marker name mappings and returns cgm2 marker name
        Args:
            acq: acquisition read from btk c3d
        """
        for mapping in name_mappings:
            if mapping[0] == marker_name_from:
                return mapping[1]
        return ""


class HBMToCGM2Mapper(AbstractToCGM2Mapper):
    def __init__(self):
        self._NAME_MAPPINGS = (("RASIS", "RASI"),
                               ("LASIS", "LASI"),
                               ("RPSIS", "RPSI"),
                               ("LPSIS", "LPSI"),
                               ("LLTHI", "LTHI"),
                               ("LLEK", "LKNE"),
                               ("LMEK", "LKNM"),
                               ("LLSHA", "LTIB"),
                               ("LLM", "LANK"),
                               ("LMM", "LMED"),
                               ("LMT2", "LFMH"),  # TODO: not same
                               ("LMT5", "LVMH"),
                               ("RLTHI", "RTHI"),
                               ("RLEK", "RKNE"),
                               ("RMEK", "RKNM"),
                               ("RLSHA", "RTIB"),
                               ("RLM", "RANK"),
                               ("RMM", "RMED"),
                               ("RMT2", "RFMH"),  # TODO: not same
                               ("RMT5", "RVMH"),
                               ("JN", "CLAV"),
                               ("C7", "T2")  # TODO: not same
                               )

    def map_to_cgm2(self, acq: btkAcquisition):
        """ Maps hmb trunk model to cgm2
        Iterates through point names and maps hbm trunk to cgm2 names. Further calculates missing points from existing
        Args:
            acq: acquisition read from btk c3d
        """
        # map names
        for i in range(0, acq.GetPointNumber()):
            point = acq.GetPoint(i)
            from_marker_name = point.GetLabel()
            cmg2_marker_name = self._map_marker_names(from_marker_name, self._NAME_MAPPINGS)
            if cmg2_marker_name:
                point.SetLabel(cmg2_marker_name)

        self._calc_toe(acq, "L")
        self._calc_toe(acq, "R")

    def _calc_toe(self, acq: btkAcquisition, side: str = "L"):
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
