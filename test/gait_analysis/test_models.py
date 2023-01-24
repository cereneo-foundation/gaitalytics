import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.models import HBMToCGM2Mapper


class TestHBMToCGM2Mapper(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "HBM_Trunk_cgm2.5.settings"

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
                              "LFMH",
                              "LVMH",
                              "LHEE",
                              "LTOE",
                              "RTHI",
                              "RKNE",
                              "RKNM",
                              "RTIB",
                              "RANK",
                              "RMED",
                              "RFMH",
                              "RVMH",
                              "RHEE",
                              "RTOE",
                              "CLAV")

    def test_good_case(self):
        HBMToCGM2Mapper().calculate_missing_markers(self.acq)
        for marker_name in self._NAME_MAPPINGS:
            try:
                self.acq.GetPoint(marker_name)
            except RuntimeError:
                self.assertTrue(False, f"{marker_name} not found")


if __name__ == '__main__':
    unittest.main()
