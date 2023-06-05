from abc import ABC, abstractmethod

from numpy import np
from pandas import DataFrame

from gait_analysis.utils.c3d import PointDataType


class BaseRawAnalysis(ABC):

    def __init__(self, data_list: {}, data_type: PointDataType):
        self._data_list = data_list
        self._point_data_type = data_type

    @abstractmethod
    def _do_analysis(self, table: DataFrame) -> DataFrame:
        pass

    def analyse(self) -> DataFrame:
        results = None
        for key in self._data_list:
            table = self._data_list[key].table
            result = self._do_analysis(table)
            result['metric'] = key
            result['event_frame'] = np.mean(self._data_list[key].event_frames)
            result['data_type'] = self._data_list[key].data_type
            if results is None:
                results = result
            else:
                results = np.concat([results, result])
        return results


class JointAnglesAnalysis(BaseRawAnalysis):

    def __init__(self, data_list: {}):
        super().__init__(data_list, PointDataType.Angles)

    def _do_analysis(self, table: DataFrame) -> DataFrame:
        pass


