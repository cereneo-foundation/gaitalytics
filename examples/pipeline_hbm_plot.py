from argparse import ArgumentParser, Namespace


import pandas as pd

from gait_analysis.analysis.plot import PdfPlotter, SeparatelyPicturePlot, PlotGroup
from gait_analysis.utils import config
from gait_analysis.utils.config import MarkerModelConfig

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
    # load file into memory
    configs = MarkerModelConfig()
    configs.read_configs(SETTINGS_FILE)

    desc_results = pd.read_csv("plots/desc.csv")
    plot = PdfPlotter(configs, "plots")

    plot.plot(desc_results, [PlotGroup.KINEMATICS, PlotGroup.KINETICS])

    plot = SeparatelyPicturePlot(configs, "plots", "svg")

    plot.plot(desc_results, [PlotGroup.KINEMATICS, PlotGroup.KINETICS])


    # sd_results = SDNormalisedAnalysis(normalised_data).analyse()
    # print(sd_results)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
