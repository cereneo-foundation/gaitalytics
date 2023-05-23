from argparse import ArgumentParser, Namespace

import yaml

from gait_analysis.utils import c3d

from gait_analysis.analysis.plot import PdfPlotter, SeparatelyPicturePlot, PlotGroup
from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker
from gait_analysis.cycle.normalisation import LinearTimeNormalisation
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "./test/data/"
TEST_EVENTS_FILE_NAME = "Baseline.4.c3d"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():

    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")

    cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())

    cycles = cycle_builder.build_cycles(acq_trial)
    normalised_data = LinearTimeNormalisation().normalise(acq_trial, cycles)
    desc_results = DescriptiveNormalisedAnalysis(normalised_data).analyse()
    desc_results.to_csv("plots/desc.csv", index=False)



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
