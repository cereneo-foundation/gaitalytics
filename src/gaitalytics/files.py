from abc import ABC, abstractmethod
from statistics import mean
from typing import List, Dict, Union

import btk

import gaitalytics.utils

ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


def is_progression_axes_flip(left_heel, left_toe):
    return 0 < mean(left_toe[gaitalytics.utils.AxesNames.y.value] - left_heel[gaitalytics.utils.AxesNames.y.value])


class FileHandler(ABC):
    def __init__(self, file_path: str):
        self._file_path = file_path
        self.read_file()

    def sort_events(self):
        """
        sort events in acquisition
        """
        events = self.get_events()

        value_frame: Dict[int, gaitalytics.utils.GaitEvent] = {}

        for index in range(0, len(events)):
            if events[index].frame not in value_frame:
                value_frame[events[index].frame] = events[index]

        sorted_keys: Dict[int, gaitalytics.utils.GaitEvent] = dict(sorted(value_frame.items()))

        self.clear_events()
        self.set_events(list(sorted_keys.values()))

    @abstractmethod
    def read_file(self):
        pass

    def write_file(self, out_file_path=None):
        if out_file_path is None:
            out_file_path = self._file_path
        self._write_file(out_file_path)

    @abstractmethod
    def _write_file(self, out_file_path: str):
        pass

    @abstractmethod
    def get_events_size(self) -> int:
        pass

    @abstractmethod
    def get_events(self) -> List[gaitalytics.utils.GaitEvent]:
        pass

    @abstractmethod
    def set_events(self, events: List[gaitalytics.utils.GaitEvent]):
        pass

    @abstractmethod
    def get_event(self, index: int) -> gaitalytics.utils.GaitEvent:
        pass

    @abstractmethod
    def add_event(self, event: gaitalytics.utils.GaitEvent):
        pass

    @abstractmethod
    def clear_events(self):
        pass

    @abstractmethod
    def get_point_frequency(self) -> int:
        pass

    @abstractmethod
    def get_actual_start_frame(self) -> int:
        pass

    @abstractmethod
    def get_subject_measures(self) -> gaitalytics.utils.SubjectMeasures:
        pass

    @abstractmethod
    def get_points_size(self) -> int:
        pass

    @abstractmethod
    def get_point(self, marker_index: Union[int, str]) -> gaitalytics.utils.Point:
        pass

    @abstractmethod
    def add_point(self, new_point: gaitalytics.utils.Point):
        pass


class BtkFileHandler(FileHandler):

    def __init__(self, file_path: str):
        self._aqc = None
        super().__init__(file_path)

    @property
    def aqc(self):
        return self._aqc

    @aqc.setter
    def aqc(self, aqc):
        self._aqc = aqc

    def get_subject_measures(self) -> gaitalytics.utils.SubjectMeasures:
        body_mass = self._aqc.GetMetaData().GetChild("PROCESSING").GetChild("Bodymass").GetInfo().ToDouble()[0]
        body_height = self._aqc.GetMetaData().GetChild("PROCESSING").GetChild("Height").GetInfo().ToDouble()[0]
        left_leg_length = self._aqc.GetMetaData().GetChild("PROCESSING").GetChild("LLegLength").GetInfo().ToDouble()[0]
        right_leg_length = self._aqc.GetMetaData().GetChild("PROCESSING").GetChild("RLegLength").GetInfo().ToDouble()[0]
        name = self._aqc.GetMetaData().GetChild("SUBJECTS").GetChild("NAMES").GetInfo().ToString()[0].strip()
        start_frame = self._aqc.GetMetaData().GetChild("TRIAL").GetChild("ACTUAL_START_FIELD").GetInfo().ToInt()[0]
        subject = gaitalytics.utils.SubjectMeasures(body_mass, body_height, left_leg_length, right_leg_length, name,
                                                    start_frame)
        return subject

    def _write_file(self, out_file_path: str):
        """
        write a c3d with Btk

        Args:
            out_file_path (str): filename with its path
        """
        writer = btk.btkAcquisitionFileWriter()
        writer.SetInput(self._aqc)
        writer.SetFilename(out_file_path)
        writer.Update()

    def read_file(self):
        """
        read a c3d with btk
        """
        reader = btk.btkAcquisitionFileReader()
        reader.SetFilename(self._file_path)
        reader.Update()
        self._aqc = reader.GetOutput()

        # sort events
        self.sort_events()

    def get_events_size(self) -> int:
        return self._aqc.GetEventNumber()

    def get_events(self) -> List[gaitalytics.utils.GaitEvent]:
        events: List[gaitalytics.utils.GaitEvent] = []
        for event in btk.Iterate(self._aqc.GetEvents()):
            events.append(self.map_btk_event(event))
        return events

    def set_events(self, events: List[gaitalytics.utils.GaitEvent]):
        new_events = btk.btkEventCollection()
        for gait_event in events:
            new_events.InsertItem(self.map_event(gait_event))

        self._aqc.SetEvents(new_events)

    def get_event(self, index: int) -> gaitalytics.utils.GaitEvent:
        btk_event = self._aqc.GetEvent(index)
        return self.map_btk_event(btk_event)

    def clear_events(self):
        self._aqc.ClearEvents()

    def add_event(self, event: gaitalytics.utils.GaitEvent):
        self._aqc.AppendEvent(self.map_event(event))

    def get_point_frequency(self) -> int:
        return self._aqc.GetPointFrequency()

    def get_actual_start_frame(self) -> int:
        return self._aqc.GetMetaData().GetChild("TRIAL").GetChild("ACTUAL_START_FIELD").GetInfo().ToInt()[0] - 1

    def get_point(self, marker_index: Union[int, str]) -> gaitalytics.utils.Point:
        return self.map_btk_point(self._aqc.GetPoint(marker_index))

    def get_points_size(self) -> int:
        return self._aqc.GetPointNumber()

    def add_point(self, new_point: gaitalytics.utils.Point):
        point = btk.btkPoint(new_point.type.value)
        point.SetValues(new_point.values)
        point.SetLabel(new_point.label)
        self._aqc.AppendPoint(point)

    def map_btk_event(self, btk_event: btk.btkEvent) -> gaitalytics.utils.GaitEvent:
        gait_event = gaitalytics.utils.GaitEvent(self.get_actual_start_frame(), self.get_point_frequency())
        gait_event.time = btk_event.GetTime()
        gait_event.context = btk_event.GetContext()
        gait_event.subject = btk_event.GetSubject()
        gait_event.icon_id = btk_event.GetId()
        gait_event.description = btk_event.GetDescription()
        gait_event.generic_flag = btk_event.GetDetectionFlags()
        gait_event.label = btk_event.GetLabel()
        return gait_event

    @staticmethod
    def map_event(gait_event: gaitalytics.utils.GaitEvent) -> btk.btkEvent:
        btk_event = btk.btkEvent()
        btk_event.SetTime(gait_event.time)
        btk_event.SetContext(gait_event.context)
        btk_event.SetSubject(gait_event.subject)
        btk_event.SetId(gait_event.icon_id)
        btk_event.SetDescription(gait_event.description)
        btk_event.SetDetectionFlags(gait_event.generic_flag)
        btk_event.SetLabel(gait_event.label)
        return btk_event

    @staticmethod
    def map_btk_point(btk_point: btk.btkPoint):
        point = gaitalytics.utils.Point()
        point.values = btk_point.GetValues()
        point.label = btk_point.GetLabel()
        point.residuals = btk_point.GetResiduals()
        point.type = gaitalytics.utils.PointDataType(btk_point.GetType())
        return point
