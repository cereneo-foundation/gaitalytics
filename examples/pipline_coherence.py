from gaitalytics import emg, files

# This is an example pipeline #
###############################

# Define paths
DATA_PATH = "test/data/"
TEST_ORIGIN_FILE_NAME = "1min_emg_walk.c3d"
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "CGM2_5-pyCGM2.settings"


def main():
    acq_trial = c3d.read_btk(f"{DATA_PATH}{TEST_ORIGIN_FILE_NAME}")

    # Instanciate EMGCoherenceAnalysis objects
    coh_left = emg.EMGCoherenceAnalysis(1, 2, "Left")  # Verify if good channel indexs
    coh_right = emg.EMGCoherenceAnalysis(3, 4, "Right")  # Verify if good channel indexs

    # Results stored in a tuple of frequencies and coherences
    coherence_result_left = coh_left.calculate_coherence(acq_trial)
    coherence_result_right = coh_right.calculate_coherence(acq_trial)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
