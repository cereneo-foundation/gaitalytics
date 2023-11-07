import os

from gaitalytics import api
from gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.5.c3d"
    buffered_path_raw = "./raw"
    buffered_path_norm = "./norm"

    configs = utils.ConfigProvider(settings_file)
    if not os.path.exists(buffered_path_raw):
        os.mkdir(buffered_path_raw)
        cycle_data = api.extract_cycles(file_path, configs, buffer_output_path=buffered_path_raw)
    else:
        cycle_data = api.extract_cycles_buffered(buffered_path_raw, configs).get_raw_cycle_points()

    if not os.path.exists(buffered_path_norm):
        os.mkdir(buffered_path_norm)
    api.normalise_cycles(file_path, cycle_data, buffer_output_path=buffered_path_norm)


# __name__
if __name__ == "__main__":
    main()
