import os
import re
from typing import List, Dict

from gait_analysis.cycle.extraction import BufferedCyclePoint, BasicCyclePoint
from gait_analysis.utils.config import ConfigProvider
from gait_analysis.utils.utils import FILENAME_DELIMITER, get_key_from_filename


class CyclePointLoader:

    def __init__(self, configs: ConfigProvider, dir_path: str):
        self._raw_cycle_data = {}
        self._norm_cycle_data = {}
        file_names = os.listdir(dir_path)
        postfix = BasicCyclePoint.TYPE_RAW
        raw_file_names = self._filter_filenames(file_names, postfix)

        self._raw_cycle_data = self._init_buffered_points(configs, dir_path, raw_file_names)

        postfix = BasicCyclePoint.TYPE_NORM
        norm_file_names = self._filter_filenames(file_names, postfix)
        self._norm_cycle_data = self._init_buffered_points(configs, dir_path, norm_file_names)

    def _init_buffered_points(self, configs, dir_path, file_names) -> Dict[str, BasicCyclePoint]:
        cycle_data: Dict[str, BasicCyclePoint] = {}
        for file_name in file_names:
            point = BufferedCyclePoint(configs, dir_path, file_name)
            foo, key, foo = get_key_from_filename(file_name)
            cycle_data[key] = point
        return cycle_data

    @staticmethod
    def _filter_filenames(file_names, postfix) -> List[str]:
        r = re.compile(f".*{FILENAME_DELIMITER}{postfix}.*\.csv")
        return list(filter(r.match, file_names))

    def get_raw_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._raw_cycle_data

    def get_norm_cycle_points(self) -> Dict[str, BasicCyclePoint]:
        return self._norm_cycle_data
