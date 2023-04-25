from pyCGM2.Report import normativeDatasets
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from pyCGM2.Lib import analysis, plot

from gait_analysis.analysis import fit_trial_to_model
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering


# This is an example pipeline #
###############################

# Define paths
DATA_PATH = "C:/ViconData/Handshake/Bramberger/20230420/"
TEST_ORIGIN_FILE_NAME = "S003.3.c3d"
TEST_EVENTS_FILE_NAME = "S003.4.c3d"
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"

ANALYSIS_KINEMATIC_LABELS_DICT = {
    'Left': ["LHipAngles", "LKneeAngles", "LAnkleAngles", "LFootProgressAngles", "LPelvisAngles",
             "LThoraxAngles", "LSpineAngles"],
    'Right': ["RHipAngles", "RKneeAngles", "RAnkleAngles", "RFootProgressAngles", "RPelvisAngles",
              "RThoraxAngles", "RSpineAngles"]}

ANALYSIS_KINETIC_LABELS_DICT = {
    'Left': ["LHipMoment", "LKneeMoment", "LAnkleMoment", "LHipPower", "LKneePower", "LAnklePower"],
    'Right': ["RHipMoment", "RKneeMoment", "RAnkleMoment", "RHipPower", "RKneePower", "RAnklePower"]}


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory
  #  acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}", settings["Translators"])

    # detect gait events #
    ######################

   # GaitEventDetectorFactory().get_zenis_detector().detect_events(acq_trial)
   # btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")
    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}", settings["Translators"])

    analysisInstance = analysis.makeAnalysis(DATA_PATH, TEST_EVENTS_FILE_NAME,
                                             emgChannels=None,
                                             btkAcqs=[acq_trial],
                                             kinematicLabelsDict = ANALYSIS_KINEMATIC_LABELS_DICT,
                                             kineticLabelsDict = ANALYSIS_KINETIC_LABELS_DICT)
    normativeDataset = normativeDatasets.NormativeData("Schwartz2008", "Free")  # selected normative dataset
    ###
    # plots
    plot.plot_DescriptiveKinematic(DATA_PATH, analysisInstance, "LowerLimb", normativeDataset)
    ###
    plot.plot_DescriptiveKinetic(DATA_PATH, analysisInstance, "LowerLimb", normativeDataset)
    plot.plot_spatioTemporal(DATA_PATH, analysisInstance)

    # export as spreadsheet
    analysis.exportAnalysis(analysisInstance, DATA_PATH, "spreadsheet")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
