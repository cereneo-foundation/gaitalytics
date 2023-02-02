import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_filtering


class TestZenisEvents(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])
        low_pass_filtering(self.acq)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.path = f"{cls.data_path}1min_modelled.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5_CEFIR.settings"

    def test_good_case(self):
        GaitEventDetectorFactory().get_zenis_detector().detect_events(self.acq)
        self.assertEqual(self.acq.GetEvents().GetItemNumber(), 218, "Zenis event detector does not work")
        #btkTools.smartWriter(self.acq, f"{self.data_path}1min_modelled_events.c3d")


class TestForcePlateEvents(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/1min_modelled.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5_CEFIR.settings"

    def test_good_case(self):
        GaitEventDetectorFactory().get_force_plate_detector().detect_events(self.acq)
        self.assertEqual(self.acq.GetEvents().GetItemNumber(), 216, "Force plate event detector does not work")


if __name__ == '__main__':
    unittest.main()
