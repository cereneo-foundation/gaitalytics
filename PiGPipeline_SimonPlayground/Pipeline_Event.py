import os
import btk
from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
from gait_analysis.events import GaitEventDetectorFactory
from gait_analysis.filtering import low_pass_point_filtering, low_pass_force_plate_filtering


def add_event(DATA_PATH: str, SUBJECT: str, SESSIONS: str):
    for sess in SESSIONS[:]:
        file_list = []
        for root, dirs, files_ in os.walk(DATA_PATH + SUBJECT + sess):
            # select file name
            for file in files_:
                # check the extension of files
                if file.endswith('.c3d') and ("PiG" in file) and ("Calib" not in file) and ("Events" not in file):
                    # print whole path of files
                    print(os.path.join(root, file))
                    file_list.append(os.path.join(root, file))

        for acquisition in file_list:
            acq_trial = btkTools.smartReader(acquisition)
            low_pass_point_filtering(acq_trial)
            low_pass_force_plate_filtering(acq_trial)

            acq_trial.ClearEvents()
            GaitEventDetectorFactory().get_force_plate_detector().detect_events(acq_trial)

            evs = acq_trial.GetEvents()

            for i in range(evs.GetItemNumber()):
                eva = evs.GetItem(i)
                eva.SetFrame(int(eva.GetTime() * 100))

            save_name = acquisition[:-4] + "withEvents.c3d"
            print(save_name)
            btkTools.smartWriter(acq_trial, save_name)

def return_event_from_leg(acq, context):
    list_event = list()
    for event in btk.Iterate(acq.GetEvents()):
        if event.GetContext() == context:
            list_event.append(event)
    return list_event

def correct_gaitcycles(acq,seq = ["Foot Strike","Foot Off","Foot Strike"],context = ["Left","Right"]):
    gaitCycles = list()
    for side in context:
        event_from_this_side = return_event_from_leg(acq,side)

        for i in range(len(event_from_this_side) - 2):
            if [event_from_this_side[i].GetLabel(), event_from_this_side[i + 1].GetLabel(), event_from_this_side[i + 2].GetLabel()] == seq:
                gaitCycles.append(cycle.GaitCycle(acq, event_from_this_side[i].GetFrame(), event_from_this_side[i + 2].GetFrame(), side))

    return gaitCycles