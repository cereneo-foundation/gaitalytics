import unittest

from pyCGM2.Utils import files

import gait_analysis.utils.c3d
from gait_analysis import anthropomorphic as ap
from gait_analysis.utils.c3d import SideEnum
from pyCGM2.Tools import btkTools


class TestAnthropomorphic(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq_static = btkTools.smartReader(self.filename_static, settings["Translators"])
        self.acq_walk = btkTools.smartReader(self.filename_walk, settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.filename_static = f"{cls.data_path}1min_static.c3d"
        cls.filename_walk = f"{cls.data_path}1min.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5-pyCGM2.settings"

    def test_weight_good(self):
        calc = ap.AnthropomorphicCalculator(self.acq_static)
        calc.store_in_acquisition(self.acq_walk)
        weight = float(btkTools.smartGetMetadata(self.acq_walk, gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LABEL,
                                                 gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_BODYMASS_LABEL)[0])
        self.assertEqual(round(weight), 84)

    def test_height_good(self):
        calc = ap.AnthropomorphicCalculator(self.acq_static)
        calc.store_in_acquisition(self.acq_walk)
        height = float(btkTools.smartGetMetadata(self.acq_walk, gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LABEL,
                                                 gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_HEIGHT_LABEL)[0])
        self.assertEqual(round(height), 1588)

    def test_leg_length_good(self):
        calc = ap.AnthropomorphicCalculator(self.acq_static)
        calc.store_in_acquisition(self.acq_walk)
        l_leg_length = float(btkTools.smartGetMetadata(self.acq_walk,
                                                       gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LABEL,
                                                       f"{SideEnum.LEFT}{gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LEG_LENGTH_LABEL}"))
        r_leg_length = float(btkTools.smartGetMetadata(self.acq_walk,
                                                       gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LABEL,
                                                       f"{SideEnum.RIGHT}{gait_analysis.utils.utils.c3d_utils.METADATA_PROCESSING_LEG_LENGTH_LABEL}"))

        self.assertEqual(round(l_leg_length), 1588)
        self.assertEqual(round(r_leg_length), 1588)


if __name__ == '__main__':
    unittest.main()
