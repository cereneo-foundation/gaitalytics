from unittest import TestCase
from pyCGM2.Tools import btkTools


class TestC3dFileWrapper(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"

    def test_get_events(self):
        file = btkTools.smartReader(self.path)


