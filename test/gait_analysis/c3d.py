import os
import unittest

from gait_analysis.c3d import C3dAcquisition
from gait_analysis.c3d import GaitEventContext
from gait_analysis.utils import ConfigProvider

DATA_PATH = "./test/data"
TEST_INPUT_FILE_NAME = "Baseline.3.c3d"
TEST_OUTPUT_FILE_NAME = "test.c3d"
SETTINGS_FILE = "settings/hbm_pig.yaml"


class C3dFunctionsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        configs = ConfigProvider()
        configs.read_configs(SETTINGS_FILE)
        cls._configs: ConfigProvider = configs

    def tearDown(self) -> None:
        if os.path.exists(f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}"):
            os.remove(f"{DATA_PATH}/{TEST_OUTPUT_FILE_NAME}")

    def test_get_point_frame_number(self):
        acq_trial = C3dAcquisition.read_btk(f"{DATA_PATH}/{TEST_INPUT_FILE_NAME}")
        self.assertEqual(acq_trial.get_point_frame_number(), 24998)

    def test_get_point(self):
        acq_trial = C3dAcquisition.read_btk(f"{DATA_PATH}/{TEST_INPUT_FILE_NAME}")
        self.assertEqual(acq_trial.get_point(self._configs.MARKER_MAPPING.right_heel), 24998)

    def test_write(self):
        pass

    def test_sort(self):
        pass


class GaitEventContextTest(unittest.TestCase):

    def test_get_contrary_left(self):
        context = GaitEventContext.get_contrary_context(GaitEventContext.LEFT.value)
        self.assertEqual(context, GaitEventContext.RIGHT)

    def test_get_contrary_right(self):
        context = GaitEventContext.get_contrary_context(GaitEventContext.RIGHT.value)
        self.assertEqual(context, GaitEventContext.LEFT)


if __name__ == '__main__':
    unittest.main()
