from btk import btkAcquisition
import numpy as np # in others too ?
import scipy as sp
from scipy import signal


class EMGCoherenceAnalysis:
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
        self.emg_channel_1 = emg_channel_1
        self.emg_channel_2 = emg_channel_2
        self.side = side
        self.window_size = window_size

    def filter(self, acq: btkAcquisition):
        """
        Band-pass filter and EMG pre-processing

        :param acq: EMG raw acquisition
        :return: filtered version of EMG signal
        """
        x = acq.get_point(acq.GetPointLabel(self.emg_channel_1)) # get EMG data 
        x -= np.mean(x)

        # Frequency filtering
        fs = acq.GetPointFrequency()
        high = 10/fs #hyperparameter
        low = 500/fs #hyperparameter
        b, a = sp.signal.butter(2, [high,low], btype='bandpass') #hyperparameter
        acq_filtered = sp.signal.filtfilt(b, a, x)

        acq_rectified = abs(acq_filtered) # EMG Rectification

        return acq_rectified
    
        pass

    def get_windows(self, acq: btkAcquisition):
        """
        Selects portions of EMG signal to analyze with coherence. These portions correspond to swing phase in gait

        :param acq: EMG raw acquisition
        :return: list of selected EMG signal windows
        """
        # TODO luca get windows
        pass

    def calculate_coherence(self, acq: btkAcquisition, windows: list) -> tuple:
        """
        Calculates coherence over frequency for each window and averages them

        :param acq: filtered version of EMG signal
        :param windows: list of selected EMG signal windows 
        :return:
        """
        # TODO luca coherence
        pass
