import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.events import GaitEventDetectorFactory


class TestZenisEvents(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])
        HBMToCGM2Mapper().calculate_missing_markers(self.acq)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "HBM_Trunk.settings"

    def test_good_case(self):
        GaitEventDetectorFactory().get_zenis_detector().detect_events(self.acq)
        self.assertEqual(self.acq.GetEvents().GetItemNumber(), 622, "Zenis event detector does not work")


class TestForcePlateEvents(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])
        HBMToCGM2Mapper().calculate_missing_markers(self.acq)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls.path = "test/data/test.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "HBM_Trunk.settings"

    def test_good_case(self):
        GaitEventDetectorFactory().get_force_plate_detector().detect_events(self.acq)
        self.assertEqual(self.acq.GetEvents().GetItemNumber(), 622, "Force plate event detector does not work")


if __name__ == '__main__':
    unittest.main()
