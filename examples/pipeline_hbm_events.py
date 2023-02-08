from argparse import ArgumentParser, Namespace

from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files

from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering
from gait_analysis.models import HBMToCGM2Mapper
# This is an example pipeline #
###############################

# Define paths
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    namespace = get_args()
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)

    # load file into memory
    acq_trial = btkTools.smartReader(f"{namespace.path}{namespace.file}", settings["Translators"])
    HBMToCGM2Mapper.calculate_missing_markers(acq_trial)
    # filter points and force plate #
    #################################
    low_pass_point_filtering(acq_trial)
    low_pass_force_plate_filtering(acq_trial)

    # detect gait events #
    ######################

    GaitEventDetectorFactory().get_zenis_detector().detect_events(acq_trial)
    out_file = namespace.file.replace(".c3d", "_filtered_event.c3d")
    btkTools.smartWriter(acq_trial, f"{namespace.path}{out_file}")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
