from argparse import ArgumentParser, Namespace

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

import gait_analysis.events
from gait_analysis.events import EventNormalSequencePerContextChecker, EventNormalSequenceInterContextChecker


# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"
DATA_PATH = "C:/ViconData/Handshake/Bramberger/20230420/"
TEST_EVENTS_FILE_NAME = "S003.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory

    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    # detect gait events #
    ######################
    [anomaly_detected, abnormal_event_frames] = EventNormalSequencePerContextChecker(
        EventNormalSequenceInterContextChecker()).check_events(acq_trial)
    print(f"Anomaly: {anomaly_detected}")
   # print(f"Frames: {abnormal_event_frames}")
    for abnorm in abnormal_event_frames:
        print(abnorm)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
