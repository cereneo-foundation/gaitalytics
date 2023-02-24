import os

from pyCGM2.Tools import btkTools
from PiGPipeline_SimonPlayground import SimonPipelineUtils


def make_PiG_conversion(DATA_PATH, SUBJECT, SESSIONS):
    translators = SimonPipelineUtils.make_translator_PiG()
    # traverse whole directory
    for sess in SESSIONS[:]:
        file_list = []
        for root, dirs, files_ in os.walk(DATA_PATH + SUBJECT + sess):
            # select file name
            for file in files_:
                # check the extension of files
                if file.endswith('.c3d') and ("PiG" not in file):
                    # print whole path of files
                    print(os.path.join(root, file))
                    file_list.append(os.path.join(root, file))

        for acquisition in file_list:

            acq_trial = btkTools.smartReader(acquisition, translators)
            save_name = acquisition[:-4] + "PiG.c3d"
            print(save_name)
            btkTools.smartWriter(acq_trial, save_name)

            if "Calib" in save_name:
                anthropo_info = SimonPipelineUtils.get_anthropo_info(acq_trial)

        for anthropo, value in anthropo_info.items():
            print(anthropo, ":", value)
    ##



