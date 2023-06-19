from argparse import ArgumentParser, Namespace

from gait_analysis.c3d import C3dAcquistion
from gait_analysis.events import ZenisGaitEventDetector
from gait_analysis.api import ConfigProvider

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.yaml"
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
    configs = ConfigProvider()

    configs.read_configs(SETTINGS_FILE)

    acq_trial = C3dAcquistion.read_btk(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}")

    # detect gait events #
    ######################
    ZenisGaitEventDetector(configs).detect_events(acq_trial.acq)

    acq_trial.write_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")




# Using the special variable
# __name__
if __name__ == "__main__":
    main()
