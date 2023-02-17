from btk import btkAcquisition
from pyCGM2.Signal import signal_processing
from gait_analysis.utils import get_marker_names
import numpy as np


def low_pass_point_filtering(acq: btkAcquisition, filter_frequency: int = 15, filter_order=2, markers_to_filter: list = []):
    """ filters defined markers with low pass filter

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


def low_pass_force_plate_filtering(acq: btkAcquisition, filter_frequency: int = 5, filter_order=4):
    """ filters defined marker with low pass filter

    :param acq: loaded acquisition
    :param filter_frequency: threshold frequency
    :param filter_order: filter order
    :return:
    """
    signal_processing.forcePlateFiltering(acq, order=filter_order, fc=filter_frequency)


def band_pass_filter_emg(acq: btkAcquisition, emg_label: str, frequency_high: int = 10,
                         frequency_low: int = 400):
    """
    Band-pass filter and EMG pre-processing

    :param acq: EMG raw acquisition
    :param emg_label: Voltage channel for EMG analog to be filtered
    :param frequency_high: high-pass frequency
    :param frequency_low: low-pass frequency
    :return:
    """
    x = acq.GetAnalog(emg_label).GetValues()  # get EMG data as array from c3d file
    x -= np.mean(x)

    # Frequency filtering
    acq_filtered = signal_processing.highPass(array=x, lowerFreq=frequency_low, upperFreq=frequency_high, fa=acq.GetAnalogFrequency())

    # EMG Rectification
    acq.GetAnalog(emg_label).SetData(signal_processing.rectify(acq_filtered))
