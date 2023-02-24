from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles

##
file_a = "C:/ViconData/TMR/JiahuiA_TMR109/23_12_D2/23_12_D2_GameSession03PiGwithEvents.c3d"
acq = btkTools.smartReader(file_a)

gait_cycle = correct_gaitcycles(acq)



import matplotlib.pyplot as plt
plt.plot(acq.GetPoint('LAbsAnkleAngle').GetValues()[:,0][0:100])
##
import numpy as np
dur = []
for elem in gait_cycle:
    dur.append(elem.getSpatioTemporalParameter("speed"))
print(np.mean(dur))
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

