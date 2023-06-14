import os
import re
from typing import List, Dict

from gait_analysis.cycle.extraction import BufferedRawCyclePoint, RawCyclePoint
from gait_analysis.cycle.normalisation import BufferedNormalisedCyclePoint, NormalisedCyclePoint
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.utils import POSTFIX_RAW, FILENAME_DELIMITER, get_key_from_filename, POSTFIX_NORM


class CyclePointLoader:

    def __init__(self, configs: ConfigProvider, dir_path: str):
        self._raw_cycle_data = {}
        self._norm_cycle_data = {}
        file_names = os.listdir(dir_path)
        postfix = POSTFIX_RAW
        raw_file_names = self._filter_filenames(file_names, postfix)
        for raw_file_name in raw_file_names:
            point = BufferedRawCyclePoint(configs, dir_path, raw_file_name)
            key = get_key_from_filename(raw_file_name)
            self._raw_cycle_data[key] = point

        postfix = POSTFIX_NORM
        norm_file_names = self._filter_filenames(file_names, postfix)
        for norm_file_name in norm_file_names:
            point = BufferedNormalisedCyclePoint(configs, dir_path, norm_file_name)
            key = get_key_from_filename(norm_file_name)
            self._norm_cycle_data[key] = point

    @staticmethod
    def _filter_filenames(file_names, postfix) -> List[str]:
        r = re.compile(f".*{FILENAME_DELIMITER}{postfix}.*\.csv")
        return list(filter(r.match, file_names))

    def get_raw_cycle_points(self) -> Dict[str, RawCyclePoint]:
        return self._raw_cycle_data

    def get_norm_cycle_points(self) -> Dict[str, NormalisedCyclePoint]:
        return self._norm_cycle_data
