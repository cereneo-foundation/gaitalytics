import abc

from pandas import DataFrame
from btk import btkAcquisition


class AbstractToCGM2Mapper(abc.ABC):
    """
    Abstract clas do define different biomechanical model mappers
    """
    @abc.abstractmethod
    def map_to_cgm2(self, points: btkAcquisition) -> btkAcquisition:
        pass

    @staticmethod
    def _map_marker_names(marker_name_from: str, name_mappings: tuple) -> str:
        """
        Loops through tuples of marker name mappings and returns cgm2 marker name
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

    def map_to_cgm2(self, acq: btkAcquisition) -> btkAcquisition:
        """
        Iterates through point names and maps hbm trunk to cgm2 names. Further calculates missing points from existing
        """
        # map names
        for i in range(0, acq.GetPointNumber()):
            point = acq.GetPoint(i)
            from_marker_name = point.GetLabel()
            cmg2_marker_name = self._map_marker_names(from_marker_name, self._NAME_MAPPINGS)
            if cmg2_marker_name:
                point.SetLabel(cmg2_marker_name)

        # TODO: calc missing markers
        self._calc_ltoe(acq, "L")
        return acq

    def _calc_ltoe(self, acq: btkAcquisition, side: str = "L") -> btkAcquisition:
        hee = acq.GetPoint(f"{side}HEE")
        fmh = acq.GetPoint(f"{side}FMH")
        vmh = acq.GetPoint(f"{side}VMH")
        return acq

