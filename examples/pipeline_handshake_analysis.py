import os
import re
from argparse import ArgumentParser, Namespace

from gait_analysis.analysis.cycle import JointAnglesCycleAnalysis, SpatioTemporalAnalysis
from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.cycle.extraction import CycleDataExtractor, BasicCyclePoint
from gait_analysis.event.anomaly import BasicContextChecker
from gait_analysis.utils import c3d
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.io import CyclePointLoader
from gait_analysis.utils.utils import cycle_points_to_csv

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
    configs = ConfigProvider()
    configs.read_configs(SETTINGS_FILE)
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile("S0.*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            print(f"{root}/{filtered_file}")
            subject = filtered_file.replace(".4.c3d", "")
            cycle_path = f"{DATA_OUTPUT_BASE}{DATA_OUTPUT_CYCLES}/{subject}"
            if not os.path.exists(cycle_path):
                acq_trial = c3d.read_btk(f"{root}/{filtered_file}")
                cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())
                cycles = cycle_builder.build_cycles(acq_trial)
                cycle_data = CycleDataExtractor(configs).extract_data(cycles, acq_trial)
                os.mkdir(cycle_path)
                cycle_points_to_csv(cycle_data, cycle_path, subject)
            else:
                cycle_data = CyclePointLoader(configs, cycle_path).get_raw_cycle_points()

            joint_angles_results = JointAnglesCycleAnalysis(cycle_data).analyse()
            spatio_results = SpatioTemporalAnalysis(configs, cycle_data, 100).analyse()
            filename_base = f"{DATA_OUTPUT_BASE}{DATA_OUTPUT_METRICS}/{subject}"
            joint_angles_results.merge(spatio_results, on=BasicCyclePoint.CYCLE_NUMBER).to_csv(f"{filename_base}_metrics.csv")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
