from src.gaitalytics import api
from src.gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.4.c3d"
    buffered_path = "./out"

    configs = utils.ConfigProvider(settings_file)

    cycle_data = api.extract_cycles(file_path, configs, buffer_output_path=buffered_path)
    api.normalise_cycles(file_path, cycle_data, buffer_output_path=buffered_path)


# __name__
if __name__ == "__main__":
    main()
