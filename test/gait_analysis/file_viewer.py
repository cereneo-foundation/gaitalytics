from pyCGM2.Tools import btkTools
from pyCGM2.Utils import files


# This pipeline refactors gait event to a qtm suitable form
FILENAME = "test/data/1min.c3d"
SETTINGS_PATH = "settings/"
SETTINGS_FILE = "CGM2_5-pyCGM2.settings"


def main():
    settings = files.loadModelSettings(SETTINGS_PATH, SETTINGS_FILE)
    acq = btkTools.smartReader(FILENAME, settings["Translators"])
    xiph_point = acq.GetPoint("CLAV").Clone()
    xiph_point.SetLabel("XIPH")
    values = xiph_point.GetValues()
    values[:, 2] = values[:, 2] * 0.90
    values[:, 1] = values[:, 1] - 25
    xiph_point.SetValues(values)
    acq.AppendPoint(xiph_point)
    btkTools.smartWriter(acq, "test/data/1min_CGM_HBM.c3d")


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
