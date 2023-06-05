import yaml

from gait_analysis.event.utils import GaitEventContext

KEY_PLOT_MAPPING_DATA_TYPE = 'data_types'
KEY_PLOT_MAPPING_PLOTS = "plots"
KEY_PLOT_MAPPING = 'model_mapping_plot'


class MarkerModelConfig:
    _MARKER_MAPPING = "marker_set_mapping"
    _MARKER_MAPPING_R_HEEL = "right_heel"
    _MARKER_MAPPING_L_HEEL = "left_heel"
    _MARKER_MAPPING_R_HIP_FRONT = "right_front_hip"
    _MARKER_MAPPING_L_HIP_FRONT = "left_front_hip"
    _MARKER_MAPPING_R_HIP_BACK = "right_back_hip"
    _MARKER_MAPPING_L_HIP_BACK = "left_back_hip"

    def __init__(self):
        self._config = None

    def get_heel(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_HEEL]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_HEEL]

    def get_front_hip(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_HIP_FRONT]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_HIP_FRONT]

    def get_back_hip(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_HIP_BACK]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_HIP_BACK]

    def read_configs(self, file_path: str):
        with open(file_path, 'r') as f:
            self._config = yaml.safe_load(f)
