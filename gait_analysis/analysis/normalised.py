from abc import ABC, abstractmethod
from statistics import mean

import numpy as np

from pandas import DataFrame, concat


class BaseNormalisedAnalysis(ABC):

    def __init__(self, data_list: {}):
        self.data_list = data_list

    @abstractmethod
    def _do_analysis(self, table: DataFrame) -> DataFrame:
        pass

    def analyse(self) -> DataFrame:
        results = None
        for key in self.data_list:
            table = self.data_list[key].data_table
            result = self._do_analysis(table)
            result['metric'] = key
            result['event_frame'] = self.data_list[key].get_event_frame()
            result['data_type'] = self.data_list[key].data_type
            if results is None:
                results = result
            else:
                results = concat([results, result])
        return results


class DescriptiveNormalisedAnalysis(BaseNormalisedAnalysis):

    def _do_analysis(self, table: DataFrame) -> DataFrame:
        frame_number = np.arange(1, 101, 1)  # Could be something like myRange = range(1,1000,1)
        result = DataFrame({"frame_number": frame_number})
        result['mean'] = table.mean(axis=0).to_list()
        result['sd'] = table.std(axis=0).to_list()
        result['max'] = table.max(axis=0).to_list()
        result['min'] = table.min(axis=0).to_list()
        result['median'] = table.median(axis=0).to_list()
        result['sd_up'] = result.apply(lambda row: row['mean'] + row['sd'], axis=1)
        result['sd_down'] = result.apply(lambda row: row['mean'] - row['sd'], axis=1)
        return result


