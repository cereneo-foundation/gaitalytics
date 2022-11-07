import ezc3d
import pandas as pd

C3D_FIELD_DATA = 'data'
C3D_FIELD_DATA_POINTS = 'points'
C3D_FIELD_DATA_PLATFORM = 'platform'
C3D_FIELD_DATA_FORCE = 'force'
C3D_FIELD_DATA_MOMENT = 'moment'
C3D_FIELD_DATA_COP = 'center_of_pressure'

C3D_FIELD_PARAMETER = 'parameters'
C3D_FIELD_PARAMETER_POINT = 'POINT'
C3D_FIELD_PARAMETER_ANALOG = 'ANALOG'
C3D_FIELD_PARAMETER_LABELS = 'LABELS'
C3D_FIELD_PARAMETER_DESCRIPTIONS = 'DESCRIPTIONS'

C3D_FIELD_VALUE = 'value'

DIRECTION_Z = 'z'
DIRECTION_Y = 'y'
DIRECTION_X = 'x'


class C3dFileWrapper:
    """This wrapper class simplifies the usage of ezc3d.

    This wrapper class can be used to read data without deep knowledge of the c3d-file structure and
    integrates nicely with the gait library
    """

    def __init__(self, c3d_file: ezc3d.c3d):
        """Initialises caches and stores c3d object

        :param c3d_file: c3d object loaded from 3D-motion-capture system file
        """
        self.c3d_file = c3d_file
        self._directions = {DIRECTION_X: 0, DIRECTION_Y: 1, DIRECTION_Z: 2}

    @property
    def c3d_file(self) -> ezc3d.c3d:
        """returns stored c3d object

        :return: stored c3d object
        :rtype: ezc3d.c3d
        """
        return self._c3d_file

    @c3d_file.setter
    def c3d_file(self, c3d_file: ezc3d.c3d):
        """Stores c3d object and re-initialized cache

        :param c3d_file: c3d object loaded from 3D-motion-capture system file
        """
        self._c3d_file = c3d_file
        self._init_point_labels()
        self._init_platform_labels()

    def get_point_labels(self) -> list[str]:
        """Returns list of available point labels from c3d file

        :return: list of point labels
        """
        return list(self._point_labels.keys())

    def get_platform_labels(self) -> list[str]:
        """Returns list of available platform labels from c3d file

        :return: list of platform labels
        """
        return list(self._platform_labels.keys())

    def get_points(self, labels: list[str], directions: list[str] = None) \
            -> pd.DataFrame:
        """Returns point data.

        :param labels: point labels for which the data is needed
        :param directions: direction names of which the data is needed, Default = ['x','y','z']
        :return: two-dimensional table of numpy arrays with requested point labels in columns and directions in row
        """
        if directions is None:
            directions = [DIRECTION_X, DIRECTION_Y, DIRECTION_Z]
        points_dict = {}
        for label_key in labels:
            dir_dict = {}
            for dir_key in directions:
                dir_dict[dir_key] = self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_POINTS][self._directions[dir_key]][
                    self._point_labels[label_key]]
            points_dict[label_key] = dir_dict
        return pd.DataFrame(points_dict)

    def get_platform_forces(self, platform_labels: list[str], directions: list[str] = None) -> pd.DataFrame:
        """Returns platform force data

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed, Default = ['x','y','z']
        :return: two-dimensional table of numpy arrays with requested platform labels in columns and directions in row
        """
        if directions is None:
            directions = [DIRECTION_X, DIRECTION_Y, DIRECTION_Z]
        return self._get_platform_data(directions, platform_labels, C3D_FIELD_DATA_FORCE)

    def get_platform_moments(self, platform_labels: list[str], directions: list[str] = None) -> pd.DataFrame:
        """Returns platform moments data

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed, Default = ['x','y','z']
        :return: two-dimensional table of numpy arrays with requested platform labels in columns and directions in row
        """
        if directions is None:
            directions = [DIRECTION_X, DIRECTION_Y, DIRECTION_Z]
        return self._get_platform_data(directions, platform_labels, C3D_FIELD_DATA_MOMENT)

    def get_platform_cop(self, platform_labels: list[str], directions: list[str] = None) -> pd.DataFrame:
        """Returns platform center of pressure data

        :param platform_labels: platform labels for which the data is needed
        :type platform_labels: list[str]
        :param directions: direction names of which the data is needed, Default = ['x','y','z']
        :return: two-dimensional table of numpy arrays with requested platform labels in columns and directions in row
        """
        if directions is None:
            directions = [DIRECTION_X, DIRECTION_Y, DIRECTION_Z]
        return self._get_platform_data(directions, platform_labels, C3D_FIELD_DATA_COP)

    def _init_point_labels(self):
        """Caches point labels in self._point_labels"""
        c3d_labels = self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_POINT][C3D_FIELD_PARAMETER_LABELS][
            C3D_FIELD_VALUE]
        self._point_labels = {}
        for label in c3d_labels:
            index = c3d_labels.index(label)
            self._point_labels[label] = index

    def _init_platform_labels(self):
        """Caches platform labels in self._platform_labels
        Loops through all analog labels and checks for "Force Plate" in label. Checks if label already exists
         in tuple and saves it in cache tuple"""
        descriptions = self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_ANALOG][
            C3D_FIELD_PARAMETER_DESCRIPTIONS][C3D_FIELD_VALUE]
        self._platform_labels = {}
        label_index = 0
        for description in descriptions:
            if description.find("Force Plate") > 0:
                if not (description in self._platform_labels):
                    self._platform_labels[description] = label_index
                    label_index += 1

    def _get_platform_data(self, directions: list[str], platform_labels: list[str], data_label: str) -> pd.DataFrame:
        """returns platform data of requested platforms and directions for specific data

        Runs through all data of the specified platform label and directions and restructure it with tuples to
        a dict

        :param platform_labels: platform labels for which the data is needed
        :param directions: direction names of which the data is needed
        :param data_label: name of key for specific data in ezc3d.c3d structure
        :return: two-dimensional table of numpy arrays with requested platform labels in columns and directions in row
        """
        data_dict = {}
        for label_key in platform_labels:
            dir_dict = {}
            for dir_key in directions:
                dir_dict[dir_key] = self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_PLATFORM][
                    self._platform_labels[label_key]][data_label][self._directions[dir_key]]
            data_dict[label_key] = dir_dict
        return pd.DataFrame(data_dict)
