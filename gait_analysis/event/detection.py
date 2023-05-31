from abc import ABC, abstractmethod

import numpy as np
from btk import btkAcquisition, btkEvent
from scipy import signal

from gait_analysis.event.utils import GaitEventLabel, GaitContext
from gait_analysis.utils import utils, config, c3d

FORCE_PLATE_SIDE_MAPPING_CAREN = {"Left": 0, "Right": 1}


class AbstractGaitEventDetector(ABC):

    @abstractmethod
    def detect_events(self, acq: btkAcquisition):
        pass

    @staticmethod
    def _create_event(acq, frame: int, event_label: GaitEventLabel, event_context: GaitContext):
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

    def __init__(self, configs: dict, foot_strike_offset: int = 0, foot_off_offset: int = 0):
        """ Initializes Object

        :param foot_strike_offset: numbers of frames to offset next foot strike event
        :param foot_off_offset: number of frames to offset next foot off event
        """
        self.config = configs
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

        self._create_events(acq, left_diff_toe, GaitEventLabel.FOOT_OFF, GaitContext.LEFT)
        self._create_events(acq, right_diff_toe, GaitEventLabel.FOOT_OFF, GaitContext.RIGHT)
        self._create_events(acq, left_diff_heel, GaitEventLabel.FOOT_STRIKE, GaitContext.LEFT)
        self._create_events(acq, right_diff_heel, GaitEventLabel.FOOT_STRIKE, GaitContext.RIGHT)

     #   c3d.sort_events(acq)

    def _create_events(self, acq, diff, event_label: GaitEventLabel, event_context: GaitContext):
        peak_function = np.less if event_label == GaitEventLabel.FOOT_STRIKE else np.greater
        extremes = signal.argrelextrema(diff[:, c3d.AxesNames.y.value], peak_function)
        extremes = extremes[0]
        # self._plot(diff[0:2000, c3d.AxesNames.y.value], extremes)
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

        for context in GaitContext:
            force_down_sample = utils.force_plate_down_sample(acq, self._mapped_force_plate[context.value])
            detection = utils.detect_onset(force_down_sample, threshold=self._weight_threshold)
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