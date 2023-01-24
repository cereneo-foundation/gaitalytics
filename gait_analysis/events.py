from abc import ABC, abstractmethod

import numpy
from btk import btkAcquisition, btkEvent, btkForcePlatformsExtractor, btkGroundReactionWrenchFilter
from pyCGM2.Tools import btkTools
from pyCGM2.Events import eventFilters, eventProcedures

from pyCGM2.Signal import detect_onset
from pyCGM2.Signal import signal_processing
from gait_analysis.utils import FS_or_FO


class AbstractGaitEventDetector(ABC):

    @abstractmethod
    def detect_events(self, acq: btkAcquisition):
        pass

    @staticmethod
    def clear_events(self, bkt_acq: btkAcquisition, event_names: list = None):
        if event_names is None:
            bkt_acq.ClearEvents()
        else:
            btkTools.clearEvents(btkAcquisition, event_names)


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

    def __init__(self, mappedFP: str = 'LR', weight_threshold: int = 10):
        """ Initializes Object
        Args:
             mappedForcePlate (str): letters indicated foot assigned to a force plate (eg LR)
        """
        self._mappedFP = mappedFP
        self._weight_threshold = weight_threshold

    def addForcePlateGeneralEvents_Cefir(self, btkAcq: btkAcquisition):
        """add maximum force plate as general event
        Args:
            btkAcq (btk.acquisition): btk acquisition instance
            mappedForcePlate (str): letters indicated foot assigned to a force plate (eg LR, for FP1=Left & FP2=Right)

        Adapted from pyCGM2 forceplates.py
        """
        ff = btkAcq.GetFirstFrame()
        lf = btkAcq.GetLastFrame()
        pf = btkAcq.GetPointFrequency()
        appf = btkAcq.GetNumberAnalogSamplePerFrame()

        # --- ground reaction force wrench ---
        pfe = btkForcePlatformsExtractor()
        grwf = btkGroundReactionWrenchFilter()

        # Filter the FP signal
        signal_processing.forcePlateFiltering(btkAcq)
        # --
        pfe.SetInput(btkAcq)
        pfc = pfe.GetOutput()
        grwf.SetInput(pfc)
        grwc = grwf.GetOutput()
        grwc.Update()

        # remove force plates events
        #

        # add general events
        indexFP = 0
        for letter in self._mappedFP:

            force = grwc.GetItem(indexFP).GetForce().GetValues()
            force_downsample = force[0:(lf - ff + 1) * appf:appf][:, 2]  # downsample

            detection = detect_onset.detect_onset(force_downsample, threshold=self._weight_threshold)
            sequence = FS_or_FO(force_downsample, detection)  # return array of ["Label event":str,index of event:int]
            if letter == "L":
                for elem in sequence:
                    type_event = elem[0]
                    indx_event = elem[1]

                    ev = btkEvent(type_event, (indx_event - 1) / pf, 'Left', btkEvent.Automatic, '',
                                  'event from Force plate assignment')
                    btkAcq.AppendEvent(ev)
            elif letter == "R":
                for elem in sequence:
                    type_event = elem[0]
                    indx_event = elem[1]

                    ev = btkEvent(type_event, (indx_event - 1) / pf, 'Right', btkEvent.Automatic, '',
                                  'event from Force plate assignment')
                    btkAcq.AppendEvent(ev)

            indexFP += 1

    def detect_events(self, acq: btkAcquisition):
        """
        detects gait events and stores it in to the acquisition
        Args:
            acq: acquisition read from btk c3d
        """
        self.addForcePlateGeneralEvents_Cefir(acq)


class GaitEventDetectorFactory(object):

    def __init__(self):
        self._zenis = None
        self._force_plate = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GaitEventDetectorFactory, cls).__new__(cls)
        return cls.instance

    def get_zenis_detector(self) -> AbstractGaitEventDetector:
        if self._zenis is None:
            self._zenis = ZenisGaitEventDetector()
        return self._zenis

    def get_force_plate_detector(self) -> AbstractGaitEventDetector:
        if self._force_plate is None:
            self._force_plate = ForcePlateEventDetection()
        return self._force_plate
