from abc import ABC, abstractmethod
from btk import btkAcquisition
from pyCGM2.Events import eventFilters, eventProcedures
from pyCGM2.ForcePlates import forceplates

class AbstractGaitEventDetector(ABC):

    @abstractmethod
    def detect_events(self, acq: btkAcquisition):
        pass


class ZenisGaitEventDetector(AbstractGaitEventDetector):
    """
    This class detects gait events from cgm2 model data
    """

    def __init__(self, foot_strike_offset: int = 0, foot_off_offset: int = 0):
        """ Initializes Object
        Args:
            foot_strike_offset: numbers of frames to offset next foot strike event
            foot_off_offset: number of frames to offset next foot off event
        """
        self._foot_strike_offset = foot_strike_offset
        self._foot_off_offset = foot_off_offset

    def detect_events(self, acq: btkAcquisition):
        """
        detects gait events and stores it in to the acquisition
        Args:
            acq: acquisition read from btk c3d
        """
        evp = eventProcedures.ZeniProcedure()
        evp.setFootOffOffset(self._foot_off_offset)
        evp.setFootStrikeOffset(self._foot_strike_offset)
        evf = eventFilters.EventFilter(evp, acq)
        evf.detect()


class ForcePlateEventDetection(AbstractGaitEventDetector):
    """
    This class detects gait events from Force Plate signal
    """

    def __init__(self, mappedFP : string ='LRX'):
        """ Initializes Object
        Args:
             mappedForcePlate (str): letters indicated foot assigned to a force plate (eg LRX)
        """
        self._mappedFP = mappedFP

    def detect_events(self, acq: btkAcquisition):
        """
        detects gait events and stores it in to the acquisition
        Args:
            acq: acquisition read from btk c3d
        """
        forceplates.addForcePlateGeneralEvents(acq,self._mappedFP)

class GaitEventDetectorFactory(object):

    def __init__(self):
        self._zenis = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GaitEventDetectorFactory, cls).__new__(cls)
        return cls.instance

    def get_zenis_detector(self) -> AbstractGaitEventDetector:
        if self._zenis is None:
            self._zenis = ZenisGaitEventDetector()
        return self._zenis
