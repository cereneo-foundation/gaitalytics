import numpy as np
from btk import btkAcquisition, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from pyCGM2.Tools import btkTools


def get_marker_names(acq: btkAcquisition) -> list:
    """
    Returns marker names
    :param acq: loaded acquisition
    :return: all marker names contained in acquisition
    """
    marker_names = []
    i = acq.BeginPoint()
    while i != acq.EndPoint():
        marker_names.append(i.value().GetLabel())
        i.incr()
    return marker_names


def force_plate_down_sample(acq: btkAcquisition, force_plate_index: int) -> list:
    first_frame_index = acq.GetFirstFrame()
    last_frame_index = acq.GetLastFrame()
    analog_sample_per_frame = acq.GetNumberAnalogSamplePerFrame()

    force_plate_extractor = btkForcePlatformsExtractor()
    ground_reaction_filter = btkGroundReactionWrenchFilter()

    force_plate_extractor.SetInput(acq)
    force_plate_collection = force_plate_extractor.GetOutput()
    ground_reaction_filter.SetInput(force_plate_collection)
    ground_reaction_collection = ground_reaction_filter.GetOutput()
    ground_reaction_collection.Update()
    force = ground_reaction_collection.GetItem(force_plate_index).GetForce().GetValues()
    return force[0:(last_frame_index - first_frame_index + 1) * analog_sample_per_frame:analog_sample_per_frame][:, 2]


def calculate_height_from_markers(acq_calc: btkAcquisition) -> int:
    try:
        return int(round(np.mean(acq_calc.GetPoint("GLAB").GetValues()[:, 2])) * 1.005)
        # TODO need a nice factor to determine height from forehead
    except RuntimeError:
        # I no GLAB use t2
        return int(round(np.mean(acq_calc.GetPoint("GLAB").GetValues()[:, 2])) * 1.05)
        # TODO need a nice factor to determine height from forehead


def calculate_height_from_markers_file(static_file_name: str, data_path: str) -> int:
    acq_calc = btkTools.smartReader(f"{data_path}{static_file_name}")
    return calculate_height_from_markers(acq_calc)


def calculate_weight_from_force_plates_file(static_file_name: str, data_path: str) -> float:
    acq_calc = btkTools.smartReader(f"{data_path}{static_file_name}")
    return calculate_weight_from_force_plates(acq_calc)


def calculate_weight_from_force_plates(acq_calc: btkAcquisition) -> float:
    wl = np.mean(acq_calc.GetAnalogs().GetItem(2).GetValues())
    wr = np.mean(acq_calc.GetAnalogs().GetItem(8).GetValues())
    return np.abs((wl + wr) / 9.81)


def correct_points(acq_trial: btkAcquisition, treadmill_speed: float):
    for i in range(0, acq_trial.GetPointNumber()):
        for frame_i in range(0, acq_trial.GetPointFrameNumber() - 1):
            acq_trial.GetPoint(i).SetValue(frame_i, 1, acq_trial.GetPoint(i).GetValues()[frame_i, 1] - (
                    frame_i * treadmill_speed))


def calculate_treadmill_speed(acq_trial: btkAcquisition) -> float:
    # TODO clean up please abo
    rhee = acq_trial.GetPoint("RHEE")
    lhee = acq_trial.GetPoint("LHEE")
    speeds = []
    stride_time = []
    stride_dist = []
    start_y = 0
    start_frame = 0
    for i in range(0, (acq_trial.GetEvents().GetItemNumber() - 1)):
        event = acq_trial.GetEvent(i)
        if event.GetContext() == "Right":
            if event.GetLabel() == "Foot Strike":
                start_frame = event.GetFrame()
                start_y = rhee.GetValue(event.GetFrame(), 1)
            else:
                end_frame = event.GetFrame()
                end_y = rhee.GetValue(event.GetFrame(), 1)
                time_passed = (end_frame - start_frame)
                dist = np.abs(start_y - end_y)
                stride_dist.append(dist)
                stride_time.append(time_passed)
                speeds.append(dist / time_passed)
    return np.mean(speeds)
