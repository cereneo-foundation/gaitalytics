from abc import ABC, abstractmethod
from statistics import mean

import numpy as np

from pandas import DataFrame, concat


class BaseNormalisedAnalysis(ABC):

    def __init__(self, data_list: {}):
        self.data_list = data_list

    @abstractmethod
    def _do_magic(self, table: DataFrame) -> {}:
        pass

    def analyse(self) -> DataFrame:
        results = None
        for key in self.data_list:
            table = self.data_list[key].table
            result = self._do_magic(table)
            result['metric'] = key
            result['event_frame'] = mean(self.data_list[key].event_frames)
            if results is None:
                results = result
            else:
                results = results.append(result)
        return results


class DescriptiveNormalisedAnalysis(BaseNormalisedAnalysis):

    def _do_magic(self, table: DataFrame) -> DataFrame:
        frame_number = np.arange(1, 101, 1)  # Could be something like myRange = range(1,1000,1)
        numbers = DataFrame({"frame_number": frame_number})
        mean = table.mean(axis=0).to_frame('mean')
        sd = table.std(axis=0).to_frame('sd')
        maximum = table.max(axis=0).to_frame('max')
        minimum = table.min(axis=0).to_frame('min')
        median = table.median(axis=0).to_frame('median')

        result = concat([numbers, mean, sd, maximum, minimum, median], axis=1)
        result['sd_up'] = result.apply(lambda row: row['mean'] + row['sd'], axis=1)
        result['sd_down'] = result.apply(lambda row: row['mean'] - row['sd'], axis=1)
        return result
