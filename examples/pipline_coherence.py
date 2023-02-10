from pyCGM2.Report import normativeDatasets
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from pyCGM2.Lib import analysis, plot

from gait_analysis.analysis import fit_trial_to_model
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.emg import EMGCoherenceAnalysis
from gait_analysis.utils import calculate_height_from_markers, calculate_weight_from_force_plates

# This is an example pipeline #
###############################

# Define paths
DATA_PATH = "test/data/"
TEST_ORIGIN_FILE_NAME = "1min.c3d"
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "CGM2_5-pyCGM2.settings"


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)
    acq_trial = btkTools.smartReader(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}", settings["Translators"])

    coh_left = EMGCoherenceAnalysis(1, 2, "Left")
    coh_right = EMGCoherenceAnalysis(3, 4, "Right")


    coh_left.filter(acq_trial)
    windows = coh_left.get_windows(acq_trial)
    coherence_result_left = coh_left.calculate_coherence(acq_trial, windows)

    coh_right.filter(acq_trial)
    windows = coh_right.get_windows(acq_trial)
    coherence_result_right = coh_right.calculate_coherence(acq_trial, windows)






# Using the special variable
# __name__
if __name__ == "__main__":
    main()
