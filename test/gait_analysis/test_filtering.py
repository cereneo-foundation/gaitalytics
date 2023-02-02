import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_filtering


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
        low_pass_filtering(self.acq)
        #btkTools.smartWriter(self.acq, f"{self.data_path}1min_filtered.c3d")




if __name__ == '__main__':
    unittest.main()
