from argparse import ArgumentParser, Namespace
import os
import re

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.event.detection import ZenisGaitEventDetector

# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"
DATA_PATH = "C:/ViconData/Handshake/"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile(".*\.3\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            print(filtered_file)
            event_added_file = filtered_file.replace("3.c3d", "4.c3d")
            if not os.path.exists(f"{root}/{event_added_file}"):
                print(f"{root}/{filtered_file}")
                acq_trial = btkTools.smartReader(f"{root}/{filtered_file}", settings["Translators"])
                ZenisGaitEventDetector().detect_events(acq_trial)
                btkTools.smartWriter(acq_trial, f"{root}/{event_added_file}")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
