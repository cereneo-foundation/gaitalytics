from gaitalytics import api
from gaitalytics import utils


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Cereneo_FP_23_Int_01.3.c3d"
    out_path = "./test/data/"

    # load configs
    configs = utils.ConfigProvider(settings_file)

    api.detect_gait_events(file_path, out_path, configs, show_plot=True)


if __name__ == "__main__":
    main()
