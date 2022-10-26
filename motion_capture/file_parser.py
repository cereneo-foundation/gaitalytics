from abc import ABC, abstractmethod

import c3d
import numpy as np


class FileParser(ABC):

    @abstractmethod
    def get_data(self):
        pass


class C3dFileParser(FileParser):

    def __init__(self, path):
        input_stream = open(path, 'rb')
        self._labeled_points = {}
        self._labeled_analogs = {}
        self._frame_no = []
        try:
            c3d_reader = c3d.Reader(input_stream)
            self._extract_data(c3d_reader)
        finally:
            input_stream.close()

    def _extract_data(self, c3d_reader):
        # prepare datastructure for storing imu, force plat, emg ,points
        point_labels = c3d_reader.point_labels
        for label in point_labels:
            self._labeled_points[label.strip()] = {'x': [], 'y': [], 'z': [],
                                                   'err': [], 'cam': []}

        analog_labels = c3d_reader.analog_labels
        for label in analog_labels:
            self._labeled_analogs[label.strip()] = []

        for frame_no, points, analog in c3d_reader.read_frames(copy=False):
            self._extract_points(points)
            self._extract_analog(analog)
            self._frame_no.append(frame_no)

    def _extract_points(self, points):
        i = 0
        for x, y, z, err, cam in points:
            label = list(self._labeled_points.keys())[i]
            self._labeled_points[label]['x'].append(x)
            self._labeled_points[label]['y'].append(y)
            self._labeled_points[label]['z'].append(z)
            self._labeled_points[label]['err'].append(err)
            self._labeled_points[label]['cam'].append(cam)
            i += 1

    def _extract_analog(self, analogs):
        i = 0
        for analog in analogs:
            label = list(self._labeled_analogs.keys())[i]
            self._labeled_analogs[label].extend(analog)
            i += 1

    def get_data(self):
        return BioMechanicData(points=self._labeled_points, emg=self._labeled_analogs)

    @property
    def frame_no(self):
        return self.frame_no

    @property
    def points(self):
        return self._labeled_points

    @property
    def analogs(self):
        return self._labeled_analogs


class BioMechanicData:
    def __init__(self, frame_no=np.array([]), points={}, emg={}, force_plate={}, imus={}):
        self._frame_no = frame_no
        self._points = points
        self._emg = emg
        self._force_plate = force_plate
        self._imus = imus
        self._frame_count = self._check_synchronisation()

    @staticmethod
    def _calc_n_frames(data):
        return len(data[list(data.keys())[0]])

    def _check_synchronisation(self):
        n_frames = []
        if self._points:
            n_frames.append(self._calc_n_frames(self._points[list(self._points.keys())[0]]))
        if self._imus:
            n_frames.append(self._calc_n_frames(self._imus))
        if self._force_plate:
            n_frames.append(self._calc_n_frames(self._force_plate))
        if self._emg:
            n_frames.append(self._calc_n_frames(self._emg))

        for i in range(len(n_frames) - 2):
            if n_frames[i] != n_frames[i + 1]:
                raise Exception("Data is not synced")
        return n_frames[0]

    @property
    def point_data(self):
        return self._points

    @property
    def imu_data(self):
        return self._imus

    @property
    def force_plate_data(self):
        return self._force_plate

    @property
    def emg_data(self):
        return self._emg

    @property
    def frame_count(self):
        return self._frame_count
