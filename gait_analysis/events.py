from abc import ABC, abstractmethod

import numpy
from btk import btkAcquisition, btkEvent
from pyCGM2.Events import eventFilters, eventProcedures
from pyCGM2.Signal import detect_onset
from pyCGM2.Tools import btkTools

from gait_analysis import utils
from gait_analysis.utils.c3d import GAIT_EVENT_FOOT_STRIKE, GAIT_EVENT_FOOT_OFF

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


class EventAnomalyChecker(ABC):
    """
    Queued Events anomaly checker framework. Calls checker in a defined sequence
    """

    """
    Initiate instance and adds event_checker as callable child.
    :param event_checker: Subclass of EventAnomalyChecker
    """

    def __init__(self, event_checker=None):
        self.child = event_checker

    """
    Calls event anomaly checker of subclass and its children in sequences
    :param acq_walk: Acquisition with predefined events
    """

    def check_events(self, acq_walk: btkAcquisition) -> [bool, list]:
        abnormal_event_frames = []
        [anomaly_detected, abnormal_event_frames] = self._check_events(acq_walk, abnormal_event_frames)
        if self.child is not None:
            [child_anomaly_detected, child_abnormal_event_frames] = self.child.check_events(acq_walk)

            abnormal_event_frames.extend(child_abnormal_event_frames)
            anomaly_detected = child_anomaly_detected | anomaly_detected
        return anomaly_detected, abnormal_event_frames

    """
    Implementation of event checker
    :param acq_walk: Acquisition with added Events
    :param abnormal_event_frames: list of found already found anomalies
    :return: flag is anomalies found, list of anomalies
    """

    def _check_events(self, acq_walk: btkAcquisition, abnormal_event_frames: list) -> [bool, list]:
        pass


class EventNormalSequencePerContextChecker(EventAnomalyChecker):
    """
    Checks if events are alternating between Heel_Strike and Foot_Off per context
    :param acq_walk: Acquisition with added Events
    :param abnormal_event_frames: list of found already found anomalies
    :return: flag is anomalies found, list of anomalies
    """

    def _check_events(self, acq_walk: btkAcquisition, abnormal_event_frames: list) -> [bool, list]:
        abnormal_event_frames = []
        anomaly_detected = False

        btkTools.sortedEvents(acq_walk)

        for current_event_index in range(0, acq_walk.GetEventNumber()):
            current_event = acq_walk.GetEvent(current_event_index)
            context = current_event.GetContext()
            for next_event_index in range(current_event_index + 1, acq_walk.GetEventNumber()):
                next_event = acq_walk.GetEvent(next_event_index)
                if next_event.GetContext() == context:
                    if current_event.GetLabel() == next_event.GetLabel():
                        anomaly_detected = True
                        abnormal_event_frames.append({"Context": context, "Start-Frame": current_event.GetFrame(),
                                                      "End-Frame": next_event.GetFrame(),
                                                      "Anomaly": "Normal Per Context Sequence"})
                    break

        return [anomaly_detected, abnormal_event_frames]


class EventNormalSequenceInterContextChecker(EventAnomalyChecker):
    """
    Checks if events sequence LEFT, LEFT, RIGHT, RIGHT
    :param acq_walk: Acquisition with added Events
    :param abnormal_event_frames: list of found already found anomalies
    :return: flag is anomalies found, list of anomalies
    """

    def _check_events(self, acq_walk: btkAcquisition, abnormal_event_frames: list) -> [bool, list]:
        abnormal_event_frames = []
        anomaly_detected = False

        btkTools.sortedEvents(acq_walk)

        for current_event_index in range(0, acq_walk.GetEventNumber()):
            current_event = acq_walk.GetEvent(current_event_index)
            print("")
            print(f"Curr Frame: {current_event.GetFrame()} {current_event.GetContext()} {current_event.GetLabel()}")

            current_label = current_event.GetLabel()

            if current_label == GAIT_EVENT_FOOT_OFF:
                [anomaly_detected, abnormal_event_frames] = self._check_foot_off(acq_walk, current_event,
                                                                                 abnormal_event_frames,
                                                                                 current_event_index)
            elif current_label == GAIT_EVENT_FOOT_STRIKE:
                [anomaly_detected, abnormal_event_frames] = self._check_foot_strike(acq_walk, current_event,
                                                                                    abnormal_event_frames,
                                                                                    current_event_index)
        return [anomaly_detected, abnormal_event_frames]

    @staticmethod
    def _check_foot_off(acq_walk, current_event, abnormal_event_frames, current_event_index):
        anomaly_detected = False
        for next_event_index in range(current_event_index + 1, acq_walk.GetEventNumber()):
            next_event = acq_walk.GetEvent(next_event_index)
            print(f"Next Frame: {next_event.GetFrame()} {next_event.GetContext()} {next_event.GetLabel()}")
            if next_event.GetContext() != current_event.GetContext():
                anomaly_detected = True
                abnormal_event_frames.append(
                    {"Label": current_event.GetLabel(), "Start-Frame": current_event.GetFrame(),
                     "End-Frame": next_event.GetFrame(),
                     "Anomaly": "Normal Inter Context Sequence"})
            break

        return [anomaly_detected, abnormal_event_frames]

    @staticmethod
    def _check_foot_strike(acq_walk, current_event, abnormal_event_frames, current_event_index):
        anomaly_detected = False
        counter_events_between_context = 0
        for next_event_index in range(current_event_index + 1, acq_walk.GetEventNumber()):
            next_event = acq_walk.GetEvent(next_event_index)
            print(f"Next Frame: {next_event.GetFrame()} {next_event.GetContext()} {next_event.GetLabel()}")
            if next_event.GetContext() == current_event.GetContext():
                if counter_events_between_context != 2:
                    anomaly_detected = True
                    abnormal_event_frames.append(
                        {"Label": current_event.GetLabel(), "Start-Frame": current_event.GetFrame(),
                         "End-Frame": next_event.GetFrame(),
                         "Anomaly": "Normal Inter Context Sequence"})
                break
            else:
                counter_events_between_context += 1
        return [anomaly_detected, abnormal_event_frames]
