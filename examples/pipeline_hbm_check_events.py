from argparse import ArgumentParser, Namespace

from gait_analysis.c3d import C3dAcquistion

from gait_analysis.events import ContextPatternChecker, EventSpacingChecker

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

    acq_trial = C3dAcquistion.read_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    event_checker = EventSpacingChecker(ContextPatternChecker())
    detected, anomalies = event_checker.check_events(acq_trial.acq)
    for anomaly in anomalies:
        print(anomaly)



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
