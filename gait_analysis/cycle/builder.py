from abc import ABC, abstractmethod

from btk import btkAcquisition, btkEvent

from gait_analysis.event.anomaly import EventAnomalyChecker
from gait_analysis.event.utils import GaitEventLabel, find_next_event
from gait_analysis.utils.c3d import GaitEventContext


class GaitCycle:

    def __init__(self, number: int, context: GaitEventContext, start_frame: int, end_frame: int,
                 unused_event: btkEvent):
        self.number = number
        self.context = context
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.unused_event = unused_event


class GaitCycleList:

    def __init__(self):
        self._left_cycles = {}
        self._right_cycles = {}

    def add_cycle(self, cycle: GaitCycle):
        if cycle.context == GaitEventContext.LEFT:
            self._left_cycles[cycle.number] = cycle
        else:
            self._right_cycles[cycle.number] = cycle

    @property
    def left_cycles(self) -> {int: GaitCycle}:
        return self._left_cycles

    @left_cycles.setter
    def left_cycles(self, cycles: {int: GaitCycle}):
        self._left_cycles = cycles

    @property
    def right_cycles(self) -> {int: GaitCycle}:
        return self._right_cycles

    @right_cycles.setter
    def right_cycles(self, cycles: {int: GaitCycle}):
        self._right_cycles = cycles

    def get_number_of_cycles(self) -> int:
        l_num = list(self._left_cycles.keys())[-1]
        r_num = list(self._left_cycles.keys())[-1]
        return l_num if l_num >= r_num else r_num


class CycleBuilder(ABC):

    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
        self.eventAnomalyChecker = event_anomaly_checker

    def build_cycles(self, aqc: btkAcquisition) -> GaitCycleList:
        [detected, detail_tuple] = self.eventAnomalyChecker.check_events(aqc)
        if detected:
            raise RuntimeError(detail_tuple)

        return self._build(aqc)

    @abstractmethod
    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        pass


class EventCycleBuilder(CycleBuilder):
    def __init__(self, event_anomaly_checker: EventAnomalyChecker, event: GaitEventLabel):
        super().__init__(event_anomaly_checker)
        self.event_label = event.value

    def _build(self, acq: btkAcquisition) -> GaitCycleList:
        gait_cycles = GaitCycleList()
        numbers = {GaitEventContext.LEFT.value: 0,
                   GaitEventContext.RIGHT.value: 0}
        for event_index in range(0, acq.GetEventNumber()):
            start_event = acq.GetEvent(event_index)
            context = start_event.GetContext()

            label = start_event.GetLabel()
            if label == self.event_label:
                try:
                    [end_event, unused_events] = find_next_event(acq, label, context, event_index)
                    if end_event is not None:
                        numbers[context] = numbers[context] + 1
                        cycle = GaitCycle(numbers[context], GaitEventContext.get_context(context),
                                          start_event.GetFrame(), end_event.GetFrame(),
                                          unused_events)
                        gait_cycles.add_cycle(cycle)
                except IndexError as err:
                    pass  # If events do not match in the end this will be raised
        return gait_cycles


class HeelStrikeToHeelStrikeCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
        super().__init__(event_anomaly_checker, GaitEventLabel.FOOT_STRIKE)


class ToeOffToToeOffCycleBuilder(EventCycleBuilder):
    def __init__(self, event_anomaly_checker: EventAnomalyChecker):
        super().__init__(event_anomaly_checker, GaitEventLabel.FOOT_OFF)
