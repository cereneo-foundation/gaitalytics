from btk import btkAcquisition
from pyCGM2 import enums
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Lib.CGM import cgm2_5


def fit_trial_to_model(acq_trial: btkAcquisition,
                       acq_calc: btkAcquisition,
                       data_path: str,
                       trial_file_name: str,
                       static_file_name: str,
                       settings: list,
                       body_weight: float,
                       body_height: int) -> bool:
    # calibration options from settings
    left_flat_foot = settings["Calibration"]["Left flat foot"]
    right_flat_foot = settings["Calibration"]["Right flat foot"]
    head_flat = settings["Calibration"]["Head flat"]
    translators = settings["Translators"]
    marker_diameter = settings["Global"]["Marker diameter"]
    hjc = settings["Calibration"]["HJC"]
    point_suffix = settings["Global"]["Point suffix"]
    marker_weight = settings["Fitting"]["Weight"]
    moment_projection = settings["Fitting"]["Moment Projection"]
    # anthropometric parameters
    required_mp = dict()
    required_mp["Bodymass"] = body_weight
    required_mp["Height"] = body_height
    required_mp["LeftLegLength"] = 0
    required_mp["LeftKneeWidth"] = 0
    required_mp["RightLegLength"] = 0
    required_mp["RightKneeWidth"] = 0
    required_mp["LeftAnkleWidth"] = 0
    required_mp["RightAnkleWidth"] = 0
    required_mp["LeftSoleDelta"] = 0
    required_mp["RightSoleDelta"] = 0
    required_mp["LeftShoulderOffset"] = 0
    required_mp["LeftElbowWidth"] = 0
    required_mp["LeftWristWidth"] = 0
    required_mp["LeftHandThickness"] = 0
    required_mp["RightShoulderOffset"] = 0
    required_mp["RightElbowWidth"] = 0
    required_mp["RightWristWidth"] = 0
    required_mp["RightHandThickness"] = 0

    optional_mp = dict()
    optional_mp["InterAsisDistance"] = 0
    optional_mp["LeftAsisTrocanterDistance"] = 0
    optional_mp["LeftTibialTorsion"] = 0
    optional_mp["LeftThighRotation"] = 0
    optional_mp["LeftShankRotation"] = 0
    optional_mp["RightAsisTrocanterDistance"] = 0
    optional_mp["RightTibialTorsion"] = 0
    optional_mp["RightThighRotation"] = 0
    optional_mp["RightShankRotation"] = 0
    ##
    # calibrate function
    model, final_acq_static, error = cgm2_5.calibrate(data_path,
                                                      static_file_name,
                                                      translators,
                                                      marker_weight,
                                                      required_mp,
                                                      optional_mp,
                                                      True,
                                                      left_flat_foot,
                                                      right_flat_foot,
                                                      head_flat,
                                                      marker_diameter,
                                                      hjc,
                                                      point_suffix,
                                                      forceBtkAcq=acq_calc)

    moment_projection_enums = enums.enumFromtext(moment_projection, enums.MomentProjection)
    matching_food_side_on = forceplates.matchingFootSideOnForceplate(acq_trial)
    # detect correct foot contact with a force plate
    ###
    # fitting function

    acq_trial, anomaly_detected = cgm2_5.fitting(model, data_path, trial_file_name,
                                                 translators,
                                                 marker_weight,
                                                 True,
                                                 marker_diameter,
                                                 point_suffix,
                                                 matching_food_side_on,
                                                 moment_projection_enums,
                                                 frameInit=None,
                                                 frameEnd=None,
                                                 forceBtkAcq=acq_trial)
    return anomaly_detected
