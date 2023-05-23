from argparse import ArgumentParser, Namespace

from gait_analysis.utils import c3d
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
    # load file into memory

    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}")

    # detect gait events #
    ######################
    ZenisGaitEventDetector().detect_events(acq_trial)

    c3d.write_btk(acq_trial, f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")




# Using the special variable
# __name__
if __name__ == "__main__":
    main()
