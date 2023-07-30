from gaitalytics import utils, api


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.4.c3d"
    out_path = "./test/data/"

    # load configs
    configs = utils.ConfigProvider(settings_file)

    api.model_data(file_path, out_path, configs, methode=api.MODELLING_CMOS, belt_speed=0.8, dominant_leg_length=998, show_plot = True)


if __name__ == "__main__":
    main()
