from enum import Enum

import btk

ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


class PointDataType(Enum):
    Points = 0
    Angles = 1
    Forces = 2
    Moments = 3
    Power = 4

    @classmethod
    def get_type_by_index(cls, index):
        if index == 0:
            return cls.Points
        elif index == 1:
            return cls.Angles
        elif index == 2:
            return cls.Forces
        elif index == 3:
            return cls.Moments
        elif index == 4:
            return cls.Power

class AxesNames(Enum):
    x = 0
    y = 1
    z = 2

    @classmethod
    def get_axes_by_index(cls, index):
        if index == 0:
            return cls.x
        elif index == 1:
            return cls.y
        elif index == 2:
            return cls.z


def sort_events(acq):
    """
    sort events

    Args:
        acq (btkAcquisition): a btk acquisition instance

    """
    events = acq.GetEvents()

    value_frame = {}
    for event in btk.Iterate(events):
        if event.GetFrame() not in value_frame:
            value_frame[event.GetFrame()] = event

    sorted_keys = sorted(value_frame)

    newEvents = btk.btkEventCollection()
    for key in sorted_keys:
        newEvents.InsertItem(value_frame[key])


    acq.ClearEvents()
    acq.SetEvents(newEvents)


def read_btk(filename):
    """
    read a c3d with btk

    Args:
        filename (str): filename with its path
    """
    reader = btk.btkAcquisitionFileReader()
    reader.SetFilename(filename)
    reader.Update()
    acq = reader.GetOutput()

    # sort events
    sort_events(acq)

    return acq


def write_btk(acq, filename):
    """
    write a c3d with Btk

    Args:
        acq (btk.acquisition): a btk acquisition instance
        filename (str): filename with its path
    """
    writer = btk.btkAcquisitionFileWriter()
    writer.SetInput(acq)
    writer.SetFilename(filename)
    writer.Update()
