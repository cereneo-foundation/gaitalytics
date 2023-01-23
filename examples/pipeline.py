from pyCGM2.Tools import  btkTools
from gait_analysis.models import HBMToCGM2Mapper
from gait_analysis.events import ZenisGaitEventDetector

mapper = HBMToCGM2Mapper()
acq = btkTools.smartReader("test/data/test.c3d", mapper.get_translator())
mapper.calculate_missing_markers(acq)
filters.filtfilt(acq)
ZenisGaitEventDetector().detect_events(acq)
btkTools.smartWriter(acq, "test/data/test_event.c3d")
acq.Clone()
