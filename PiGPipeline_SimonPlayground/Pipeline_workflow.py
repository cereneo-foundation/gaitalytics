from PiGPipeline_SimonPlayground.Pipeline_make_PiGfiles import make_PiG_conversion
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles

###
# Convert the files in PiG markers name
DATA_PATH = r"C:/ViconData/TMR/"
SUBJECT = "SaskiaN_TMR102/"
SESSIONS = ["20_12_D1/", "21_12_D2/"]

make_PiG_conversion(DATA_PATH,SUBJECT,SESSIONS)
##
# Create new c3d with events added
add_event(DATA_PATH, SUBJECT, SESSIONS)
##
##

from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle

##

##
file_a = "C:/ViconData/TMR/SaskiaN_TMR102/20_12_D1/GameSession06PiGwithEvents.c3d"
acq = btkTools.smartReader(file_a)

gait_cycle = correct_gaitcycles(acq)

###

##
import matplotlib.pyplot as plt
plt.plot(acq.GetPoint('LAbsAnkleAngle').GetValues()[:,0][0:100])
##
import numpy as np
dur = []
for elem in gait_cycle:
    if elem.getEvents("All")[0].GetContext()=="Left":
        dur.append(elem.getSpatioTemporalParameter("stanceDuration"))
print(np.mean(dur))


xspan = np.linspace(1,len(dur),len(dur))
plt.plot(xspan,dur,'-o',"blue",label = "Left")
dur = []
for elem in gait_cycle:
    if elem.getEvents("All")[0].GetContext()=="Right":
        dur.append(elem.getSpatioTemporalParameter("stanceDuration"))
print(np.mean(dur))
xspan = np.linspace(1,len(dur),len(dur))
plt.plot(xspan,dur,'-o',"r",label = "Right")
plt.legend()
##
cyclos = cycle.Cycles()
cyclos.setKinematicCycles(gait_cycle)
##
from pyCGM2.Processing import analysis

Kinematic_labels = {"Left": ["LAbsAnkleAngle", "LAnkleAngles", "LFootProgressAngles", "LHipAngles",
                             "LKneeAngles", "LPelvisAngles", "LSpineAngles", "LThoraxAngles"],
                    "Right": ["RAbsAnkleAngle", "RAnkleAngles", "RFootProgressAngles", "RHipAngles",
                              "RKneeAngles", "RPelvisAngles", "RSpineAngles", "RThoraxAngles"]}

anal = analysis.AnalysisBuilder(cyclos, kinematicLabelsDict=Kinematic_labels)

anal.computeKinematics()
##
analysisFilter = analysis.AnalysisFilter()

analysisFilter.setBuilder(anal)
analysisFilter.build()
analy = analysisFilter.analysis

##
left_cycle = analy.kinematicStats.data["LAbsAnkleAngle", "Left"]["values"]
right_cycle = analy.kinematicStats.data["RAbsAnkleAngle", "Right"]["values"]

##
from pyCGM2.Processing import analysisHandler

truc = analysisHandler.getValues(analy, "LAbsAnkleAngle", "Left")
##
import matplotlib.pyplot as plt

fig, ax = plt.subplots(nrows=1, ncols=2)

for cyc in left_cycle:
    ax[0].plot(cyc[:, 0])

for cyc in right_cycle:
    ax[1].plot(cyc[:, 0])
ax[0].set_title("Left side")
ax[1].set_title("Right side")
plt.show()
##
from PiGPipeline_SimonPlayground.Pipeline_Event import return_event_from_leg


def check_continuity_gaitcycles(acq, seq=["Foot Strike", "Foot Off", "Foot Strike"], context=["Left", "Right"]):
    left_right_gaitcycles = []
    for side in context:
        event_from_this_side = return_event_from_leg(acq, side)
        gaitCycles = list()
        for i in range(len(event_from_this_side) - 2):
            if [event_from_this_side[i].GetLabel(), event_from_this_side[i + 1].GetLabel(),
                event_from_this_side[i + 2].GetLabel()] == seq:
                gaitCycles.append([event_from_this_side[i].GetFrame(), event_from_this_side[i + 2].GetFrame()])
        left_right_gaitcycles.append(gaitCycles)

    return left_right_gaitcycles[0], left_right_gaitcycles[1]


##


##
left_cycle, right_cycle = check_continuity_gaitcycles(acq)
##

ff = 0
lf = 0
for cycl in right_cycle:
    ff_tmp = cycl[0]
    lf_tmp = cycl[-1]

    if ff_tmp != lf:
        print("not continuous gait here [", ff, ",", lf, "]", "with the following gait [", ff_tmp, ",", lf_tmp, "]")
    ff = ff_tmp
    lf = lf_tmp
##
len(right_cycle)

##
len(left_cycle)

##
