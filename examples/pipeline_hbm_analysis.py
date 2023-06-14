from gait_analysis.analysis.cycle import SpatioTemporalAnalysis, JointAnglesCycleAnalysis
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis
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
    desc_results.to_csv("out/desc.csv", index=False)

    joint_angles_results = JointAnglesCycleAnalysis(cycle_data).analyse()
    joint_angles_results.to_csv("out/joint_angles.csv", index=False)



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
