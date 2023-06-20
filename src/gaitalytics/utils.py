from __future__ import annotations

from enum import Enum

import yaml

from . import cycle


def min_max_norm(data):
    scale_min = -1
    scale_max = 1
    max_data = max(data)
    min_data = min(data)
    diff = max_data - min_data
    return [((entry - min_data) * (scale_max - scale_min) / diff) + scale_min for entry in data]


class ConfigProvider:
    _MARKER_MAPPING = "marker_set_mapping"
    _MODEL_MAPPING = "model_mapping"

    def __init__(self, file_path: str):
        self._read_configs(file_path)
        self.MARKER_MAPPING = Enum('MarkerMapping', self._config[self._MARKER_MAPPING])
        self.MODEL_MAPPING = Enum('ModelMapping', self._config[self._MODEL_MAPPING])

    def get_translated_label(self, label: str, point_type: cycle.PointDataType):
        try:
            if point_type == cycle.PointDataType.Marker:
                return self.MARKER_MAPPING(label)
            else:
                return self.MODEL_MAPPING(label)
        except ValueError as e:
            return None

    def _read_configs(self, file_path: str):
        with open(file_path, 'r') as f:
            self._config = yaml.safe_load(f)

    @staticmethod
    def define_key(translated_label: Enum, point_type: cycle.PointDataType, direction: cycle.AxesNames,
                   side: cycle.GaitEventContext) -> str:
        if translated_label is not None:
            return f"{translated_label.name}.{point_type.name}.{direction.name}.{side.value}"
