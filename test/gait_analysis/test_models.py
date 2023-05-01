import unittest

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.analysis import fit_trial_to_model
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.utils import calculate_height_from_markers, calculate_weight_from_force_plates


class TestHBMToCGM2Mapper(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.acq = btkTools.smartReader(self.path, settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = "test/data/test.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "HBM_Trunk_cgm2.5.settings"

        cls._NAME_MAPPINGS = ("RASI",
                              "LASI",
                              "RPSI",
                              "LPSI",
                              "LTHI",
                              "LKNE",
                              "LKNM",
                              "LTIB",
                              "LANK",
                              "LMED",
                              "LFMH",
                              "LVMH",
                              "LHEE",
                              "LTOE",
                              "RTHI",
                              "RKNE",
                              "RKNM",
                              "RTIB",
                              "RANK",
                              "RMED",
                              "RFMH",
                              "RVMH",
                              "RHEE",
                              "RTOE",
                              "CLAV")

    def test_good_case(self):
        HBMToCGM2Mapper().calculate_missing_markers(self.acq)
        for marker_name in self._NAME_MAPPINGS:
            try:
                self.acq.GetPoint(marker_name)
            except RuntimeError:
                self.assertTrue(False, f"{marker_name} not found")


class TestCGM2HBMtoCGM2Mapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.test_file = "1min_CGM_HBM.c3d"
        cls.static_file = "1min_CGM_HBM_static.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5_CEFIR.settings"

    def test_good_case(self):
        settings = files.loadModelSettings(self.settings_path, self.settings_file)

        # load file into memory
        acq_calc = btkTools.smartReader(f"{self.data_path}{self.static_file}", settings["Translators"])
        acq_trial = btkTools.smartReader(f"{self.data_path}{self.static_file}", settings["Translators"])


        # get anthropometric parameters #
        #################################
        weight = calculate_weight_from_force_plates(acq_calc)
        height = calculate_height_from_markers(acq_calc)

        # fit trial to model #
        ######################
        anomaly_detected = fit_trial_to_model(acq_trial, acq_calc, self.data_path, self.test_file,
                                              self.static_file, settings, weight, height)

        # detect gait events #
        ######################
        GaitEventDetectorFactory().get_zenis_detector().detect_events(acq_trial)


if __name__ == '__main__':
    unittest.main()
