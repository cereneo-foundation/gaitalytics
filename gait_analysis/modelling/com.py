from btk import btkAcquisition, btkPoint

from gait_analysis.event.utils import GaitEventContext
from gait_analysis.utils.config import MarkerModelConfig


class COMModeller:
    def init(self, configs: MarkerModelConfig):
        self._configs = configs

    def create_com(self, acq: btkAcquisition):
        l_hip_b = acq.GetPoint(self._configs.get_back_hip(GaitEventContext.LEFT)).GetValues()
        r_hip_b = acq.GetPoint(self._configs.get_back_hip(GaitEventContext.RIGHT)).GetValues()
        l_hip_f = acq.GetPoint(self._configs.get_front_hip(GaitEventContext.LEFT)).GetValues()
        r_hip_f = acq.GetPoint(self._configs.get_front_hip(GaitEventContext.RIGHT)).GetValues()

        com = (l_hip_b + r_hip_b + l_hip_f + r_hip_f) / 4
        acq.AppendPoint(btkPoint(com, btkPoint.Marker))

