import abc

from pandas import DataFrame


class AbstractToCGM2Mapper(abc.ABC):
    @abc.abstractmethod
    def map_to_cgm2(self, points: DataFrame) -> DataFrame:
        pass

    @staticmethod
    def static_map_marker_names(marker_name_from: str, name_mappings: tuple) -> str:
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
                               ("LLHTI", "LHTI"),
                               ("LLEK", "LKNE"),
                               ("LMEK", "LKNM"),
                               ("LLSHA", "LTIB"),
                               ("LLM", "LANK"),
                               ("LMM", "LMED"),
                               ("LMT2", "LFMH"),  # TODO: not same
                               ("LMT5", "LVMH"),
                               ("RLHTI", "RHTI"),
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

    def map_to_cgm2(self, points: DataFrame) -> DataFrame:
        # map names
        from_marker_names = points.columns
        for i in range(0, len(from_marker_names)):
            cmg2_marker_name = self.static_map_marker_names(from_marker_names[i], self._NAME_MAPPINGS)
            if cmg2_marker_name:
                points.rename(columns={from_marker_names[i]: cmg2_marker_name}, inplace=True)
        # TODO: calc missing markers

        return points
