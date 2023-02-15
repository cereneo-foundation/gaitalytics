import unittest

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis import utils


class TestWeightCalculation(unittest.TestCase):
    def test_weight(self):
        weight = utils.calculate_weight_from_force_plates_file("1min_static.c3d", "test/data/")
        self.assertEqual(84, round(weight))


class TestHeightCalculation(unittest.TestCase):
    def test_weight(self):
        weight = utils.calculate_height_from_markers_file("1min_static.c3d", "test/data/")
        self.assertEqual(1588, round(weight))


class TestTreadmillSpeedCalculation(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.test_acq = btkTools.smartReader(f"{self.data_path}{self.test_file}", self.settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.test_file = "1min_filtered_modelled_events.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5-pyCGM2.settings"

    def test_speed(self):
        speed = utils.calculate_treadmill_speed(self.test_acq)
        print(speed)


if __name__ == '__main__':
    unittest.main()
