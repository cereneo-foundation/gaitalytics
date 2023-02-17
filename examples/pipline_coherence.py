
from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files
from gait_analysis.emg import EMGCoherenceAnalysis
from gait_analysis.filtering import band_pass_filter_emg


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

    #Instanciate EMGCoherenceAnalysis objects
    coh_left = EMGCoherenceAnalysis(1, 2, "Left")
    coh_right = EMGCoherenceAnalysis(3, 4, "Right")

    #Processing
    print(acq_trial)
    band_pass_filter_emg(acq_trial)
    band_pass_filter_emg(acq_trial, coh_left.emg_channel_1_index)
    band_pass_filter_emg(acq_trial, coh_left.emg_channel_2_index)
    band_pass_filter_emg(acq_trial, coh_right.emg_channel_1_index)
    band_pass_filter_emg(acq_trial, coh_right.emg_channel_2_index)

    #Results stored in a tuple of frequencies and coherences
    coherence_result_left = coh_left.calculate_coherence(acq_trial)
    coherence_result_right = coh_right.calculate_coherence(acq_trial)






# Using the special variable
# __name__
if __name__ == "__main__":
    main()
