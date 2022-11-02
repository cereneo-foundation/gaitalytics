import pandas as pd

C3D_FIELD_DATA = 'data'
C3D_FIELD_DATA_POINTS = 'points'
C3D_FIELD_DATA_PLATFORM = 'platform'
C3DF_FIELD_DATA_FORCE = 'force'

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

    def __init__(self, c3d_file):
        self._c3d_file = c3d_file
        self._point_labels = None
        self._platform_labels = None

    @property
    def c3d_file(self):
        return self._c3d_file

    @c3d_file.setter
    def set_c3d_file(self, c3d_file):
        self._c3d_file = c3d_file

    @property
    def point_labels(self):
        if self._point_labels is None:
            self._point_labels = self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_POINT][
                C3D_FIELD_PARAMETER_LABELS][C3D_FIELD_VALUE]
        return self._point_labels

    @property
    def platform_labels(self):
        if self._platform_labels is None:
            descriptions = \
                self._c3d_file[C3D_FIELD_PARAMETER][C3D_FIELD_PARAMETER_ANALOG][C3D_FIELD_PARAMETER_DESCRIPTIONS
                ][C3D_FIELD_VALUE]
            self._platform_labels = []
            for description in descriptions:
                if description.find("Force Plate") > 0:
                    if not (description in self._platform_labels):
                        self._platform_labels.append(description)

        return self._platform_labels

    @staticmethod
    def _convert_directions_to_column_numbers(directions):
        dir_columns = {}
        for direction in directions:
            if direction == DIRECTION_X:
                dir_columns[direction] = 0
            elif direction == DIRECTION_Y:
                dir_columns[direction] = 1
            elif direction == DIRECTION_Z:
                dir_columns[direction] = 2
        return dir_columns

    @staticmethod
    def _convert_labels_to_numbers(labels, c3d_labels):
        label_columns = {}
        for label in labels:
            index = c3d_labels.index(label)
            label_columns[label] = index
        return label_columns

    def get_points(self, labels, directions=[DIRECTION_X, DIRECTION_Y, DIRECTION_Z]):
        dir_columns = self._convert_directions_to_column_numbers(directions)
        label_columns = self._convert_labels_to_numbers(labels, self.point_labels)
        points_dict = {}
        for label_key in label_columns:
            dir_dict = {}
            for dir_key in dir_columns:
                dir_dict[dir_key] = self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_POINTS][dir_columns[dir_key]][
                    label_columns[label_key]]
            points_dict[label_key] = dir_dict
        return pd.DataFrame(points_dict)

    def get_platform_forces(self, platform_labels, directions=[DIRECTION_X, DIRECTION_Y, DIRECTION_Z]):
        dir_columns = self._convert_directions_to_column_numbers(directions)
        label_columns = self._convert_labels_to_numbers(platform_labels, self.platform_labels)
        force_dict = {}
        for label in label_columns:
            dir_dict = {}
            self._c3d_file[C3D_FIELD_DATA][C3D_FIELD_DATA_PLATFORM][label_columns[label]][C3DF_FIELD_DATA_FORCE]
