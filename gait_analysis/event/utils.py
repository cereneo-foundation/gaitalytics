from enum import Enum

from btk import btkAcquisition, btkEvent


class GaitEventLabel(Enum):
    FOOT_STRIKE = "Foot Strike"
    FOOT_OFF = "Foot Off"

    @classmethod
    def get_contrary_event(cls, event_label: str):
        if event_label == cls.FOOT_STRIKE.value:
            return cls.FOOT_OFF
        return cls.FOOT_STRIKE

    @classmethod
    def get_type_id(cls, event_label: str):
        if event_label == cls.FOOT_STRIKE.value:
            return 1
        return 2


class GaitContext(Enum):
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def get_contrary_context(cls, context: str):
        if context == cls.LEFT.value:
            return cls.RIGHT
        return cls.LEFT


def find_next_event(acq: btkAcquisition, label: str, context, start_index: int) -> [btkEvent, btkEvent]:
    if acq.GetEventNumber() >= start_index + 1:
        for event_index in range(start_index + 1, acq.GetEventNumber()):
            event = acq.GetEvent(event_index)
            if event.GetContext() == context:
                if event.GetLabel() == label:
                    return [event, unused_event]
                else:
                    unused_event = event
    raise IndexError()