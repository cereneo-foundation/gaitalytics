import unittest

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering


class TestFiltering(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(f"{self.data_path}{self.test_file_name}", settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.test_file_name = "1min.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5_CEFIR.settings"

    def test_good_case(self):
        low_pass_point_filtering(self.acq)
        low_pass_force_plate_filtering(self.acq)


if __name__ == '__main__':
    unittest.main()
