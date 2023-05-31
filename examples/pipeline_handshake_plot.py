import os
import re
from argparse import ArgumentParser, Namespace

import pandas as pd


from gait_analysis.analysis.plot import PdfPlotter, PlotGroup
from gait_analysis.utils import config

SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "out/"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    configs = config.read_configs(SETTINGS_FILE)

    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile(".*desc\.csv")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:

            desc_results = pd.read_csv(f"{root}/{filtered_file}")
            filename = filtered_file.replace("desc.csv", "overview.pdf")
            plot = PdfPlotter(configs, "out", filename)

            plot.plot(desc_results, [PlotGroup.KINEMATICS, PlotGroup.KINETICS])



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
