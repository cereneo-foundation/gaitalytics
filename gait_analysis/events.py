from abc import ABC, abstractmethod

import numpy as np
from btk import btkAcquisition, btkEvent, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from matplotlib import pyplot as plt
from scipy import signal

from gait_analysis.api import GaitEventLabel, ConfigProvider
from gait_analysis.utils import min_max_norm
from gait_analysis import c3d
from gait_analysis.c3d import is_progression_axes_flip

FORCE_PLATE_SIDE_MAPPING_CAREN = {"Left": 0, "Right": 1}


# Event detection
class AbstractGaitEventDetector(ABC):

    @abstractmethod
    def detect_events(self, acq: btkAcquisition):
        pass

    @staticmethod
    def _create_event(acq, frame: int, event_label: GaitEventLabel, event_context: c3d.GaitEventContext):
        frequency = acq.GetPointFrequency()
        event = btkEvent()
        event.SetLabel(event_label.value)
        #  event.SetFrame(int(frame))
        event.SetId(GaitEventLabel.get_type_id(event_label.value))
        event.SetDetectionFlags(btkEvent.Automatic)
        event.SetContext(event_context.value)
        event.SetTime(float((frame - 1) / frequency))
        return event


class ZenisGaitEventDetector(AbstractGaitEventDetector):
    """
    This class detects gait events from cgm2 model data
    """

    def __init__(self, configs: ConfigProvider, foot_strike_offset: int = 0, foot_off_offset: int = 0):
        """ Initializes Object

        :param foot_strike_offset: numbers of frames to offset next foot strike event
        :param foot_off_offset: number of frames to offset next foot off event
        """
        self._config = configs
        self._foot_strike_offset = foot_strike_offset
        self._foot_off_offset = foot_off_offset

    def detect_events(self, acq: btkAcquisition):
        """detects zeni gait events and stores it in to the acquisition

        :param acq: loaded and filtered acquisition
        """

        right_heel = acq.GetPoint(self._config.MARKER_MAPPING.right_heel.value).GetValues()
        left_heel = acq.GetPoint(self._config.MARKER_MAPPING.left_heel.value).GetValues()
        right_hip = acq.GetPoint(self._config.MARKER_MAPPING.right_back_hip.value).GetValues()
        left_hip = acq.GetPoint(self._config.MARKER_MAPPING.left_back_hip.value).GetValues()

        sacrum = (right_hip + left_hip) / 2.0
        right_diff_heel = right_heel - sacrum
        left_diff_heel = left_heel - sacrum
        right_diff_toe = right_heel - sacrum
        left_diff_toe = left_heel - sacrum

        self._create_events(acq, left_diff_toe, GaitEventLabel.FOOT_OFF, c3d.GaitEventContext.LEFT)
        self._create_events(acq, right_diff_toe, GaitEventLabel.FOOT_OFF, c3d.GaitEventContext.RIGHT)
        self._create_events(acq, left_diff_heel, GaitEventLabel.FOOT_STRIKE, c3d.GaitEventContext.LEFT)
        self._create_events(acq, right_diff_heel, GaitEventLabel.FOOT_STRIKE, c3d.GaitEventContext.RIGHT)

    #   c3d.sort_events(acq)

    def _create_events(self, acq, diff, event_label: GaitEventLabel, event_context: c3d.GaitEventContext,
                       min_distance: int = 100,
                       show_plot: bool = False):
        data = diff[:, c3d.AxesNames.y.value]
        if is_progression_axes_flip(acq.GetPoint(self._config.MARKER_MAPPING.left_heel.value).GetValues(),
                                    acq.GetPoint(self._config.MARKER_MAPPING.left_meta_5.value).GetValues()):
            data = data * -1
        data = min_max_norm(data)

        if GaitEventLabel.FOOT_STRIKE == event_label:
            data = [entry * -1 for entry in data]

        extremes, foo = signal.find_peaks(data, height=[0, 1], distance=min_distance)
        if show_plot:
            plt.plot(data)
            for i in extremes:
                plt.plot(i, data[i], 'ro')
            plt.plot()
            plt.show()

        for frame in extremes:
            acq.AppendEvent(self._create_event(acq, frame, event_label, event_context))


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

        for context in c3d.GaitEventContext:
            force_down_sample = force_plate_down_sample(acq, self._mapped_force_plate[context.value])
            detection = detect_onset(force_down_sample, threshold=self._weight_threshold)
            sequence = self._detect_gait_event_type(force_down_sample, detection)
            self._store_force_plate_events(acq, context, sequence)

    def _store_force_plate_events(self, btk_acq, context, sequence):
        for elem in sequence:
            event_label = elem[0]
            frame = elem[1]
            ev = self._create_event(btk_acq, frame, event_label, context)
            btk_acq.AppendEvent(ev)

    @staticmethod
    def _detect_gait_event_type(force_plate_signal: np.ndarray, detected_force_plate_events: np.ndarray) -> list:
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
                        detected_event_types.append([GaitEventLabel.FOOT_OFF, signal_index])
                    else:
                        detected_event_types.append([GaitEventLabel.FOOT_STRIKE, signal_index])
        return detected_event_types  # Contain the label of the event and the corresponding index


# Anomaly detection

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
        [anomaly_detected, abnormal_event_frames] = self._check_events(acq_walk)
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

    @abstractmethod
    def _check_events(self, acq_walk: btkAcquisition) -> [bool, list]:
        pass


class ContextPatternChecker(EventAnomalyChecker):
    """
    Checks if events are alternating between Heel_Strike and Foot_Off per context
    """

    """
    kick off the checker
    :param acq_walk: Acquisition with added Events
    :return: flag is anomalies found, list of anomalies
    """
    def _check_events(self, acq_walk: btkAcquisition) -> [bool, list]:
        abnormal_event_frames = []
        anomaly_detected = False

        c3d.sort_events(acq_walk)

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


class EventSpacingChecker(EventAnomalyChecker):

    def __init__(self, event_checker=None, frame_threshold=30):
        super().__init__(event_checker)
        self._frame_threshold = frame_threshold

    def _check_events(self, acq_walk: btkAcquisition) -> [bool, list]:
        anomaly_detected = False
        abnormal_event_frames = []
        for current_event_index in range(0, acq_walk.GetEventNumber()):
            current_event = acq_walk.GetEvent(current_event_index)
            context = current_event.GetContext()
            for next_event_index in range(current_event_index + 1, acq_walk.GetEventNumber()):
                next_event = acq_walk.GetEvent(next_event_index)
                if next_event.GetContext() == context:
                    if next_event.GetFrame() - current_event.GetFrame() < self._frame_threshold:
                        abnormal_event_frames.append({"Context": context, "Start-Frame": current_event.GetFrame(),
                                                      "End-Frame": next_event.GetFrame(),
                                                      "Anomaly": "Abnormal time spacing"})
                        anomaly_detected = True
                    break
        return [anomaly_detected, abnormal_event_frames]


# utils
def find_next_event(acq: btkAcquisition, label: str, context, start_index: int) -> [btkEvent, btkEvent]:
    if acq.GetEventNumber() >= start_index + 1:
        for event_index in range(start_index + 1, acq.GetEventNumber()):
            event = acq.GetEvent(event_index)
            if event.GetContext() == context:
                if not event.GetLabel() == label:
                    return [event, unused_event]
                else:
                    unused_event = event
    raise IndexError()


def force_plate_down_sample(acq: btkAcquisition, force_plate_index: int) -> list:
    """

    :param acq: c3d file
    :param force_plate_index: index of force plate in c3d
    :return: down sample data
    """
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
    ## TODO rewrite code, just copied it

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
