from btk import btkAcquisition, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from pyCGM2.Tools import btkTools
import numpy as np


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


def calculate_weight_from_part(static_file_name: str, data_path: str) -> float:
    acq_static = btkTools.smartReader(f"{data_path}{static_file_name}")
    wl = np.mean(acq_static.GetAnalogs().GetItem(2).GetValues())
    wr = np.mean(acq_static.GetAnalogs().GetItem(8).GetValues())
    return np.abs((wl + wr) / 9.81)

