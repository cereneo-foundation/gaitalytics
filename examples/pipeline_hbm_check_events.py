from argparse import ArgumentParser, Namespace

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.cycles import HeelStrikeCycleBuilder
from gait_analysis.event.events import EventNormalSequencePerContextChecker, EventNormalSequenceInterContextChecker

# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"
DATA_PATH = "C:/Users/boeni/Projects/gait_analysis/test/data/"
TEST_EVENTS_FILE_NAME = "PGV_0_45.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory

    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    cycle_builder = EventCycleBuilder(
        EventNormalSequencePerContextChecker(EventNormalSequenceInterContextChecker()))

    cycles = cycle_builder.build_cycles(acq_trial)
    cycles





# Using the special variable
# __name__
if __name__ == "__main__":
    main()
