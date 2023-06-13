import os
import re
from argparse import ArgumentParser, Namespace

from gait_analysis.analysis.raw import JointAnglesAnalysis, JointAngularVelocityAnalysis
from gait_analysis.cycle.extraction import CycleDataExtractor
from gait_analysis.utils import c3d

from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker
from pandas import DataFrame
from gait_analysis.utils.config import ConfigProvider

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
        r = re.compile("S0.*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            filename = filtered_file.replace(".4.c3d", "_joint_angles.csv")
            if not os.path.exists(f"out/{filename}.csv"):
                print(f"{root}/{filtered_file}")
                acq_trial = c3d.read_btk(f"{root}/{filtered_file}")
                cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())
                cycles = cycle_builder.build_cycles(acq_trial)
                cycle_data = CycleDataExtractor(configs).extract_data(cycles, acq_trial)
                results_angles = JointAnglesAnalysis(cycle_data).analyse()
                results_velo = JointAngularVelocityAnalysis(cycle_data).analyse()
                results = DataFrame.merge(results_angles, results_velo, on=['cycle_number', 'metric', 'data_type'])

                results.to_csv(f"out/{filename}.csv", index=False)



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
