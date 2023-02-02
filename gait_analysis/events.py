from abc import ABC, abstractmethod

import numpy
from btk import btkAcquisition, btkEvent, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from pyCGM2.Events import eventFilters, eventProcedures
from pyCGM2.Signal import detect_onset
from gait_analysis import utils
from pyCGM2.Tools import btkTools

FORCE_PLATE_SIDE_MAPPING_CAREN = {"Left": 0, "Right": 1}
GAIT_EVENT_FOOT_STRIKE = "Foot Strike"
GAIT_EVENT_FOOT_OFF = "Foot Off"

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

    def __init__(self, foot_strike_offset: int = 0, foot_off_offset: int = 0):
        """ Initializes Object

        :param foot_strike_offset: numbers of frames to offset next foot strike event
        :param foot_off_offset: number of frames to offset next foot off event
        """

        self._foot_strike_offset = foot_strike_offset
        self._foot_off_offset = foot_off_offset

    def detect_events(self, acq: btkAcquisition):
        """detects zeni gait events and stores it in to the acquisition

        :param acq: loaded and filtered acquisition
        """

        evp = eventProcedures.ZeniProcedure()
        evp.setFootStrikeOffset(self._foot_strike_offset)
        evp.setFootOffOffset(self._foot_off_offset)

        # event filter
        evf = eventFilters.EventFilter(evp, acq)
        evf.detect()
        state = evf.getState()


class ForcePlateEventDetection(AbstractGaitEventDetector):
    """
    This class detects gait events from Force Plate signals
    """

    def __init__(self, mapped_force_plate: dict = FORCE_PLATE_SIDE_MAPPING_CAREN, force_gait_event_threshold: int = 10):
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

        signal_length = len(force_plate_signal)
        detected_event_types = []
        for couple_index in detected_force_plate_events:
            for signal_index in couple_index:

                # check for index out of bound
                if 20 < signal_index < (signal_length - 20):

                    # positive or negative slope (FeetOff or FeetStrike)
                    diff = force_plate_signal[signal_index - 20] - force_plate_signal[signal_index + 20]
                    if diff > 0:
                        detected_event_types.append(["Foot Off", signal_index])
                    else:
                        detected_event_types.append(["Foot Strike", signal_index])
        return detected_event_types  # Contain the label of the event and the corresponding index


class GaitEventDetectorFactory(object):

    def __init__(self):
        self._zenis = None
        self._force_plate = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GaitEventDetectorFactory, cls).__new__(cls)
        return cls.instance

    def get_zenis_detector(self) -> AbstractGaitEventDetector:
        if self._zenis is None:
            self._zenis = ZenisGaitEventDetector()
        return self._zenis

    def get_force_plate_detector(self) -> AbstractGaitEventDetector:
        if self._force_plate is None:
            self._force_plate = ForcePlateEventDetection()
        return self._force_plate
