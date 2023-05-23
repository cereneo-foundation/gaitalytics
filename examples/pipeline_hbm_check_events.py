from argparse import ArgumentParser, Namespace

import configparser
from gait_analysis.utils import c3d


from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker, EventNormalSequenceInterContextChecker
from gait_analysis.cycle.normalisation import LinearTimeNormalisation

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.ini"
DATA_PATH = "./test/data/"
TEST_EVENTS_FILE_NAME = "Baseline.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():


    # load file into memory

    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    event_checker = BasicContextChecker()
    detected, anomalies = event_checker.check_events(acq_trial)
    for anomaly in anomalies:
        print(anomaly)



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
