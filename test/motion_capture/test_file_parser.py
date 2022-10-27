import unittest
from os import getcwd
from pathlib import Path

from motion_capture import file_parser


class TestParseC3DFile(unittest.TestCase):
    testFilePath = Path(getcwd(), "test/data/test.c3d")

    def test_load_file(self):
        parser = file_parser.C3dFileParser(self.testFilePath)
        points = parser.points

        self.assertTrue(points, "Empty Point")


if __name__ == '__main__':
    unittest.main()
