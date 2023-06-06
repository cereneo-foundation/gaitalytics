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
    _MARKER_MAPPING_R_META_HEAD_2 = "right_meta_2"
    _MARKER_MAPPING_L_META_HEAD_2 = "left_meta_2"
    _MARKER_MAPPING_R_META_HEAD_5 = "right_meta_5"
    _MARKER_MAPPING_L_META_HEAD_5 = "left_meta_5"
    _MARKER_MAPPING_L_LAT_MALLEOLI = "left_lat_malleoli"
    _MARKER_MAPPING_R_LAT_MALLEOLI = "right_lat_malleoli"
    _MARKER_MAPPING_L_MED_MALLEOLI = "left_med_malleoli"
    _MARKER_MAPPING_R_MED_MALLEOLI = "right_med_malleoli"

    _MODEL_MAPPING = "model_mapping"
    _MODEL_MAPPING_COM = "com"
    _MODEL_MAPPING_L_GRF = "left_GRF"
    _MODEL_MAPPING_R_GRF = "right_GRF"

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

    def get_meta_2(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_META_HEAD_2]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_META_HEAD_2]

    def get_meta_5(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_META_HEAD_5]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_META_HEAD_5]

    def get_com(self):
        return self._config[self._MODEL_MAPPING][self._MODEL_MAPPING_COM]

    def get_ground_reaction_force(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MODEL_MAPPING][self._MODEL_MAPPING_L_GRF]
        else:
            return self._config[self._MODEL_MAPPING][self._MODEL_MAPPING_R_GRF]

    def get_lateral_malleoli(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_LAT_MALLEOLI]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_LAT_MALLEOLI]

    def get_medial_malleoli(self, side: GaitEventContext):
        if side == GaitEventContext.LEFT:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_L_MED_MALLEOLI]
        else:
            return self._config[self._MARKER_MAPPING][self._MARKER_MAPPING_R_MED_MALLEOLI]

    def read_configs(self, file_path: str):
        with open(file_path, 'r') as f:
            self._config = yaml.safe_load(f)
