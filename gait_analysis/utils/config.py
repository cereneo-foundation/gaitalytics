from enum import Enum

import yaml

from gait_analysis.utils.c3d import AxesNames, PointDataType, GaitEventContext

KEY_PLOT_MAPPING_DATA_TYPE = 'data_types'
KEY_PLOT_MAPPING_PLOTS = "plots"
KEY_PLOT_MAPPING = 'model_mapping_plot'

class ConfigProvider:
    _MARKER_MAPPING = "marker_set_mapping"
    _MODEL_MAPPING = "model_mapping"

    def __init__(self):
        self._config = None
        self.MARKER_MAPPING = None
        self.MODEL_MAPPING = None

    def get_translated_label(self, label: str, direction: AxesNames, point_type: PointDataType):
        try:
            if point_type == PointDataType.Marker:
                return self.MARKER_MAPPING(label)
            else:
                return self.MODEL_MAPPING(f"{label}.{direction.name}")
        except ValueError as e:
            return None

    def read_configs(self, file_path: str):
        with open(file_path, 'r') as f:
            self._config = yaml.safe_load(f)
        self.MARKER_MAPPING = Enum('MarkerMapping', self._config[self._MARKER_MAPPING])
        self.MODEL_MAPPING = Enum('ModelMapping', self._config[self._MODEL_MAPPING])
