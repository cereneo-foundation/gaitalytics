## get anthropo information from a c3d file with
# PiG marker name
import numpy as np


def get_anthropo_info(acq_calib):

    # Weight
    FP1 = acq_calib.GetAnalog("Force.Fz1").GetValues()
    FP2 = acq_calib.GetAnalog("Force.Fz2").GetValues()
    weight = np.abs((np.mean(FP1[:100]) + np.mean(FP2[:100])) / 9.81)

    # Height from "CLAV" marker position
    Clav_z = acq_calib.GetPoint("CLAV").GetValues()[:, 2]
    height = np.mean(Clav_z[:100] + 300)

    # Left leg length
    LASI = acq_calib.GetPoint("LASI").GetValues()[:, 2]
    LLM = acq_calib.GetPoint("LLM").GetValues()[:, 2]
    left_leg_length = np.mean(LASI[:100]) - np.mean(LLM[:100])

    # Right leg length
    RASI = acq_calib.GetPoint("RASI").GetValues()[:, 2]
    RLM = acq_calib.GetPoint("RLM").GetValues()[:, 2]
    right_leg_length = np.mean(RASI[:100]) - np.mean(RLM[:100])

    # Left Knee
    LMEK = acq_calib.GetPoint("LMEK").GetValues()[:, 0]
    LLEK = acq_calib.GetPoint("LLEK").GetValues()[:, 0]
    left_knee_width = np.abs(np.mean(LMEK[:100]) - np.mean(LLEK[:100]))

    # Right Knee
    RMEK = acq_calib.GetPoint("RMEK").GetValues()[:, 0]
    RLEK = acq_calib.GetPoint("RLEK").GetValues()[:, 0]
    right_knee_width = np.abs(np.mean(RMEK[:100]) - np.mean(RLEK[:100]))

    # Left ankle
    LLM = acq_calib.GetPoint("LLM").GetValues()[:, 0]
    LMM = acq_calib.GetPoint("LMM").GetValues()[:, 0]
    left_ankle_width = np.abs(np.mean(LLM[:100]) - np.mean(LMM[:100]))

    # Right ankle
    RLM = acq_calib.GetPoint("RLM").GetValues()[:, 0]
    RMM = acq_calib.GetPoint("RMM").GetValues()[:, 0]
    right_ankle_width = np.abs(np.mean(RLM[:100]) - np.mean(RMM[:100]))

    anthropo_info = {"Weight":weight,
                     "Height": height,
                     "Left Leg Length":left_leg_length,
                     "Left Knee Width": left_knee_width,
                     "Left Ankle Width": left_ankle_width,
                     "Right Leg Length":right_leg_length,
                     "Right Knee Width":right_knee_width,
                     "Right Ankle Width":right_ankle_width}
    return anthropo_info


def make_translator_PiG():
    markerNamesHBM = ['LASIS', 'RASIS', 'LPSIS', 'RPSIS', 'LLTHI', 'LLEK', 'LMEK', 'LLSHA',
                      'LLM', 'LMM', 'LMT2', 'RLTHI', 'RLEK', 'RMEK', 'RLSHA',
                      'RLM', 'RMM', 'RMT2', 'XIPH', 'JN']

    markerNamesPiG = ['LASI', 'RASI', 'LPSI', 'RPSI', 'LTHI', 'LKNE', 'LKNEM', 'LTIB',
                      'LANK', 'LANKM', 'LTOE', 'RTHI', 'RKNE', 'RKNEM', 'RTIB',
                      'RANK', 'RANKM', 'RTOE', 'STRN', 'CLAV']

    translator = {}

    for i in range(len(markerNamesHBM)):
        translator[markerNamesPiG[i]] = markerNamesHBM[i]
    return translator