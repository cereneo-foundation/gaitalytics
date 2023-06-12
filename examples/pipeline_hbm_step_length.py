from argparse import ArgumentParser, Namespace

from typing import List

import yaml
from gait_analysis.utils import c3d

from gait_analysis.cycle.builder import ToeOffToToeOffCycleBuilder, GaitCycle
from gait_analysis.event.anomaly import BasicContextChecker

import matplotlib.pyplot as plt

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "./test/data/"
TEST_EVENTS_FILE_NAME = "S003.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    # load file into memory
    f = open(SETTINGS_FILE, "r")
    config = yaml.safe_load(f)

    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    cycle_builder = ToeOffToToeOffCycleBuilder(BasicContextChecker())

    TTcycles = cycle_builder.build_cycles(acq_trial)


def get_step_length(cycles: List[GaitCycle]):
    for cycle in cycles:
        cycle.number
        cycle.context
        cycle.unused_event


# Using the special variable
# __name__
if __name__ == "__main__":
    main()

