import os

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.utils import correct_points_frame_by_frame

# This is an example pipeline #
###############################

# Define paths
DATA_PATH = "test/data/"
TEST_ORIGIN_FILE_NAME = "1min.c3d"
TEST_FILTERED_FILE_NAME = "1min_filtered.c3d"
TEST_MODELLED_FILE_NAME = "1min_filtered_modelled.c3d"
TEST_EVENTS_FILE_NAME = "1min_filtered_modelled_events.c3d"
TEST = "test.c3d"
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

    GaitEventDetectorFactory().get_zenis_detector().detect_events(acq_trial)
    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST}")
    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST}", settings["Translators"])
    correct_points_frame_by_frame(acq_trial)

    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST}")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
