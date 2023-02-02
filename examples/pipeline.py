from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.analysis import fit_trial_to_model

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

# define patient specific values
BODY_WEIGHT = 83.0
BODY_HEIGHT = 1720


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory
    acq = btkTools.smartReader(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}", settings["Translators"])

    # filter points and force plate #
    #################################
    low_pass_point_filtering(acq)
    low_pass_force_plate_filtering(acq)
    # save filtered file
    btkTools.smartWriter(acq, f"{DATA_PATH}{TEST_FILTERED_FILE_NAME}")

    # fit trial to model #
    ######################
    anomaly_detected = fit_trial_to_model(acq, DATA_PATH, TEST_FILTERED_FILE_NAME, STATIC_FILE_NAME, settings, BODY_WEIGHT, BODY_HEIGHT)
    btkTools.smartWriter(acq, f"{DATA_PATH}{TEST_MODELLED_FILE_NAME}")

    # detect gait events #
    ######################
    GaitEventDetectorFactory().get_zenis_detector().detect_events(acq)
    btkTools.smartWriter(acq, f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()



