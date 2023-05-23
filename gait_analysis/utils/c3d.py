from enum import Enum
import btk


class DataType(Enum):
    Angles = 1
    Moments = 2
    Power = 3


class AxesNames(Enum):
    X = "x"
    Y = "y"
    Z = "z"

    @classmethod
    def get_axes_by_index(cls, index):
        if index == 0:
            return cls.X
        elif index == 1:
            return cls.Y
        elif index == 2:
            return cls.Z


ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


class SideEnum(Enum):
    """
    Helper enum to define side
    """
    LEFT = "L"
    RIGHT = "R"


def sorted_events(acq):
    """
    sort events

    Args
        acq (btkAcquisition): a btk acquisition instance

    """
    evs = acq.GetEvents()

    contextLst = []  # recuperation de tous les contextes
    for it in btk.Iterate(evs):
        if it.GetContext() not in contextLst:
            contextLst.append(it.GetContext())

    valueFrame = []  # recuperation de toutes les frames SANS doublons
    for it in btk.Iterate(evs):
        if it.GetFrame() not in valueFrame:
            valueFrame.append(it.GetFrame())
    valueFrame.sort()  # trie

    events = []
    for frame in valueFrame:
        for it in btk.Iterate(evs):
            if it.GetFrame() == frame:
                events.append(it)

    newEvents = btk.btkEventCollection()
    for ev in events:
        newEvents.InsertItem(ev)

    acq.ClearEvents()
    acq.SetEvents(newEvents)


def read_btk(filename):
    """
    Convenient function to read a c3d with Btk

    Args:
        filename (str): filename with its path
    """
    reader = btk.btkAcquisitionFileReader()
    reader.SetFilename(filename)
    reader.Update()
    acq = reader.GetOutput()

    # sort events
    sorted_events(acq)

    return acq


def write_btk(acq, filename):
    """
    Convenient function to write a c3d with Btk

    Args:
        acq (btk.acquisition): a btk acquisition instance
        filename (str): filename with its path
    """
    writer = btk.btkAcquisitionFileWriter()
    writer.SetInput(acq)
    writer.SetFilename(filename)
    writer.Update()
