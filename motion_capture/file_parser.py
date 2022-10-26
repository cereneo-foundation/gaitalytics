from abc import ABCMeta, abstractmethod

import c3d


class C3dFileParser:

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

    def _extract_analog(self, *analogs):
        i = 0
        for analog in analogs:
            label = list(self._labeled_analogs.keys())[i]
            # We should adress this -> 10 measurement per frame
            self._labeled_analogs[label].append(analog)
            i += 1

    @property
    def frame_no(self):
        return self._frame_no

    @property
    def points(self):
        return self._labeled_points

    @property
    def analogs(self):
        return self._labeled_analogs


class BioMechanicData:
    def __init__(self, analogs_mapper, frame_no=[], points={}, analogs={}, ):
        self._frame_no = frame_no
        self._points = points
        self._emg = analogs_mapper.get_emg_data(analogs)
        self._momentum = analogs_mapper.get_momentum_data(analogs)
        self._force = analogs_mapper.get_force_data(analogs)
        self._check_synchronisation()

    def _check_synchronisation(self):
        n_frames = []
        if self._points:
            n_frames.append(len(self._points[list(self._points.keys())[0]]['x']))
        if self._frame_no:
            n_frames.append(len(self._frame_no))

        for i in range(len(n_frames) - 2):
            if n_frames[i] != n_frames[i + 1]:
                raise Exception("Data is not synced")

    @property
    def point_data(self):
        return self._points

    @point_data.setter
    def point_data(self, point_data):
        self._points = point_data

    @property
    def momentum_data(self):
        return self._momentum

    @momentum_data.setter
    def momentum_data(self, momentum_data):
        self._momentum = momentum_data

    @property
    def force_data(self):
        return self._force

    @force_data.setter
    def force_data(self, force_data):
        self._force = force_data

    @property
    def emg_data(self):
        return self._emg

    @emg_data.setter
    def emg_data(self, emg_data):
        self._emg = emg_data


class AbstractAnalogsMapper(ABCMeta):
    @abstractmethod
    def get_emg_data(self, analogs):
        pass

    @abstractmethod
    def get_momentum_data(self, analogs):
        pass

    @abstractmethod
    def get_force_data(self, analogs):
        pass


class AnalogsMapper(AbstractAnalogsMapper):

    def __init__(cls, emg_prefix, force_prefix, momentum_prefix):
        cls._EMG_PREFIX = emg_prefix
        cls._FORCE_PREFIX = force_prefix
        cls._MOMENTUM_PREFIX = momentum_prefix

    @staticmethod
    def _find_analogs_with_prefix(analogs, prefix):
        data = {}
        for analog_label in analogs.keys():
            if analog_label.startswith(prefix):
                data[analog_label.split('.', 1)[1]] = analogs[analog_label]
        return data

    @staticmethod
    def extract_data_with_axes(data):
        moments_struct = {}
        for moment_label in data.keys():
            if len(moment_label) == 3:
                moments_struct[moment_label[2:3]] = {}
        for moment_label in data.keys():
            if len(moment_label) == 3:
                moments_struct[moment_label[2:3]][moment_label[1:2]] = data[moment_label]
        return moments_struct

    def get_emg_data(self, analogs):
        return self._find_analogs_with_prefix(analogs, self._EMG_PREFIX)

    def get_momentum_data(self, analogs):
        moments = self._find_analogs_with_prefix(analogs, self._MOMENTUM_PREFIX)
        return self.extract_data_with_axes(moments)

    def get_force_data(self, analogs):
        forces = self._find_analogs_with_prefix(analogs, self._FORCE_PREFIX)
        return self.extract_data_with_axes(forces)
