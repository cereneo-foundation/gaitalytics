import os

from gaitalytics import api
from gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.5.c3d"
    buffered_path = "./out"

    configs = utils.ConfigProvider(settings_file)
    if not os.path.exists(buffered_path):
        os.mkdir(buffered_path)
        cycle_data = api.extract_cycles(file_path, configs, buffer_output_path=buffered_path)
    else:
        cycle_data = api.extract_cycles_buffered(buffered_path,configs).get_raw_cycle_points()
    api.normalise_cycles(file_path, cycle_data, buffer_output_path=buffered_path)


# __name__
if __name__ == "__main__":
    main()
