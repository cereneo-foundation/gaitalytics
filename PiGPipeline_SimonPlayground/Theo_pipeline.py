from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles
import matplotlib.pyplot as plt
import numpy as np


##
#path_a = r"C:/ViconData/TMR/SaskiaN_TMR102/21_12_D2/GameSession06PiGwithEvents.c3d"

file_jiahui = r"C:/Users/KLGM_001/Documents/Theo/TheoFile/SaskiaN_TMR102/21_12_D2/GameSession06PiGwithEvents.c3d"
acq = btkTools.smartReader(file_jiahui)

# extract gait cycles in a list
gait_cycle = correct_gaitcycles(acq)
##

# select all right gait cycles
right_side = []

# elem is a class
for elem in gait_cycle:
    if elem.getEvents("All")[0].GetContext() == "Right":
        right_side.append(elem)

# select all left gait cycles
left_side = []

for elem in gait_cycle:
    if elem.getEvents("All")[0].GetContext() == "Left":
        left_side.append(elem)

##

names_R = ["RAnkleAngles", "RFootProgressAngles", "RHipAngles", "RKneeAngles", "RPelvisAngles", "RSpineAngles",
           "RThoraxAngles"]
names_L = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles", "LKneeAngles", "LPelvisAngles", "LSpineAngles",
           "LThoraxAngles"]
# first cycle
#plt.plot(right_side[0].getPointTimeSequenceData("RAnkleAngles")[:,0])
#plt.plot(right_side[1].getPointTimeSequenceData("RAnkleAngles")[:,0])




# plot all gait cycles of left foot
for i in range (0,len(left_side)) :
    plt.plot(left_side[i].getPointTimeSequenceData("RAnkleAngles")[:,0])
    plt.title('left foot gait cycles')

plt.show()

##
print(len(right_side[1].getPointTimeSequenceData("RAnkleAngles")[:,0]))

##

len_x = (len(right_side[1].getPointTimeSequenceData("RAnkleAngles")[:,0]))

x = np.linspace(1, len_x, len_x)
y = (right_side[1].getPointTimeSequenceData("RAnkleAngles")[:,0])



for i in range (1,10) :
    mymodel = np.poly1d(np.polyfit(x,y,i))
    myline = np.linspace(1, len_x, 400)

    plt.scatter(x,y)
    plt.plot(myline, mymodel(myline))
plt.show()




##

#file_a = "C:/ViconData/TMR/JiahuiA_TMR109/23_12_D2/23_12_D2_GameSession03PiGwithEvents.c3d"
#acq = btkTools.smartReader(file_a)

#gait_cycle = correct_gaitcycles(acq)

#cycl = gait_cycle[0]

#cycl.getPointTimeSequenceData("LAnkleAngles")
#cycl.getPointTimeSequenceDataNormalized("LAnkleAngles")



#import matplotlib.pyplot as plt
#plt.plot(acq.GetPoint('LAbsAnkleAngle').GetValues()[:,0][0:100])
##
##
import numpy as np

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

