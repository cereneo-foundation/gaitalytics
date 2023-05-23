import numpy as np
from btk import btkAcquisition, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter


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


def detect_onset(x, threshold=0, n_above=1, n_below=0,
                 threshold2=None, n_above2=1, show=False, ax=None):
    """Detects onset in data based on amplitude threshold.
    """

    x = np.atleast_1d(x).astype('float64')
    # deal with NaN's (by definition, NaN's are not greater than threshold)
    x[np.isnan(x)] = -np.inf
    # indices of data greater than or equal to threshold
    inds = np.nonzero(x >= threshold)[0]
    if inds.size:
        # initial and final indexes of almost continuous data
        inds = np.vstack((inds[np.diff(np.hstack((-np.inf, inds))) > n_below + 1],
                          inds[np.diff(np.hstack((inds, np.inf))) > n_below + 1])).T
        # indexes of almost continuous data longer than or equal to n_above
        inds = inds[inds[:, 1] - inds[:, 0] >= n_above - 1, :]
        # minimum amplitude of n_above2 values in x to detect
        if threshold2 is not None and inds.size:
            idel = np.ones(inds.shape[0], dtype=bool)
            for i in range(inds.shape[0]):
                if np.count_nonzero(x[inds[i, 0]: inds[i, 1] + 1] >= threshold2) < n_above2:
                    idel[i] = False
            inds = inds[idel, :]
    if not inds.size:
        inds = np.array([])  # standardize inds shape for output

    return inds


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
