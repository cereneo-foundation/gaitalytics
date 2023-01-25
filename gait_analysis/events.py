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

    def __init__(self, mapped_fp: str = 'LR', weight_threshold: int = 10):
        """ Initializes Object
        Args:
             mappedForcePlate (str): letters indicated foot assigned to a force plate (eg LR)
        """
        self._mapped_fp = mapped_fp
        self._weight_threshold = weight_threshold

    def addforceplategeneralevents_cefir(self, btk_acq: btkAcquisition):
        """add maximum force plate as general event
        Args:
            btk_acq (btk.acquisition): btk acquisition instance

        Adapted from pyCGM2 forceplates.py
        """
        first_frame = btk_acq.GetFirstFrame()
        last_frame = btk_acq.GetLastFrame()
        freq = btk_acq.GetPointFrequency()
        analog_sample_per_frame = btk_acq.GetNumberAnalogSamplePerFrame()

        # --- ground reaction force wrench ---
        fp_extractor = btkForcePlatformsExtractor()
        ground_reaction = btkGroundReactionWrenchFilter()

        # Filter the FP signal
        signal_processing.forcePlateFiltering(btk_acq)
        # --
        fp_extractor.SetInput(btk_acq)
        fp_collection = fp_extractor.GetOutput()
        ground_reaction.SetInput(fp_collection)
        ground_reaction_collection = ground_reaction.GetOutput()
        ground_reaction_collection.Update()

        # remove force plates events
        #

        # add general events
        index_fp = 0
        for letter in self._mapped_fp:

            force = ground_reaction_collection.GetItem(index_fp).GetForce().GetValues()
            force_downsample = force[0:(last_frame - first_frame + 1) * analog_sample_per_frame:analog_sample_per_frame][:, 2]  # down sample

            detection = detect_onset.detect_onset(force_downsample, threshold=self._weight_threshold)
            sequence = FS_or_FO(force_downsample, detection)  # return array of ["Label event":str,index of event:int]
            if letter == "L":
                for elem in sequence:
                    type_event = elem[0]
                    index_event = elem[1]

                    ev = btkEvent(type_event, (index_event - 1) / freq, 'Left', btkEvent.Automatic, '',
                                  'event from Force plate assignment')
                    btk_acq.AppendEvent(ev)
            elif letter == "R":
                for elem in sequence:
                    type_event = elem[0]
                    index_event = elem[1]

                    ev = btkEvent(type_event, (index_event - 1) / freq, 'Right', btkEvent.Automatic, '',
                                  'event from Force plate assignment')
                    btk_acq.AppendEvent(ev)

            index_fp += 1

    def detect_events(self, acq: btkAcquisition):
        """
        detects gait events and stores it in to the acquisition
        Args:
            acq: acquisition read from btk c3d
        """
        self.addforceplategeneralevents_cefir(acq)


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
