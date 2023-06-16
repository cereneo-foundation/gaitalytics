from argparse import ArgumentParser, Namespace
import os
import re

from gait_analysis import c3d
from gait_analysis.events import ZenisGaitEventDetector
from gait_analysis.api import ConfigProvider

# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "C:/ViconData/Handshake/"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    configs = ConfigProvider()
    configs.read_configs(SETTINGS_FILE)
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile("S.*\.3\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            print(f"{root}/{filtered_file}")
            event_added_file = filtered_file.replace("3.c3d", "4.c3d")
            if os.path.exists(f"{root}/{event_added_file}"):
             #   os.remove(f"{root}/{event_added_file}")
                print("existing file deleted")
            else:
                print(f"add events")
                acq_trial = c3d.read_btk(f"{root}/{filtered_file}")
                ZenisGaitEventDetector(configs).detect_events(acq_trial)
                c3d.write_btk(acq_trial, f"{root}/{event_added_file}")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
