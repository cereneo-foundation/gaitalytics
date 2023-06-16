import os
import re
from argparse import ArgumentParser, Namespace

from gait_analysis.utils import c3d
from gait_analysis.event.anomaly import BasicContextChecker, EventNormalSequenceInterContextChecker, EventSpacingChecker

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
        r = re.compile("S.*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            print(f"{root}/{filtered_file}")
            acq_trial = c3d.read_btk(f"{root}/{filtered_file}")
            detected, anomalies = BasicContextChecker(EventSpacingChecker()).check_events(acq_trial)
            if detected:
                print(f"detected")
                event_anomaly = filtered_file.replace(".4.c3d", "_anomalies.txt")
                f = open(f"./out/{event_anomaly}", "w")
                for anomaly in anomalies:
                    print(f"{anomaly['Context']}: {anomaly['Start-Frame']} - {anomaly['End-Frame']} - {anomaly['Anomaly']}", file=f)

                f.close()


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
