import os
import re
from argparse import ArgumentParser, Namespace

from gaitalytics import utils, api

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
    configs = utils.ConfigProvider(SETTINGS_FILE)
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
                api.detect_gait_events(f"{root}/{filtered_file}", root, configs)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
