from argparse import ArgumentParser, Namespace

import configparser

import yaml
from pandas import DataFrame
from gait_analysis.utils import c3d

from gait_analysis.analysis.plot import BasicPlotter
from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker, EventNormalSequenceInterContextChecker
from gait_analysis.cycle.normalisation import LinearTimeNormalisation
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis
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

    cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())

    cycles = cycle_builder.build_cycles(acq_trial)
    normalised_data = LinearTimeNormalisation().normalise(acq_trial, cycles)
    desc_results = DescriptiveNormalisedAnalysis(normalised_data).analyse()
    plot = BasicPlotter(config)
    figures = plot.plot(desc_results)
    for fig in figures:
        fig.savefig(fname=f"plots/{fig._suptitle.get_text()}.svg", format="svg")
    # sd_results = SDNormalisedAnalysis(normalised_data).analyse()
    # print(sd_results)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
