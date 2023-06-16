from gait_analysis.analysis import JointMomentsCycleAnalysis, JointPowerCycleAnalysis, JointAnglesCycleAnalysis, \
    SpatioTemporalAnalysis, DescriptiveNormalisedAnalysis
from gait_analysis.api import BasicCyclePoint, ConfigProvider, CyclePointLoader

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
    spatio_results = SpatioTemporalAnalysis(configs, cycle_data).analyse()
    moments_angles_results = JointMomentsCycleAnalysis(cycle_data).analyse()
    powers_angles_results = JointPowerCycleAnalysis(cycle_data).analyse()
    results = joint_angles_results.merge(spatio_results, on=BasicCyclePoint.CYCLE_NUMBER)
    results = results.merge(moments_angles_results, on=BasicCyclePoint.CYCLE_NUMBER)
    results = results.merge(powers_angles_results, on=BasicCyclePoint.CYCLE_NUMBER)
    results.to_csv("out/nice.csv")



# Using the special variable
# __name__
if __name__ == "__main__":
    main()
