import os

os.add_dll_directory("C:/OpenSim 4.4/bin")

from pyCGM2.Lib import analysis, plot
from pyCGM2.Report import normativeDatasets
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.analysis import fit_trial_to_model
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering
from gait_analysis.utils import calculate_height_from_markers, calculate_weight_from_force_plates

# This is an example pipeline #
###############################

# Define paths
DATA_PATH = "test/data/"
TEST_ORIGIN_FILE_NAME = "1min.c3d"
TEST_FILTERED_FILE_NAME = "1min_filtered.c3d"
TEST_MODELLED_FILE_NAME = "1min_filtered_modelled.c3d"
TEST_EVENTS_FILE_NAME = "1min_filtered_modelled_events.c3d"
STATIC_FILE_NAME = "1min_static.c3d"
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "CGM2_5-pyCGM2.settings"


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory
    acq_calc = btkTools.smartReader(f"{DATA_PATH}{STATIC_FILE_NAME}", settings["Translators"])
    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}", settings["Translators"])

    # filter points and force plate #
    #################################
    low_pass_point_filtering(acq_trial)
    low_pass_force_plate_filtering(acq_trial)
    # save filtered file
    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST_FILTERED_FILE_NAME}")

    # get anthropometric parameters #
    #################################
    weight = calculate_weight_from_force_plates(acq_calc)
    height = calculate_height_from_markers(acq_calc)

    # fit trial to model #
    ######################
    anomaly_detected = fit_trial_to_model(acq_trial, acq_calc, DATA_PATH, TEST_FILTERED_FILE_NAME,
                                          STATIC_FILE_NAME, settings, weight, height)
    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST_MODELLED_FILE_NAME}")

    # detect gait events #
    ######################
    GaitEventDetectorFactory().get_zenis_detector().detect_events(acq_trial)
    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    analysisInstance = analysis.makeAnalysis(DATA_PATH, [TEST_EVENTS_FILE_NAME],
                                             emgChannels=None)
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
