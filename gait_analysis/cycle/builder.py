from abc import ABC, abstractmethod
from btk import btkAcquisition, btkEvent
from typing import List
from gait_analysis.event.utils import GaitEventLabel, GaitContext, find_next_event

from gait_analysis.event.anomaly import EventAnomalyChecker


class GaitCycle:

    def __init__(self, number: int, context: str, start_frame: int, end_frame: int, unused_events: List[btkEvent]):
        self.number = number
        self.context = context
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.unusedEvents = unused_events


class CycleBuilder(ABC):

    def __init__(self, eventAnomalyChecker: EventAnomalyChecker):
        self.eventAnomalyChecker = eventAnomalyChecker

    def build_cycles(self, aqc: btkAcquisition) -> List[GaitCycle]:
        [detected, detail_tuple] = self.eventAnomalyChecker.check_events(aqc)
        if detected:
            raise RuntimeError(detail_tuple)

        return self._build(aqc)

    @abstractmethod
    def _build(self, acq: btkAcquisition) -> {}:
        pass


class EventCycleBuilder(CycleBuilder):
    def __init__(self, eventAnomalyChecker: EventAnomalyChecker, event: GaitEventLabel):
        super().__init__(eventAnomalyChecker)
        self.event_label = event.value

    def _build(self, acq: btkAcquisition) -> {}:
        gait_cycles = {GaitContext.LEFT.value: [],
                       GaitContext.RIGHT.value: []}
        numbers = {GaitContext.LEFT.value: 0,
                   GaitContext.RIGHT.value: 0}
        for event_index in range(0, acq.GetEventNumber()):
            start_event = acq.GetEvent(event_index)
            context = start_event.GetContext()
            label = start_event.GetLabel()
            if label == self.event_label:
                end_event = find_next_event(acq, label, context, event_index)
                numbers[context] = numbers.get(context) + 1
                if end_event is not None:
                    cycle = GaitCycle(numbers[context], context, start_event.GetFrame(), end_event.GetFrame())
                    gait_cycles[context].append(cycle)
        return gait_cycles


class HeelStrikeToHeelStrikeCycleBuilder(EventCycleBuilder):
    def __init__(self, eventAnomalyChecker: EventAnomalyChecker):
        super().__init__(eventAnomalyChecker, GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, eventAnomalyChecker: EventAnomalyChecker):
        super().__init__(eventAnomalyChecker, GaitEventLabel.FOOT_OFF)
