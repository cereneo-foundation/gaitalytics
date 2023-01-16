from unittest import TestCase
from pyCGM2.Tools import btkTools


class TestC3dFileWrapper(TestCase):

    def test_get_events(self):
        file = btkTools.smartReader("./test/data/test.c3d")
        points = file.GetPoints()
        print(file)


