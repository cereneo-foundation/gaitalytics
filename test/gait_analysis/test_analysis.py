import unittest
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from pyCGM2.Lib.CGM import cgm2_5
from pyCGM2 import enums
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Report import normativeDatasets
from pyCGM2.Lib import analysis
from pyCGM2.Lib import plot
from gait_analysis.analysis import fit_trial_to_model


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
        modelled_filenames = ["1min_filtered_modelled_events.c3d"]  # two gait trials with both gait event and CGMi model ouptuts

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

    def test_modelling(self):
        fit_trial_to_model(self.test_acq, self.data_path, self.test_file, self.static_file, self.settings, 83.0, 1720)


if __name__ == '__main__':
    unittest.main()
