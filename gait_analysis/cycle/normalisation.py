from abc import ABC, abstractmethod
from typing import List

import numpy as np
from btk import btkAcquisition

from gait_analysis.cycle.builder import GaitCycle


class NormalisedCycle:

    def __init__(self, data: np.array, number: int, context: str):
        self.data = data
        self.number = number
        self.context = context


class TimeNormalisationAlgorithm(ABC):

    def __init__(self):

        pass

    def nomalise(self, acq: btkAcquisition, cycles: {}) -> {}:
        ## TODO: find a good structure
        pass


    @abstractmethod
    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        pass


class LinearTimeNormalisation(TimeNormalisationAlgorithm):

    def _run_algorithm(self, data: np.ndarray, start_frame: int, end_frame: int,
                       number_frames: int = 100) -> np.ndarray:
        times = np.arange(0, end_frame - start_frame, 1)
        times_new = np.linspace(0, end_frame - start_frame, num=100)

        interpolated_data = []
        # Create an interpolation function
        for i in range(0, len(data[0])):
            interpolated_data.append(np.interp(times_new, times, data[start_frame:end_frame, i]))

        return np.array(interpolated_data)
