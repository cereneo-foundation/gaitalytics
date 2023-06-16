from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.cycle.extraction import CycleDataExtractor
from gait_analysis.cycle.normalisation import LinearTimeNormalisation
from gait_analysis.event.anomaly import BasicContextChecker
from gait_analysis.utils import c3d
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.utils import cycle_points_to_csv

# This is an example pipeline #
###############################

# Define paths
SETTINGS_FILE = "settings/hbm_pig.yaml"
DATA_PATH = "./test/data/"
TEST_EVENTS_FILE_NAME = "Baseline.4.c3d"


def main():
    configs = ConfigProvider()
    configs.read_configs(SETTINGS_FILE)
    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_EVENTS_FILE_NAME}")
    cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())
    cycles = cycle_builder.build_cycles(acq_trial)
    cycle_data = CycleDataExtractor(configs).extract_data(cycles, acq_trial)
    cycle_points_to_csv(cycle_data, "out", "baseline")

    normalised_data = LinearTimeNormalisation().normalise(cycle_data)
    cycle_points_to_csv(normalised_data, "out", "baseline")




# Using the special variable
# __name__
if __name__ == "__main__":
    main()
