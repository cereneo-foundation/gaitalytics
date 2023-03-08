import numpy as np
from enum import Enum
from btk import btkAcquisition, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from pyCGM2.Tools import btkTools


class SideEnum(Enum):
    """
    Helper enum to define side
    """
    LEFT = "L"
    RIGHT = "R"


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



def correct_points_frame_by_frame(acq_trial: btkAcquisition):
    frame_size = acq_trial.GetPointFrameNumber()
    correction = get_fastest_point_by_frame(acq_trial, 1)
    for frame_number in range(1, frame_size):
        if (frame_number + 2) < frame_size:
            correction_new = get_fastest_point_by_frame(acq_trial, frame_number + 1)
        correct_points_in_frame(acq_trial, frame_number, correction)
        correction += correction_new


def correct_points_in_frame(acq_trial: btkAcquisition, frame_number: int, correction: float):
    print(f"{frame_number}:{correction}")
    for point_number in range(0, acq_trial.GetPointNumber()):
        acq_trial.GetPoint(point_number).SetValue(frame_number, 1,
                                                  (acq_trial.GetPoint(point_number).GetValue(frame_number,
                                                                                             1) + correction))


def get_fastest_point_by_frame(acq_trial, frame_number) -> float:
    rfmh_point = acq_trial.GetPoint("RFMH")
    rhee_point = acq_trial.GetPoint("RHEE")
    lfmh_point = acq_trial.GetPoint("LFMH")
    lhee_point = acq_trial.GetPoint("LHEE")
    lfmh_dist = lfmh_point.GetValue(frame_number - 1, 1) - lfmh_point.GetValue(frame_number, 1)
    lhee_dist = lhee_point.GetValue(frame_number - 1, 1) - lhee_point.GetValue(frame_number, 1)
    rfmh_dist = rfmh_point.GetValue(frame_number - 1, 1) - rfmh_point.GetValue(frame_number, 1)
    rhee_dist = rhee_point.GetValue(frame_number - 1, 1) - rhee_point.GetValue(frame_number, 1)
    return np.min([lfmh_dist, lhee_dist, rfmh_dist, rhee_dist])


def return_max_length(arrays):
    return len(max(arrays, key=len))


def tolerant_mean(arrs):
    lens = [len(i) for i in arrs]
    arr = np.ma.empty((np.max(lens), len(arrs)))
    arr.mask = True
    for idx, l in enumerate(arrs):
        arr[:len(l), idx] = l
    return arr.mean(axis=-1), arr.std(axis=-1)


def create_matrix_padded(matrix, max_length):
    matx = []
    lin_array = len(np.shape(matrix[0])) == 1
    for array in matrix:
        to_pad = max_length - len(array)
        if lin_array:
            array_pad = np.pad(array, (0, to_pad), 'constant', constant_values=0)
        else:
            array_pad = np.pad(array[:, 0], (0, to_pad), 'constant', constant_values=0)
        matx.append(array_pad)
    return matx
