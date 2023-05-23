from argparse import ArgumentParser, Namespace

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.event.detection import ZenisGaitEventDetector, ForcePlateEventDetection


# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"
DATA_PATH = "./test/data/"
TEST_ORIGIN_FILE_NAME = "Baseline.3.c3d"
TEST_EVENTS_FILE_NAME = "Baseline.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory

    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}", settings["Translators"])

    # detect gait events #
    ######################
    ZenisGaitEventDetector().detect_events(acq_trial)

    btkTools.smartWriter(acq_trial, f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")




# Using the special variable
# __name__
if __name__ == "__main__":
    main()
