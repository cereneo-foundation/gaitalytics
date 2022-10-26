import unittest
from os import getcwd
from pathlib import Path

from motion_capture import file_parser


class TestParseC3DFile(unittest.TestCase):
    testFilePath = Path(getcwd(), "test/data/test.c3d")

    def test_load_file(self):
        parser = file_parser.C3dFileParser(self.testFilePath)
        test = parser.get_data()
        size_lasis_x = len(test.point_data['LASIS']['x'])
        size_force = len(test.emg_data['Force.Fx1'])

        self.assertTrue(test.c3d_data, "Empty Point")


if __name__ == '__main__':
    unittest.main()
