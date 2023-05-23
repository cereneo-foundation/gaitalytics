from abc import ABC, abstractmethod

import btk
import numpy as np
from btk import btkAcquisition, btkEvent
from pyCGM2.Signal import detect_onset
from pyCGM2.Tools import btkTools
from pyCGM2.Events.eventProcedures import ZeniProcedure
from gait_analysis.event.utils import GaitEventLabel
from gait_analysis.utils import utils, config, c3d
from scipy import signal

FORCE_PLATE_SIDE_MAPPING_CAREN = {"Left": 0, "Right": 1}


class AbstractGaitEventDetector(ABC):

    @abstractmethod
    def detect_events(self, acq: btkAcquisition):
        pass

    @staticmethod
    def clear_events(bkt_acq: btkAcquisition, event_names: list = None):
        """
        clears all events in acquisition

        :param bkt_acq: loaded acquisition
        :param event_names: List of event names to delete. None equals all
        """
        if event_names is None:
            bkt_acq.ClearEvents()
        else:
            btkTools.clearEvents(btkAcquisition, event_names)


class ZenisGaitEventDetector(AbstractGaitEventDetector):
    """
    This class detects gait events from cgm2 model data
    """

    def __init__(self, config: dict, foot_strike_offset: int = 0, foot_off_offset: int = 0):
        """ Initializes Object

        :param foot_strike_offset: numbers of frames to offset next foot strike event
        :param foot_off_offset: number of frames to offset next foot off event
        """
        self.config = config
        self._foot_strike_offset = foot_strike_offset
        self._foot_off_offset = foot_off_offset

    def detect_events(self, acq: btkAcquisition):
        """detects zeni gait events and stores it in to the acquisition

        :param acq: loaded and filtered acquisition
        """

        right_heel = acq.GetPoint(self.config[config.KEY_MARKER_MAPPING][config.KEY_MARKER_MAPPING_R_HEEL]).GetValues()
        left_heel = acq.GetPoint(self.config[config.KEY_MARKER_MAPPING][config.KEY_MARKER_MAPPING_L_HEEL]).GetValues()
        right_hip = acq.GetPoint(self.config[config.KEY_MARKER_MAPPING][config.KEY_MARKER_MAPPING_R_HIP]).GetValues()
        left_hip = acq.GetPoint(self.config[config.KEY_MARKER_MAPPING][config.KEY_MARKER_MAPPING_L_HIP]).GetValues()

        sacrum = (right_hip + left_hip) / 2.0
        right_diff_heel = right_heel - sacrum
        left_diff_heel = left_heel - sacrum
        right_diff_toe = right_heel - sacrum
        left_diff_toe = left_heel - sacrum

        l_heel_strike = find_peaks(left_diff_heel[c3d.AxesNames.X.value])
        r_heel_strike = find_peaks(right_diff_heel[c3d.AxesNames.X.value])
        l_toe_off = find_peaks(left_diff_toe[c3d.AxesNames.X.value])
        l_toe_off = find_peaks(left_diff_toe[c3d.AxesNames.X.value])

        # Find peaks(max).
        l_heel_strike = signal.argrelextrema(left_diff_heel[c3d.AxesNames.X.value], np.greater)
        l_heel_strike = l_heel_strike[0]

        r_heel_strike = signal.argrelextrema(right_diff_heel[c3d.AxesNames.X.value], np.greater)
        r_heel_strike = r_heel_strike[0]

        # Find valleys(min).
        l_toe_off = signal.argrelextrema(left_diff_toe[c3d.AxesNames.X.value], np.less)
        l_toe_off = l_toe_off[0]

        r_toe_off = signal.argrelextrema(right_diff_toe[c3d.AxesNames.X.value], np.less)
        r_toe_off = r_toe_off[0]

        events = acq.GetEvents()
        for toe_off in l_toe_off:
            ev = btkEvent(type_event, toe_off, 'Left', btkEvent.Automatic, '',
                          'event from Force plate assignment')
            btk_acq.AppendEvent(ev)




class ForcePlateEventDetection(AbstractGaitEventDetector):
    """
    This class detects gait events from Force Plate signals
    """

    def __init__(self, mapped_force_plate: dict = FORCE_PLATE_SIDE_MAPPING_CAREN,
                 force_gait_event_threshold: int = 150):
        """
        Initializes Object
        :param mapped_force_plate: Dictionary with name of force plate and index
        :param force_gait_event_threshold: threshold in newton to define gait event
        """

        self._mapped_force_plate = mapped_force_plate
        self._weight_threshold = force_gait_event_threshold

    def detect_events(self, acq: btkAcquisition):
        """
        Detect force plate gait events with peak detection
        :param acq: loaded and filtered acquisition
        """
        point_frequency = acq.GetPointFrequency()

        for side_name in self._mapped_force_plate.keys():
            force_down_sample = utils.force_plate_down_sample(acq, self._mapped_force_plate[side_name])
            detection = detect_onset.detect_onset(force_down_sample, threshold=self._weight_threshold)
            sequence = self._detect_gait_event_type(force_down_sample, detection)
            self._store_force_plate_events(acq, side_name, point_frequency, sequence)

    @staticmethod
    def _store_force_plate_events(btk_acq, side_name, point_frequency, sequence):
        for elem in sequence:
            type_event = elem[0]
            index_event = elem[1]

            ev = btkEvent(type_event, (index_event - 1) / point_frequency, side_name, btkEvent.Automatic, '',
                          'event from Force plate assignment')
            btk_acq.AppendEvent(ev)

    @staticmethod
    def _detect_gait_event_type(force_plate_signal: numpy.ndarray, detected_force_plate_events: numpy.ndarray) -> list:
        """
        Iterate through each event detected by detect_onset and determine if the event is a FootStrike or a FootOff.
        Return array of ["Type of event":str,index of event:int]
        :param force_plate_signal: Signal of the force plate
        :param detected_force_plate_events: detection from detect_onset
        :return: 2 dimensional array with event name and frame index
        """
        # Sophie was here !!! :D

        signal_length = len(force_plate_signal)
        detected_event_types = []
        for couple_index in detected_force_plate_events:
            for signal_index in couple_index:

                # check for index out of bound
                if 20 < signal_index < (signal_length - 20):

                    # positive or negative slope (FeetOff or FeetStrike)
                    diff = force_plate_signal[signal_index - 20] - force_plate_signal[signal_index + 20]
                    if diff > 0:
                        detected_event_types.append([GaitEventLabel.FOOT_OFF.value, signal_index])
                    else:
                        detected_event_types.append([GaitEventLabel.FOOT_STRIKE.value, signal_index])
        return detected_event_types  # Contain the label of the event and the corresponding index
