import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Events import eventProcedures, eventFilters
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.events import GaitEventDetectorFactory


class TestZenisEvents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = r"../data/test.c3d"

    def test_good_case(self):
        mapper = HBMToCGM2Mapper()
        acq = btkTools.smartReader(self.path, mapper.get_translator())
        btkTools.smartWriter(acq, r"../data/markers.c3d")
        mapper.calculate_missing_markers(acq)
        GaitEventDetectorFactory().get_zenis_detector().detect_events(acq)
        self.assertEqual(acq.GetEvents().GetItemNumber(), 622, "Zenis event detector does not work")


class TestForcePlateEvents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = r"../data/test.c3d"

    def test_good_case(self):
        acq = btkTools.smartReader(self.path)
        GaitEventDetectorFactory().get_force_plate_detector().detect_events(acq)
        btkTools.smartWriter(acq, r"../data/out.c3d")
        self.assertEqual(acq.GetEvents().GetItemNumber(), 2, "ForcePlate event detector does not work")


if __name__ == '__main__':
    unittest.main()
