import os
import re
from argparse import ArgumentParser, Namespace

from gaitalytics.utils import ConfigProvider
from gaitalytics import api

SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "C:/ViconData/Handshake/"
DATA_OUTPUT_BASE = "//192.168.102.50/studyRepository/StimuLoop/Handshake_semantics"
DATA_OUTPUT_CYCLES = "/cycle_outputs"
DATA_OUTPUT_METRICS = "/metrics"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    configs = ConfigProvider(SETTINGS_FILE)
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile("S0.*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            print(f"{root}/{filtered_file}")
            subject = filtered_file.replace(".4.c3d", "")
            cycle_path = f"{DATA_OUTPUT_BASE}{DATA_OUTPUT_CYCLES}/{subject}"
            if not os.path.exists(cycle_path):
                os.mkdir(cycle_path)
                cycle_data = api.extract_cycles(f"{root}/{filtered_file}", configs, buffer_output_path=cycle_path)
            else:
                cycle_data = api.extract_cycles_buffered(cycle_path, configs).get_raw_cycle_points()
            analysis = [api.ANALYSIS_MOMENTS,
                 api.ANALYSIS_ANGLES,
                 api.ANALYSIS_POWERS,
                 api.ANALYSIS_FORCES,
                 api.ANALYSIS_SPATIO_TEMP]
            results = api.analyse_data(cycle_data, configs, methode=analysis)

            filename_base = f"{DATA_OUTPUT_BASE}{DATA_OUTPUT_METRICS}/{subject}"
            results.to_csv(f"{filename_base}_metrics.csv")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
