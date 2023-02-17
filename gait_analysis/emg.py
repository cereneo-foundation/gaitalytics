from btk import btkAcquisition
import numpy as np
import scipy as sp
from scipy import signal
from gait_analysis import events

class EMGCoherenceAnalysis:
    VOLTAGE_PREFIX = "Voltage."
    """
    This class contains all the material to calculate coherence from analog EMG signals
    """

    def __init__(self,
                 emg_channel_1: int,
                 emg_channel_2: int,
                 side: str,
                 window_size: int = 1024
                 ):
        """
        Initializes Object

        :param emg_channel_1: first EMG channel
        :param emg_channel_2: second EMG channel
        :param side: leg on which the analogs are recorded
        :param window_size: size of windows used for the FFT in coherence calculation
        """
        self.emg_channel_1_index = f"{self.VOLTAGE_PREFIX}{emg_channel_1}"
        self.emg_channel_2_index = f"{self.VOLTAGE_PREFIX}{emg_channel_2}"
        self._side = side
        self._window_size = window_size

    def get_swing_phase(self, acq: btkAcquisition): # call it 'get_swing_phase' everywhere
        """
        Selects portions of EMG signal to analyze with coherence. These portions correspond to swing phase in gait

        :param acq: EMG raw acquisition with events added
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
                if event.GetLabel() == events.GAIT_EVENT_FOOT_OFF:
                    # TODO what is last Event is FS????? FUCK
                    foot_off_list.append(event.GetFrame())
                    if start: # Be sure first event ist Foot of (we want swing phase)
                        start = False
                elif event.GetLabel() == events.GAIT_EVENT_FOOT_STRIKE:
                    if not start: # Be sure first event ist Foot of (we want swing phase)
                        foot_strike_list.append(event.GetFrame())
            event_iterator.incr()

        segments = list(zip(foot_off_list, foot_strike_list))  # merge list to make a list of windows
        self._segments = segments
        #return segments

    def calculate_coherence(self, acq: btkAcquisition) -> tuple:
        """
        Calculates coherence over frequency for each window and averages them

        :param acq: filtered version of EMG signal
        :param windows: list of selected EMG signal windows
        :return f: frequencies axis for plot
        :return mean_coherence: averaged coherence over all windows
        """
        # Extract swing phase segments for both signals
        emg_channel_1 = [acq.GetAnalog(self._emg_channel_1_index).GetValues()[start:end] for start, end in self._segments]
        emg_channel_2 = [acq.GetAnalog(self._emg_channel_2_index).GetValues()[start:end] for start, end in self._segments]

        f, coh_segments = sp.signal.coherence(emg_channel_1, emg_channel_2, fs=acq.GetAnalogFrequency(), window='hann', nperseg=None, noverlap=None)
        mean_coherence = coh_segments.mean(axis=0)

        return f, mean_coherence

