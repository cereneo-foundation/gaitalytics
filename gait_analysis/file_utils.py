import ezc3d
import numpy
import pandas as pd

C3D_FIELD_DATA: str = 'data'
C3D_FIELD_DATA_POINTS: str = 'points'
C3D_FIELD_DATA_PLATFORM: str = 'platform'
C3D_FIELD_DATA_FORCE: str = 'force'
C3D_FIELD_DATA_MOMENT: str = 'moment'
C3D_FIELD_DATA_COP: str = 'center_of_pressure'

C3D_FIELD_PARAMETER: str = 'parameters'
C3D_FIELD_PARAMETER_POINT: str = 'POINT'
C3D_FIELD_PARAMETER_ANALOG: str = 'ANALOG'
C3D_FIELD_PARAMETER_TRIAL: str = 'TRIAL'
C3D_FIELD_PARAMETER_SUBJECTS: str = 'SUBJECTS'
C3D_FIELD_PARAMETER_NAMES: str = 'NAMES'
C3D_FIELD_PARAMETER_CAMERA_RATE: str = 'CAMERA_RATE'
C3D_FIELD_PARAMETER_ANALOG_RATE: str = 'RATE'

C3D_FIELD_PARAMETER_LABELS: str = 'LABELS'
C3D_FIELD_PARAMETER_DESCRIPTIONS: str = 'DESCRIPTIONS'

C3D_FIELD_VALUE: str = 'value'

DIRECTION_Z: str = 'z'
DIRECTION_Y: str = 'y'
DIRECTION_X: str = 'x'


class C3dFileWrapper:
    """
    This wrapper class simplifies the usage of ezc3d.

    This wrapper class can be used to read data without deep knowledge
    of the c3d-file structure and integrates nicely with the gait library
    """

    def __init__(self, path: str, extract_force_plate_data: bool = True):
        """
        Initialises caches and stores c3d object

        :param path: path to c3d file
        :param extract_force_plate_data: if force plate data should be extracted
        """
        self.c3d_file = ezc3d.c3d(path, extract_force_plate_data)
        self._directions = {DIRECTION_X: 0, DIRECTION_Y: 1, DIRECTION_Z: 2}

    @property
    def c3d_file(self) -> ezc3d.c3d:
        """
        Returns stored c3d object

        :return: stored c3d object
        :rtype: ezc3d.c3d
        """
        return self._c3d_file

    @c3d_file.setter
    def c3d_file(self, c3d_file: ezc3d.c3d):
        """
        Stores c3d object and re-initialized cache

        :param c3d_file: c3d object loaded from 3D-motion-capture system file
        """
        self._c3d_file = c3d_file
        self._init_point_labels()
        self._init_platform_labels()

    def get_subject(self) -> str:
        """
        Returns subject name

        :return: subject name
        """
        return self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_SUBJECTS][C3D_FIELD_PARAMETER_NAMES][C3D_FIELD_VALUE][0]

    def get_point_labels(self) -> list[str]:
        """
        Returns list of available point labels from c3d file

        :return: list of point labels
        """
        return list(self._point_labels.keys())

    def get_camera_frame_rate(self) -> numpy.float64:
        """
        Returns frame rate of camera system

        :return: frame rate
        """
        return self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_TRIAL][C3D_FIELD_PARAMETER_CAMERA_RATE][
            C3D_FIELD_VALUE][0]

    def get_points(self, labels: list[str], directions: list[str] = (DIRECTION_X, DIRECTION_Y, DIRECTION_Z)) -> pd.DataFrame:
        """
        Returns data of requested point labels in columns and directions in row

        :param labels: point labels for which the data is needed
        :param directions: direction names of which the data is needed
        :return: two-dimensional table of numpy arrays data
        """
        points_dict = {}
        for label_key in labels:
            dir_dict = {}
            for dir_key in directions:
                dir_dict[dir_key] = self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_POINTS][self._directions[dir_key]][
                    self._point_labels[label_key]]
            points_dict[label_key] = dir_dict
        return pd.DataFrame(points_dict)

    def get_platform_labels(self) -> list[str]:
        """
        Returns list of available platform labels from c3d file

        :return: list of platform labels
        """
        return list(self._platform_labels.keys())

    def get_platform_frame_rate(self) -> numpy.float64:
        """
        Returns frame rate of force plate

        :return: frame rate
        """
        return self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_ANALOG][C3D_FIELD_PARAMETER_ANALOG_RATE][
            C3D_FIELD_VALUE][0]

    def get_platform_forces(self, platform_labels: list[str],
                            directions: list[str] = (DIRECTION_X, DIRECTION_Y, DIRECTION_Z)) -> pd.DataFrame:
        """
        Returns data of requested platforms in columns and directions
        in row

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed
        :return: two-dimensional table of numpy arrays data
        """
        return self._get_platform_data(directions, platform_labels, C3D_FIELD_DATA_FORCE)

    def get_platform_moments(self, platform_labels: list[str],
                             directions: list[str] = (DIRECTION_X, DIRECTION_Y, DIRECTION_Z)) -> pd.DataFrame:
        """
        Returns data of requested platforms in columns and directions
        in row

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed,
        :return: two-dimensional table of numpy arrays data
        """
        return self._get_platform_data(directions, platform_labels,
                                       C3D_FIELD_DATA_MOMENT)

    def get_platform_cop(self, platform_labels: list[str],
                         directions: list[str] = (DIRECTION_X, DIRECTION_Y, DIRECTION_Z)) -> pd.DataFrame:
        """
        Returns data of requested platforms in columns and directions
        in row

        :param platform_labels: platform labels for which the data is needed
        :type platform_labels: list[str]
        :param directions: direction names of which the data is needed
        :return: two-dimensional table of numpy arrays data
        """
        return self._get_platform_data(directions, platform_labels,
                                       C3D_FIELD_DATA_COP)

    def _init_point_labels(self):
        """Caches point labels in self._point_labels"""
        c3d_labels = \
            self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_POINT][
                C3D_FIELD_PARAMETER_LABELS][
                C3D_FIELD_VALUE]
        self._point_labels = {}
        for label in c3d_labels:
            index = c3d_labels.index(label)
            self._point_labels[label] = index

    def _init_platform_labels(self):
        """
        Caches platform labels in self._platform_labels
        Loops through all analog labels and checks for "Force Plate" in label.
        Checks if label already exists in tuple and saves it in cache tuple
        """
        descriptions = \
            self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_ANALOG][
                C3D_FIELD_PARAMETER_DESCRIPTIONS][C3D_FIELD_VALUE]
        self._platform_labels = {}
        label_index = 0
        for description in descriptions:
            if description.find("Force Plate") > 0:
                if not (description in self._platform_labels):
                    self._platform_labels[description] = label_index
                    label_index += 1

    def _get_platform_data(self, directions: list[str],
                           platform_labels: list[str],
                           data_label: str) -> pd.DataFrame:
        """
        Runs through all data of the specified platform label and directions
        and restructure it with dicts to a DataFrame

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed
        :param data_label: name of key for specific data in ezc3d.c3d structure
        :return: two-dimensional table of numpy arrays data
        """
        data_dict = {}
        for label_key in platform_labels:
            dir_dict = {}
            for dir_key in directions:
                dir_dict[dir_key] = \
                    self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_PLATFORM][
                        self._platform_labels[label_key]][data_label][
                        self._directions[dir_key]]
            data_dict[label_key] = dir_dict
        return pd.DataFrame(data_dict)
