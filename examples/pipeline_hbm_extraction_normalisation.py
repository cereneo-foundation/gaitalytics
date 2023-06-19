from gait_analysis.api import ConfigProvider, cycle_points_to_csv
from gait_analysis import c3d
from gait_analysis.cycle_extraction import HeelStrikeToHeelStrikeCycleBuilder, CycleDataExtractor, \
    LinearTimeNormalisation
from gait_analysis.events import ContextPatternChecker

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
    cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(ContextPatternChecker())
    cycles = cycle_builder.build_cycles(acq_trial)
    cycle_data = CycleDataExtractor(configs).extract_data(cycles, acq_trial)
    cycle_points_to_csv(cycle_data, "out", "baseline")

    normalised_data = LinearTimeNormalisation().normalise(cycle_data)
    cycle_points_to_csv(normalised_data, "out", "baseline")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
