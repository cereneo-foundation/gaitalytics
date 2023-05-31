import os
import re
from argparse import ArgumentParser, Namespace

from gait_analysis.utils import c3d

from gait_analysis.cycle.builder import HeelStrikeToHeelStrikeCycleBuilder
from gait_analysis.event.anomaly import BasicContextChecker
from gait_analysis.cycle.normalisation import LinearTimeNormalisation
from gait_analysis.analysis.normalised import DescriptiveNormalisedAnalysis

SETTINGS_PATH = "settings/"
SETTINGS_FILE = "HBM_Trunk_cgm2.5.settings"
DATA_PATH = "C:/ViconData/Handshake/"


def get_args() -> Namespace:
    parser = ArgumentParser(description='Event Adder')
    parser.add_argument('--path', dest='path', type=str, help='Path to data')
    parser.add_argument('--file', dest='file', type=str, help='Trial file name')
    return parser.parse_args()


def main():
    for root, sub_folder, file_name in os.walk(DATA_PATH):
        r = re.compile("S0.*\.4\.c3d")
        filtered_files = list(filter(r.match, file_name))
        for filtered_file in filtered_files:
            filename = filtered_file.replace(".4.c3d", "_desc.csv")
            print(f"{root}/{filtered_file}")
            acq_trial = c3d.read_btk(f"{root}/{filtered_file}")

            cycle_builder = HeelStrikeToHeelStrikeCycleBuilder(BasicContextChecker())

            cycles = cycle_builder.build_cycles(acq_trial)
            normalised_data = LinearTimeNormalisation().normalise(acq_trial, cycles)
            desc_results = DescriptiveNormalisedAnalysis(normalised_data).analyse()

            desc_results.to_csv(f"out/{filename}", index=False)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
