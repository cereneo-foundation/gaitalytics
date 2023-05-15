import os
import re
from argparse import ArgumentParser, Namespace
import json

from pyCGM2.Tools import btkTools

from gait_analysis.event.anomaly import BasicContextChecker

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
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile(".*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            acq_trial = btkTools.smartReader(f"{root}/{filtered_file}")
            detected, anomalies = BasicContextChecker().check_events(acq_trial)
            if detected:
                print(f"{root}/{filtered_file}")
                event_anomaly = filtered_file.replace(".4.c3d", "_anomalies.txt")
                f = open(f"{root}/{event_anomaly}", "w")
                json.dump(anomalies, f)
                f.close()








# Using the special variable
# __name__
if __name__ == "__main__":
    main()
