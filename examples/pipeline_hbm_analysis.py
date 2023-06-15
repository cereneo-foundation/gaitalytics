import pandas as pd

from gait_analysis.analysis.cycle import SpatioTemporalAnalysis, JointAnglesCycleAnalysis
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis
from gait_analysis.cycle.extraction import BasicCyclePoint
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.io import CyclePointLoader

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "./test/data/"
TEST_EVENTS_FILE_NAME = "Baseline.4.c3d"


def main():
    configs = ConfigProvider()
    configs.read_configs(SETTINGS_FILE)
    loader = CyclePointLoader(configs, "out")
    cycle_data = loader.get_raw_cycle_points()
    norm_data = loader.get_norm_cycle_points()

    desc_results = DescriptiveNormalisedAnalysis(norm_data).analyse()
    desc_results.to_csv("out/desc.csv")

    joint_angles_results = JointAnglesCycleAnalysis(cycle_data).analyse()
    spatio_results = SpatioTemporalAnalysis(configs, cycle_data, 100).analyse()
    joint_angles_results.merge(spatio_results, on=BasicCyclePoint.CYCLE_NUMBER).to_csv("out/nice.csv")



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
