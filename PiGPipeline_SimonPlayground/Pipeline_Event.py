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



def return_events(acq):
    list_event = list()
    for event in btk.Iterate(acq.GetEvents()):
        list_event.append(event)
    return list_event


def construct_correct_seq(context):
    if context == "Right":
        oppositeSide = "Left"
    elif context == "Left":
        oppositeSide = "Right"
    return [[["Foot Strike", context], ["Foot Off", oppositeSide], ["Foot Strike", oppositeSide], ["Foot Off", context],
            ["Foot Strike", context]],[["Foot Strike", context], ["Foot Off", context], ["Foot Strike", oppositeSide], ["Foot Off", oppositeSide],
            ["Foot Strike", context]]]


def correct_seq(subset_of_event):
    context = subset_of_event[0].GetContext()
    corr_seq = construct_correct_seq(context)

    comparis = []
    for event in subset_of_event:
        comparis.append([event.GetLabel(), event.GetContext()])
    return corr_seq[0] == comparis or corr_seq[1] == comparis


def correct_gaitcycles(acq, seq=["Foot Strike", "Foot Off", "Foot Strike"], context=["Left", "Right"]):
    gaitCycles = list()
    list_events = return_events(acq)
    for i in range(len(list_events) - 5):
        if correct_seq(list_events[i:i + 5]):
            gaitCycles.append(cycle.Cycle(acq, list_events[i].GetFrame(), list_events[i + 5].GetFrame(),
                                          list_events[i].GetContext()))

    return gaitCycles
##
