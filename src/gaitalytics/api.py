from __future__ import annotations

import logging
import os
import sys
from typing import Dict, List

from pandas import DataFrame

import gaitalytics.analysis
import gaitalytics.files
import gaitalytics.cycle
import gaitalytics.events
import gaitalytics.modelling
import gaitalytics.utils

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

# constants
CYCLE_METHOD_HEEL_STRIKE = "HS"
CYCLE_METHOD_TOE_OFF = "TO"

NORMALISE_METHODE_LINEAR = "linear"
NORMALISE_METHODE_LIST = (NORMALISE_METHODE_LINEAR)

GAIT_EVENT_METHODE_MARKER = "Marker"
GAIT_EVENT_METHODE_FP = "Forceplate"
GAIT_EVENT_METHODE_LIST = (GAIT_EVENT_METHODE_MARKER, GAIT_EVENT_METHODE_FP)

GAIT_EVENT_CHECKER_CONTEXT = "context"
GAIT_EVENT_CHECKER_SPACING = "spacing"
GAIT_EVENT_CHECKER_LIST = (GAIT_EVENT_CHECKER_CONTEXT, GAIT_EVENT_CHECKER_SPACING)

ANALYSIS_MOMENTS = "moments"
ANALYSIS_ANGLES = "angles"
ANALYSIS_POWERS = "powers"
ANALYSIS_FORCES = "forces"
ANALYSIS_TOE_CLEARANCE = "toe_clearance"
ANALYSIS_SPATIO_TEMP = "spatiotemporal"
ANALYSIS_CMOS = "cmos"
ANALYSIS_MOS = "mos"
ANALYSIS_LIST = (ANALYSIS_MOMENTS,
                 ANALYSIS_ANGLES,
                 ANALYSIS_POWERS,
                 ANALYSIS_FORCES,
                 ANALYSIS_SPATIO_TEMP,
                 ANALYSIS_TOE_CLEARANCE,
                 ANALYSIS_CMOS)

MODELLING_COM = "com"
MODELLING_CMOS = "cmos"
MODELLING_XCOM = "xcom"
MODELLING_LIST = [MODELLING_COM,
                  MODELLING_CMOS,
                  MODELLING_XCOM]


def analyse_data(cycle_data: Dict[str, gaitalytics.utils.BasicCyclePoint],
                 config: gaitalytics.utils.ConfigProvider,
                 methode: List[str] = ANALYSIS_LIST, **kwargs: dict) -> DataFrame:
    """
    Runs specified analysis and concatenates into one Dataframe

    :param cycle_data: full length cycle data
    :param config: configs from marker and model mapping
    :param methode: list of methods
    :return: results of analysis
    """
    logger.info("analyse_data")
    if not all(item in ANALYSIS_LIST for item in methode):
        raise KeyError(f"{methode} are not a valid anomaly checker")

    methods: List[gaitalytics.analysis.AbstractAnalysis] = []
    if ANALYSIS_ANGLES in methode:
        methods.append(gaitalytics.analysis.JointAnglesCycleAnalysis(cycle_data, config))
    if ANALYSIS_MOMENTS in methode:
        methods.append(gaitalytics.analysis.JointMomentsCycleAnalysis(cycle_data, config))
    if ANALYSIS_POWERS in methode:
        methods.append(gaitalytics.analysis.JointPowerCycleAnalysis(cycle_data, config))
    if ANALYSIS_FORCES in methode:
        methods.append(gaitalytics.analysis.JointForcesCycleAnalysis(cycle_data, config))
    if ANALYSIS_SPATIO_TEMP in methode:
        methods.append(gaitalytics.analysis.SpatioTemporalAnalysis(cycle_data, config))
    if ANALYSIS_TOE_CLEARANCE in methode:
        methods.append(gaitalytics.analysis.MinimalClearingDifference(cycle_data, config))
    if ANALYSIS_CMOS in methode:
        methods.append(gaitalytics.analysis.CMosAnalysis(cycle_data, config))
    if ANALYSIS_MOS in methode:
        methods.append(gaitalytics.analysis.MosAnalysis(cycle_data, config))

    results = None
    for methode in methods:
        result = methode.analyse(**kwargs)
        if results is None:
            results = result
        else:
            results = results.merge(result, on=gaitalytics.utils.BasicCyclePoint.CYCLE_NUMBER)

    return results


def check_gait_event(c3d_file_path: str,
                     output_path: str,
                     anomaly_checker: List[str] = GAIT_EVENT_CHECKER_LIST):
    """
    Checks events additionally
    with given anomaly_checker method and saves it in output_path with '*_anomaly.txt' extension

    :param c3d_file_path: path of c3d file with modelled filtered data '.3.c3d'
    :param output_path: path to dir to store c3d file with events
    :param anomaly_checker: list of anomaly checkers, "context" api.GAIT_EVENT_CHECKER_CONTEXT,
       "spacing" api.GAIT_EVENT_CHECKER_SPACING
    """
    logger.info("check_gait_event")
    if not os.path.isfile(c3d_file_path):
        raise FileExistsError(f"{c3d_file_path} does not exists")
    if not os.path.isdir(output_path):
        raise FileExistsError(f"{output_path} does not exists")
    if not all(item in GAIT_EVENT_CHECKER_LIST for item in anomaly_checker):
        raise KeyError(f"{anomaly_checker} are not a valid anomaly checker")
    # read c3d
    motion_file = gaitalytics.files.BtkFileHandler(c3d_file_path)
    # get anomaly detection
    checker = _get_anomaly_checker(anomaly_checker)
    detected, anomalies = checker.check_events(motion_file)

    # write anomalies to file
    if detected:
        filename = os.path.basename(c3d_file_path).replace(".4.c3d", "_anomalies.txt")
        out_path = os.path.join(output_path, filename)
        f = open(out_path, "w")
        for anomaly in anomalies:
            print(anomaly, file=f)
        f.close()


def detect_gait_events(c3d_file_path: str,
                       output_path: str,
                       configs: gaitalytics.utils.ConfigProvider,
                       methode: str = GAIT_EVENT_METHODE_MARKER,
                       anomaly_checker: List[str] = GAIT_EVENT_CHECKER_LIST, **kwargs):
    """
    Adds gait events to c3d file and saves it in output_path with a '.4.c3d' extension. Checks events aditionally
    with given anomaly_checker method and saves it in output_path with '*_anomaly.txt' extension

    :param c3d_file_path: path of c3d file with modelled filtered data '.3.c3d'
    :param output_path: path to dir to store c3d file with events
    :param configs: configs from marker and model mapping
    :param methode: methode to detect events 'Marker' api.GAIT_EVENT_METHODE_MARKER or
        'Forceplate' api.GAIT_EVENT_METHODE_FP
    :param anomaly_checker: list of anomaly checkers, "context" api.GAIT_EVENT_CHECKER_CONTEXT,
        "spacing" api.GAIT_EVENT_CHECKER_SPACING
    """
    logger.info("detect_gait_events")
    if not os.path.isfile(c3d_file_path):
        raise FileExistsError(f"{c3d_file_path} does not exists")
    if not os.path.isdir(output_path):
        raise FileExistsError(f"{output_path} does not exists")
    if methode not in GAIT_EVENT_METHODE_LIST:
        raise KeyError(f"{methode} is not a valid methode")
    if not all(item in GAIT_EVENT_CHECKER_LIST for item in anomaly_checker):
        raise KeyError(f"{anomaly_checker} are not a valid anomaly checker")

    # read c3d
    motion_file = gaitalytics.files.BtkFileHandler(c3d_file_path)

    # define output name
    filename = os.path.basename(c3d_file_path).replace(".3.c3d", ".4.c3d")
    out_path = os.path.join(output_path, filename)

    if methode == GAIT_EVENT_METHODE_FP:
        methode = gaitalytics.events.ForcePlateEventDetection()
    elif methode == GAIT_EVENT_METHODE_MARKER:
        methode = gaitalytics.events.ZenisGaitEventDetector(configs, **kwargs)

    methode.detect_events(motion_file, **kwargs)

    # write events c3d
    motion_file.write_file(out_path)


    check_gait_event(out_path, output_path)


def _get_anomaly_checker(anomaly_checker: List[str]) -> gaitalytics.events.AbstractEventAnomalyChecker:
    """
    defines checker by list of inputs

    :param anomaly_checker: list of checker name
    :return: checker object
    """
    logger.info("_get_anomaly_checker")
    checker = None
    if GAIT_EVENT_CHECKER_CONTEXT in anomaly_checker:
        checker = gaitalytics.events.ContextPatternChecker()
    if GAIT_EVENT_CHECKER_SPACING in anomaly_checker:
        checker = gaitalytics.events.EventSpacingChecker(checker)
    return checker


def extract_cycles_buffered(buffer_output_path: str,
                            configs: gaitalytics.utils.ConfigProvider) -> gaitalytics.cycle.CyclePointLoader:
    """
    gets normalised and full length data from buffered folder. It is needed to run api.extract_cycles as
    api.normalise_cycles with given buffer_output_path once to use this function

    :param buffer_output_path: path to folder
    :param configs: configs from marker and model mapping
    :return: object containing normalised and full length data lists
    """
    logger.info("extract_cycles_buffered")
    if not os.path.isdir(buffer_output_path):
        raise FileExistsError(f"{buffer_output_path} does not exists")

    # load cycles
    loader = gaitalytics.cycle.CyclePointLoader(configs, buffer_output_path)
    return loader


def extract_cycles(c3d_file_path: str,
                   configs: gaitalytics.utils.ConfigProvider,
                   methode: str = CYCLE_METHOD_HEEL_STRIKE,
                   buffer_output_path: str = None,
                   anomaly_checker: List[str] = GAIT_EVENT_CHECKER_LIST) -> \
        Dict[str, gaitalytics.utils.BasicCyclePoint]:
    """
    extracts and returns cycles from c3d. If a buffered path is delivered data will be stored in the path in separated
    csv file. Do not edit files and structure.

    :param c3d_file_path: path of c3d file with foot_off and foot_strike events '*.4.c3d'
    :param configs: configs from marker and model mapping
    :param methode: method to cut gait cycles either "HS" api.CYCLE_METHOD_HEEL_STRIKE or "TO" api.CYCLE_METHOD_TOE_OFF
    :param buffer_output_path: if buffering needed path to folder
    :param anomaly_checker: list of anomaly checkers, "context" api.GAIT_EVENT_CHECKER_CONTEXT,
        "spacing" api.GAIT_EVENT_CHECKER_SPACING
    :return: extracted gait cycles
    """
    logger.info("extract_cycles")
    # check params for validity
    if not os.path.isfile(c3d_file_path):
        raise FileExistsError(f"{c3d_file_path} does not exists")
    if methode not in [CYCLE_METHOD_HEEL_STRIKE, CYCLE_METHOD_TOE_OFF]:
        raise KeyError(f"{methode} is not a valid methode")
    if buffer_output_path:
        if not os.path.isdir(buffer_output_path):
            raise FileExistsError(f"{buffer_output_path} does not exists")
    if not all(item in GAIT_EVENT_CHECKER_LIST for item in anomaly_checker):
        raise KeyError(f"{anomaly_checker} are not a valid anomaly checker")

    # read c3d
    motion_file = gaitalytics.c3d.BtkFileHandler(c3d_file_path)

    # get anomaly detection
    checker = _get_anomaly_checker(anomaly_checker)

    # choose cut method
    cycle_builder = None
    if methode == CYCLE_METHOD_TOE_OFF:
        cycle_builder = gaitalytics.cycle.ToeOffToToeOffCycleBuilder(checker)
    elif methode == CYCLE_METHOD_HEEL_STRIKE:
        cycle_builder = gaitalytics.cycle.HeelStrikeToHeelStrikeCycleBuilder(checker)

    # get cycles
    cycles = cycle_builder.build_cycles(motion_file.aqc)

    # extract cycles
    cycle_data = gaitalytics.cycle.CycleDataExtractor(configs).extract_data(cycles, motion_file.aqc)

    # buffer cycles
    if buffer_output_path:
        prefix = os.path.basename(c3d_file_path).replace(".4.c3d", "")
        _cycle_points_to_csv(cycle_data, buffer_output_path, prefix)

    return cycle_data


def normalise_cycles(c3d_file_path: str,
                     cycle_data: Dict[str, gaitalytics.utils.BasicCyclePoint],
                     method: str = NORMALISE_METHODE_LINEAR,
                     buffer_output_path: str = None) -> Dict[str, gaitalytics.utils.BasicCyclePoint]:
    """
    normalise and returns cycles

    :param c3d_file_path:  path of c3d file with foot_off and foot_strike events '*.4.c3d'
    :param cycle_data: full length cycle data
    :param method: method normalise "linear" api.NORMALISE_METHODE_LINEAR
    :param buffer_output_path: if buffering needed path to folder
    :return: normalised gait cycles
    """
    logger.info("normalise_cycles")
    # check params for validity
    if method not in NORMALISE_METHODE_LIST:
        raise KeyError(f"{method} is not a valid methode")
    if buffer_output_path:
        if not os.path.isdir(buffer_output_path):
            raise FileExistsError(f"{buffer_output_path} does not exists")

    # get method
    if method == NORMALISE_METHODE_LINEAR:
        method = gaitalytics.cycle.LinearTimeNormalisation()

    # normalise
    normalised_data = method.normalise(cycle_data)

    # buffer cycles
    if buffer_output_path:
        prefix = os.path.basename(c3d_file_path).replace(".4.c3d", "")
        _cycle_points_to_csv(normalised_data, buffer_output_path, prefix)

    return normalised_data


def model_data(c3d_file_path: str,
               output_path: str,
               configs: gaitalytics.utils.ConfigProvider,
               methode: str,
               **kwargs):
    """
    Models data according to chosen method and saves new c3d file in output path with '.5.c3d extension'

    :param c3d_file_path: path of c3d file with modelled filtered data '.3.c3d'
    :param output_path: path to dir to store c3d file with events
    :param configs: configs from marker and model mapping
    :param methode: methode to detect events
    :keyword belt_speed: belt speed
    """
    logger.info("model_data")
    if not methode in MODELLING_LIST:
        raise KeyError(f"{methode} is not a valid modelling methode")
    methods: List[gaitalytics.modelling.BaseOutputModeller] = []
    motion_file = gaitalytics.files.BtkFileHandler(c3d_file_path)
    subject = motion_file.get_subject_measures()
    if methode == MODELLING_CMOS:
        methods.append(gaitalytics.modelling.COMModeller(configs))
        methods.append(gaitalytics.modelling.XCOMModeller(configs))
        methods.append(gaitalytics.modelling.CMoSModeller(configs,
                                                          **kwargs))

    elif methode == MODELLING_XCOM:
        methods.append(gaitalytics.modelling.COMModeller(configs))
        methods.append(gaitalytics.modelling.XCOMModeller(configs))
    elif methode == MODELLING_COM:
        methods.append(gaitalytics.modelling.COMModeller(configs))

    for methode in methods:
        methode.create_point(motion_file, **kwargs)
    filename = os.path.basename(c3d_file_path)
    filename = filename.replace(".4.c3d", ".5.c3d")
    output_path = os.path.join(output_path, filename)
    motion_file.write_file(output_path)


def _cycle_points_to_csv(cycle_data: Dict[str, gaitalytics.utils.BasicCyclePoint], dir_path: str, prefix: str):
    logger.info("_cycle_points_to_csv")
    subject_saved = False
    for key in cycle_data:
        cycle_data[key].to_csv(dir_path, prefix)
        if not subject_saved:
            cycle_data[key].subject.to_file(dir_path)
