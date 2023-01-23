import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Events import eventProcedures, eventFilters
from gait_analysis.models import HBMToCGM2Mapper


class TestHBMToCGM2Mapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls._NAME_MAPPINGS = ("RASI",
                              "LASI",
                              "RPSI",
                              "LPSI",
                              "LTHI",
                              "LKNE",
                              "LKNM",
                              "LTIB",
                              "LANK",
                              "LMED",
                              "LFMH",  # TODO: not same
                              "LVMH",
                              "LHEE",
                              "LTOE",
                              "RTHI",
                              "RKNE",
                              "RKNM",
                              "RTIB",
                              "RANK",
                              "RMED",
                              "RFMH",  # TODO: not same
                              "RVMH",
                              "RHEE",
                              "RTOE",
                              "CLAV",
                              "T2") # TODO: not same

    def test_good_case(self):
        acq = btkTools.smartReader(self.path)
        mapper = HBMToCGM2Mapper()
        mapper.map_to_cgm2(acq)
        for marker_name in self._NAME_MAPPINGS:
            try:
                acq.GetPoint(marker_name)
            except RuntimeError:
                self.assertTrue(False, f"{marker_name} not found")



if __name__ == '__main__':
    unittest.main()
