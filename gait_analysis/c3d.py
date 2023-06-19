from __future__ import annotations

from enum import Enum
from statistics import mean

import btk
import ezc3d
import numpy as np

ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


class PointDataType(Enum):
    Marker = 0
    Angles = 1
    Forces = 2
    Moments = 3
    Power = 4
    Scalar = 5
    Reaction = 6


class AxesNames(Enum):
    x = 0
    y = 1
    z = 2


class GaitEventContext(Enum):
    """
    Representation of gait event contexts. At the moment mainly left and right
    """
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def get_contrary_context(cls, context: str):
        if context == cls.LEFT.value:
            return cls.RIGHT
        return cls.LEFT


class C3dAcquisition:
    """
    Main entry point to handle c3d files
    """

    def __init__(self, acq: ezc3d.c3d):
        self.acq = acq

    @property
    def acq(self) -> ezc3d.c3d:
        return self._acq

    @acq.setter
    def acq(self, acq: ezc3d.c3d):
        self._acq = acq

    def get_number_of_points(self) -> int:
        """
        Returns the amount of stored points in c3d
        :return: amount of stored points
        """
        return self.acq['parameters']['POINT']['LABELS']['value']

    def get_point_frame_number(self) -> int:
        """
        Returns the number of frames in points
        :return: number of frames
        """
        return self.acq['parameters']['POINT']['FRAMES']['value'][0]

    def get_point(self, index: Enum("MarkerMapping")) -> btk.btkPoint:
        """
        Returns a specific point either py name or index
        :param index: name or index of the required point
        :return: point object
        """
        self.acq.get("parameters").get("POINT").get("LABELS").get("value").index(index.value)
        print(index)
        return None

    @staticmethod
    def read_btk(filename) -> C3dAcquisition:
        """
        read a c3d with btk

        Args:
            filename (str): filename with its path
        """
        c3d = ezc3d.c3d(filename)
        acq = C3dAcquisition(c3d)
        # sort events
        #        acq.sort_events()

        return acq

    def write_btk(self, filename):
        """
        write a c3d with Btk

        Args:
            acq (btk.acquisition): a btk acquisition instance
            filename (str): filename with its path
        """
        self.acq.write(filename)

    def sort_events(self):
        """
        sort events in acquisition

        Args:
            acq (btkAcquisition): a btk acquisition instance

        """
        events = self.acq.GetEvents()

        value_frame = {}
        for event in btk.Iterate(events):
            if event.GetFrame() not in value_frame:
                value_frame[event.GetFrame()] = event

        sorted_keys = sorted(value_frame)

        newEvents = btk.btkEventCollection()
        for key in sorted_keys:
            newEvents.InsertItem(value_frame[key])

        self.acq.ClearEvents()
        self.acq.SetEvents(newEvents)


class C3dPoint:
    """
    Class to store c3d Point information
    """

    def get_values(self) -> np.ndarray:
        pass


def is_progression_axes_flip(left_heel, left_toe):
    return 0 < mean(left_toe[AxesNames.y.value] - left_heel[AxesNames.y.value])


def correct_points_frame_by_frame(acq: C3dAcquisition):
    frame_size = acq.get_point_frame_number()
    correction = get_fastest_point_by_frame(acq, 1)
    for frame_number in range(1, frame_size):
        if (frame_number + 2) < frame_size:
            correction_new = get_fastest_point_by_frame(acq, frame_number + 1)
        correct_points_in_frame(acq, frame_number, correction)
        correction += correction_new


def correct_points_in_frame(acq_trial: C3dAcquisition, frame_number: int, correction: float):
    print(f"{frame_number}:{correction}")
    for point_number in range(0, acq_trial.get_number_of_points()):
        acq_trial.get_point(point_number).SetValue(frame_number, 1,
                                                   (acq_trial.get_point(point_number).GetValue(frame_number,
                                                                                               1) + correction))


def get_fastest_point_by_frame(acq_trial: C3dAcquisition, frame_number: int) -> float:
    rfmh_point = acq_trial.get_point("RFMH")
    rhee_point = acq_trial.get_point("RHEE")
    lfmh_point = acq_trial.get_point("LFMH")
    lhee_point = acq_trial.get_point("LHEE")
    lfmh_dist = lfmh_point.GetValue(frame_number - 1, 1) - lfmh_point.GetValue(frame_number, 1)
    lhee_dist = lhee_point.GetValue(frame_number - 1, 1) - lhee_point.GetValue(frame_number, 1)
    rfmh_dist = rfmh_point.GetValue(frame_number - 1, 1) - rfmh_point.GetValue(frame_number, 1)
    rhee_dist = rhee_point.GetValue(frame_number - 1, 1) - rhee_point.GetValue(frame_number, 1)
    return np.min([lfmh_dist, lhee_dist, rfmh_dist, rhee_dist])
