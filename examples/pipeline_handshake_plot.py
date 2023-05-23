import os
import re
from argparse import ArgumentParser, Namespace

import pandas as pd
import yaml

from gait_analysis.analysis.plot import PdfPlotter, PlotGroup
from gait_analysis.utils import c3d

from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker
from gait_analysis.cycle.normalisation import LinearTimeNormalisation
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis

SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "C:/ViconData/Handshake/"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    f = open(SETTINGS_FILE, "r")
    config = yaml.safe_load(f)

    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile(".*desc\.csv")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:

            desc_results = pd.read_csv(f"{root}/{filtered_file}")
            plot = PdfPlotter(config, root)

            plot.plot(desc_results, [PlotGroup.KINEMATICS, PlotGroup.KINETICS])



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
