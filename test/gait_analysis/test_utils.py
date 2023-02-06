import unittest
from gait_analysis import utils

class TestWeightCalculation(unittest.TestCase):
    def test_something(self):
        weight = utils.calculate_weight_from_part("1min_static.c3d", "test/data/")
        print(weight)


if __name__ == '__main__':
    unittest.main()
