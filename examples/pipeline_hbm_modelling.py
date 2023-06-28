from gaitalytics import utils, c3d, modelling


def main():
    settings_file = "settings/hbm_pig.yaml"
    file_path = "./test/data/Baseline.4.c3d"
    out_path = "./test/data/Baseline.5.c3d"

    # load configs
    configs = utils.ConfigProvider(settings_file)

    # read c3d
    acq_trial = c3d.read_btk(file_path)
    com_modeller = modelling.COMModeller(configs)
    com_modeller.create_point(acq_trial)
    subject = utils.extract_subject(acq_trial)
    cmos_modeller = modelling.CMoSModeller("Left", configs, subject.left_leg_length, 1.3)
    cmos_modeller.create_point(acq_trial)
    cmos_modeller = modelling.CMoSModeller("Right", configs, subject.left_leg_length, 1.3)
    cmos_modeller.create_point(acq_trial)
    c3d.write_btk(acq_trial, out_path)


if __name__ == "__main__":
    main()
