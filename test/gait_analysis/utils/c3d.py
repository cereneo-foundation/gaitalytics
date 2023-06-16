import os
import unittest

from gait_analysis.utils import c3d
from gait_analysis.utils.c3d import GaitEventContext

DATA_PATH = "./test/data"
TEST_INPUT_FILE_NAME = "Baseline.3.c3d"
TEST_OUTPUT_FILE_NAME = "test.c3d"


class C3dFunctionsTests(unittest.TestCase):

    def tearDown(self) -> None:
        if os.path.exists(f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}"):
            os.remove(f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}")

    def test_read(self):
        acq_trial = c3d.read_btk(f"{DATA_PATH}/{TEST_INPUT_FILE_NAME}")
        self.assertEqual(acq_trial.GetPointNumber(), 124)

    def test_write(self):
        TEST_LABEL = "Hallo"
        acq = c3d.read_btk(f"{DATA_PATH}/{TEST_INPUT_FILE_NAME}")
        acq.GetPoint(1).SetLabel(TEST_LABEL)
        c3d.write_btk(acq, f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}")
        acq = c3d.read_btk(f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}")
        self.assertEqual(acq.GetPoint(1).GetLabel(), TEST_LABEL)

    def test_sort(self):
        acq = c3d.read_btk(f"{DATA_PATH}/{TEST_INPUT_FILE_NAME}")
        event = acq.GetEvent(1)
        event.SetFrame(100000)
        c3d.sort_events(acq)
        self.assertNotEquals(acq.GetEvent(1), event)


class GaitEventContextTest(unittest.TestCase):

    def test_get_contrary_left(self):
        context = GaitEventContext.get_contrary_context(GaitEventContext.LEFT.value)
        self.assertEqual(context, GaitEventContext.RIGHT)

    def test_get_contrary_right(self):
        context = GaitEventContext.get_contrary_context(GaitEventContext.RIGHT.value)
        self.assertEqual(context, GaitEventContext.LEFT)


if __name__ == '__main__':
    unittest.main()
