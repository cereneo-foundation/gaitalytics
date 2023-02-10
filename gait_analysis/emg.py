from btk import btkAcquisition


class EMGCoherenceAnalysis:
    def __init__(self,
                 emg_channel_up: int,
                 emg_channel_down: int,
                 side: str,
                 window_size: int = 1024
                 ):
        """

        """
        self.emg_channel_up = emg_channel_up
        self.emg_channel_down = emg_channel_down
        self.side = side
        self.window_size = window_size

    def filter(self, acq: btkAcquisition):
        # TODO: luca filter
        pass

    def calculate_coherence(self, acq: btkAcquisition, windows: list) -> tuple:
        # TODO luca coehrence
        pass

    def get_windows(self, acq: btkAcquisition):
        # TODO luca ge t windows
        pass
