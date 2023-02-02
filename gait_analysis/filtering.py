from btk import btkAcquisition
from pyCGM2.Signal import signal_processing
from gait_analysis.utils import get_marker_names


def low_pass_filtering(acq: btkAcquisition, filter_frequency: int = 15, filter_order=2, markers_to_filter: list = []):
    """ filters defined marker with low pass filter

    :param acq: loaded acquisition
    :param markers_to_filter: list of marker names to filter. if empty all markers
    :param filter_frequency: threshold frequency
    :param filter_order: filter order
    :return:
    """
    if not markers_to_filter:
        markers_to_filter = get_marker_names(acq)

    signal_processing.markerFiltering(
        acq, markers_to_filter, order=filter_order, fc=filter_frequency)
