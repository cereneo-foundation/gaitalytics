import yaml

KEY_PLOT_MAPPING_DATA_TYPE = 'data_types'
KEY_PLOT_MAPPING_PLOTS = "plots"
KEY_PLOT_MAPPING = 'model_mapping_plot'
KEY_MARKER_MAPPING = "marker_set_mapping"
KEY_MARKER_MAPPING_R_HEEL = "right_heel"
KEY_MARKER_MAPPING_L_HEEL = "left_heel"
KEY_MARKER_MAPPING_R_HIP = "right_hip"
KEY_MARKER_MAPPING_L_HIP = "left_hip"


def read_configs(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)