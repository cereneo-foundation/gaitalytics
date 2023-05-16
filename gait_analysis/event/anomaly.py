from abc import ABC

from btk import btkAcquisition
from pyCGM2.Tools import btkTools

from gait_analysis.event.utils import GaitEventLabel


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
    @staticmethod
    def _check_events(self, acq_walk: btkAcquisition, abnormal_event_frames: list) -> [bool, list]:
        pass


class BasicContextChecker(EventAnomalyChecker):
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

            current_label = current_event.GetLabel()

            if current_label == GaitEventLabel.FOOT_OFF.value:
                [anomaly_detected, abnormal_event_frames] = self._check_foot_off(acq_walk, current_event,
                                                                                 abnormal_event_frames,
                                                                                 current_event_index)
            elif current_label == GaitEventLabel.FOOT_STRIKE.value:
                [anomaly_detected, abnormal_event_frames] = self._check_foot_strike(acq_walk, current_event,
                                                                                    abnormal_event_frames,
                                                                                    current_event_index)
        return [anomaly_detected, abnormal_event_frames]

    @staticmethod
    def _check_foot_off(acq_walk, current_event, abnormal_event_frames, current_event_index):
        anomaly_detected = False
        for next_event_index in range(current_event_index + 1, acq_walk.GetEventNumber()):
            next_event = acq_walk.GetEvent(next_event_index)
            if next_event.GetContext() != current_event.GetContext():
                anomaly_detected = True
                abnormal_event_frames.append(
                    {"Context": current_event.GetLabel(), "Start-Frame": current_event.GetFrame(),
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
            if next_event.GetContext() == current_event.GetContext():
                if counter_events_between_context != 2:
                    anomaly_detected = True
                    abnormal_event_frames.append(
                        {"Context": current_event.GetLabel(), "Start-Frame": current_event.GetFrame(),
                         "End-Frame": next_event.GetFrame(),
                         "Anomaly": "Normal Inter Context Sequence"})
                break
            else:
                counter_events_between_context += 1
        return [anomaly_detected, abnormal_event_frames]
