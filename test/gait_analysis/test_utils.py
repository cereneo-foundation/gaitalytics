import unittest
from gait_analysis import utils


class TestWeightCalculation(unittest.TestCase):
    def test_weight(self):
        weight = utils.calculate_weight_from_force_plates_file("1min_static.c3d", "test/data/")
        self.assertEqual(84, round(weight))


class TestHeightCalculation(unittest.TestCase):
    def test_weight(self):
        weight = utils.calculate_height_from_markers_file("1min_static.c3d", "test/data/")
        self.assertEqual(round(weight), 84)

if __name__ == '__main__':
    unittest.main()
