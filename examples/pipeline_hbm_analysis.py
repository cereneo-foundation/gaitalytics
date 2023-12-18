import os

from gaitalytics import api
from gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    buffered_path = "./raw"
    out_path = "./spatio_temp"

    configs = utils.ConfigProvider(settings_file)

    loaded_cycles = api.extract_cycles_buffered(buffered_path, configs)
    cycle_data = loaded_cycles.get_raw_cycle_points()

    results = api.analyse_data(cycle_data, configs)

    if not os.path.exists(out_path):
        os.mkdir(out_path)
    results.to_csv(f"{out_path}/spatio_temp.csv")


if __name__ == "__main__":
    main()
