import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from pyCGM2.Lib.CGM import cgm2_2


class TestAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.test_acq = btkTools.smartReader(self.test_file, self.settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.test_file = "test/data/walking_0_11.c3d"
        cls.static_file = "static.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "HBM_Trunk_cgm2.2.settings"

    def test_analysis(self):
        left_flat_foot = self.settings["Calibration"]["Left flat foot"]
        right_flat_foot = self.settings["Calibration"]["Right flat foot"]
        head_flat = self.settings["Calibration"]["Head flat"]
        translators = self.settings["Translators"]
        marker_diameter = self.settings["Global"]["Marker diameter"]
        point_suffix = self.settings["Global"]["Point suffix"]
        hjc_method = self.settings["Calibration"]["HJC"]
        ik_accuracy = self.settings["Global"]["IkAccuracy"]
        weights = self.settings["Fitting"]["Weight"]

        required_mp = dict()
        required_mp["Bodymass"] = 75.0
        required_mp["Height"] = 1750
        required_mp["LeftLegLength"] = 800
        required_mp["LeftKneeWidth"] = 90
        required_mp["RightLegLength"] = 800
        required_mp["RightKneeWidth"] = 90
        required_mp["LeftAnkleWidth"] = 60
        required_mp["RightAnkleWidth"] = 60
        required_mp["LeftSoleDelta"] = 0
        required_mp["RightSoleDelta"] = 0
        required_mp["LeftShoulderOffset"] = 0
        required_mp["LeftElbowWidth"] = 0
        required_mp["LeftWristWidth"] = 0
        required_mp["LeftHandThickness"] = 0
        required_mp["RightShoulderOffset"] = 0
        required_mp["RightElbowWidth"] = 0
        required_mp["RightWristWidth"] = 0
        required_mp["RightHandThickness"] = 0

        optional_mp = dict()
        optional_mp["InterAsisDistance"] = 0
        optional_mp["LeftAsisTrocanterDistance"] = 0
        optional_mp["LeftTibialTorsion"] = 0
        optional_mp["LeftThighRotation"] = 0
        optional_mp["LeftShankRotation"] = 0
        optional_mp["RightAsisTrocanterDistance"] = 0
        optional_mp["RightTibialTorsion"] = 0
        optional_mp["RightThighRotation"] = 0
        optional_mp["RightShankRotation"] = 0

        model, finalAcqStatic, error = cgm2_2.calibrate(self.data_path,
                                                        self.static_file,
                                                        translators,
                                                        weights,
                                                        required_mp,
                                                        optional_mp,
                                                        ik_accuracy,
                                                        left_flat_foot,
                                                        right_flat_foot,
                                                        head_flat,
                                                        marker_diameter,
                                                        hjc_method,
                                                        point_suffix)

        print(error)


if __name__ == '__main__':
    unittest.main()
