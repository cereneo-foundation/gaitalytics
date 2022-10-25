import unittest
from os import getcwd
from pathlib import Path

from motion_capture import file_handling_utils


class TestLoadFile(unittest.TestCase):
    testFilePath = Path(getcwd(), "test/data/test1.c3d")

    def test_load_file(self):
        file_handling_utils.load_file(self.testFilePath)
        self.assertTrue(True, "Nice!")


if __name__ == '__main__':
    unittest.main()
