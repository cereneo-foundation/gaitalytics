import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from pyCGM2.Lib.CGM import cgm2_5
from pyCGM2 import enums
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Report import normativeDatasets
from pyCGM2.Lib import analysis
from pyCGM2.Lib import plot


class TestAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.settings = files.loadModelSettings(self.settings_path, self.settings_file)
        self.test_acq = btkTools.smartReader(f"{self.data_path}{self.test_file}", self.settings["Translators"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_path = "test/data/"
        cls.test_file = "1min_filtered.c3d"
        cls.static_file = "1min_static.c3d"
        cls.settings_path = "settings/"
        cls.settings_file = "CGM2_5_CEFIR.settings"

    def test_analysis(self):
        modelled_filenames = ["1min_modelled_events.c3d"]  # two gait trials with both gait event and CGMi model ouptuts

        analysis_instance = analysis.makeAnalysis(self.data_path, modelled_filenames, emgChannels=None)
        # construction of the analysis instance.
        normative_dataset = normativeDatasets.NormativeData("Schwartz2008", "Free")
        # selected normative dataset
        ###
        # plots
        plot.plot_DescriptiveKinematic(self.data_path, analysis_instance, "LowerLimb", normative_dataset)
        ###
        plot.plot_DescriptiveKinetic(self.data_path, analysis_instance, "LowerLimb", normative_dataset)
        plot.plot_spatioTemporal(self.data_path, analysis_instance)

        # export as spreadsheet
        #analysis.exportAnalysis(analysis_instance, self.data_path, "spreadsheet")

    def test_modelling(self):
        # calibration options from settings
        left_flat_foot = self.settings["Calibration"]["Left flat foot"]
        right_flat_foot = self.settings["Calibration"]["Right flat foot"]
        head_flat = self.settings["Calibration"]["Head flat"]
        translators = self.settings["Translators"]
        marker_diameter = self.settings["Global"]["Marker diameter"]
        hjc = self.settings["Calibration"]["HJC"]
        point_suffix = self.settings["Global"]["Point suffix"]
        marker_weight = self.settings["Fitting"]["Weight"]
        moment_projection = self.settings["Fitting"]["Moment Projection"]
        # anthropometric parameters
        required_mp = dict()
        required_mp["Bodymass"] = 83.0
        required_mp["Height"] = 1720
        required_mp["LeftLegLength"] = 0
        required_mp["LeftKneeWidth"] = 0
        required_mp["RightLegLength"] = 0
        required_mp["RightKneeWidth"] = 0
        required_mp["LeftAnkleWidth"] = 0
        required_mp["RightAnkleWidth"] = 0
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
        ##
        # calibrate function
        model, final_acq_static, error = cgm2_5.calibrate(self.data_path,
                                                          self.static_file,
                                                          translators,
                                                          marker_weight,
                                                          required_mp,
                                                          optional_mp,
                                                          False,
                                                          left_flat_foot,
                                                          right_flat_foot,
                                                          head_flat,
                                                          marker_diameter,
                                                          hjc,
                                                          point_suffix)

        moment_projection_enums = enums.enumFromtext(moment_projection, enums.MomentProjection)
        matching_food_side_on = forceplates.matchingFootSideOnForceplate(self.test_acq)
        # detect correct foot contact with a force plate
        ###
        # fitting function

        # self.test_acq, detectAnomaly = cgm2_5.fitting(model, self.data_path, self.test_file,
        #                                               translators,
        #                                               marker_weight,
        #                                               False,
        #                                               marker_diameter,
        #                                               point_suffix,
        #                                               matching_food_side_on,
        #                                               moment_projection_enums,
        #                                               frameInit=None,
        #                                               frameEnd=None)
        # btkTools.smartWriter(self.test_acq, f"{self.data_path}1min_modelled.c3d")
        print(error)


if __name__ == '__main__':
    unittest.main()
