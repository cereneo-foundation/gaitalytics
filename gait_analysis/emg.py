from btk import btkAcquisition
import scipy as sp
from scipy import signal

import gait_analysis.utils.c3d
from gait_analysis.utils.c3d import ANALOG_VOLTAGE_PREFIX_LABEL

class EMGCoherenceAnalysis:

    """
    This class contains all the material to calculate coherence from analog EMG signals
    """

    def __init__(self,
                 emg_channel_1: int,
                 emg_channel_2: int,
                 side: str,
                 ):
        """
        Initializes Object

        :param emg_channel_1: first EMG channel
        :param emg_channel_2: second EMG channel
        :param side: leg on which the analogs are recorded
        """
        self.emg_channel_1_index = f"{ANALOG_VOLTAGE_PREFIX_LABEL}{emg_channel_1}"
        self.emg_channel_2_index = f"{ANALOG_VOLTAGE_PREFIX_LABEL}{emg_channel_2}"
        self._side = side

    def get_swing_phase(self, acq: btkAcquisition):
        """
        Selects EMG signal segments that correspond to swing phase in gait.

        :param acq: EMG acquisition with events added
        :return: list of swing phase windows. Given as pairs: [Toe off index, Heel strike index]
        """
        events_list = acq.GetEvents()
        # TODO: loop trough events again, consider first event ist not Foot off
        event_iterator = acq.GetEvents().Begin()
        foot_off_list = []
        foot_strike_list = []
        start = True

        while event_iterator != acq.GetEvents().End():
            event = event_iterator.value()
            if event.GetContext() == self._side:
                if event.GetLabel() == gait_analysis.utils.utils.c3d_utils.GAIT_EVENT_FOOT_OFF:
                    # TODO what is last Event is FS????? FUCK
                    foot_off_list.append(event.GetFrame())
                    if start: # Be sure first event ist Foot of (we want swing phase)
                        start = False
                elif event.GetLabel() == gait_analysis.utils.utils.c3d_utils.GAIT_EVENT_FOOT_STRIKE:
                    if not start: # Be sure first event ist Foot of (we want swing phase)
                        foot_strike_list.append(event.GetFrame())
            event_iterator.incr()

        segments = list(zip(foot_off_list, foot_strike_list))  # merge lists to make a list of segments
        
        # Save segments as attribute
        self._segments = segments

    def calculate_coherence(self, acq: btkAcquisition) -> tuple:
        """
        Calculates coherence over frequency for each segment and averages them

        :param acq: filtered version of EMG signal
        :return f: frequencies axis for plot
        :return mean_coherence: averaged coherence over all segments
        """
        # Extract swing phase segments from both signals
        emg_channel_1 = [acq.GetAnalog(self._emg_channel_1_index).GetValues()[start:end] for start, end in self._segments]
        emg_channel_2 = [acq.GetAnalog(self._emg_channel_2_index).GetValues()[start:end] for start, end in self._segments]

        # Coherence calculation
        f, coh_segments = sp.signal.coherence(emg_channel_1, emg_channel_2, fs=acq.GetAnalogFrequency(), window='hann', nperseg=None, noverlap=None)
        mean_coherence = coh_segments.mean(axis=0)

        return f, mean_coherence

