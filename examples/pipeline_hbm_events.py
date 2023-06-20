from gait_analysis import api, utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.3.c3d"
    out_path = "./test/data/"

    # load configs
    configs = utils.ConfigProvider(settings_file)

    api.detect_gait_events(file_path, out_path, configs)


if __name__ == "__main__":
    main()
