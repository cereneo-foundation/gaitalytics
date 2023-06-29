from gaitalytics import api
from gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    buffered_path = "./out"

    configs = utils.ConfigProvider(settings_file)

    loaded_cycles = api.extract_cycles_buffered(buffered_path, configs)
    cycle_data = loaded_cycles.get_raw_cycle_points()

    results = api.analyse_data(cycle_data, configs, methode=[api.ANALYSIS_MOS])
    results.to_csv("plots/nice.csv")


if __name__ == "__main__":
    main()
