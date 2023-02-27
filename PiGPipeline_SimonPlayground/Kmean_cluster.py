import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
from PiGPipeline_SimonPlayground.Pipeline_make_PiGfiles import make_PiG_conversion
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles
from gait_analysis.utils import return_max_length
from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from kneed import KneeLocator
from sklearn.metrics import silhouette_score

names_R = ["RAnkleAngles", "RFootProgressAngles", "RHipAngles", "RKneeAngles", "RPelvisAngles", "RSpineAngles",
           "RThoraxAngles"]
names_L = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles", "LKneeAngles", "LPelvisAngles", "LSpineAngles",
           "LThoraxAngles"]

##

baseline_D1 = r"C:/ViconData/TMR/SaskiaN_TMR102/20_12_D1/BaselinePiGwithEvents.c3d"
acq_D1 = btkTools.smartReader(baseline_D1)

gait_cycle_D1 = correct_gaitcycles(acq_D1)
##


baseline_D2 = r"C:/ViconData/TMR/SaskiaN_TMR102/21_12_D2/BaselinePiGwithEvents.c3d"
acq_D2 = btkTools.smartReader(baseline_D2)
gait_cycle_D2 = correct_gaitcycles(acq_D2)


##
def return_one_side(list_gait_cycle, context):
    list_side = list()
    for cycle in list_gait_cycle:
        if cycle.getEvents("All")[0].GetContext() == context:
            list_side.append(cycle)
    return list_side


##
right_D1 = return_one_side(gait_cycle_D1, "Right")
right_D2 = return_one_side(gait_cycle_D2, "Right")

##
D1 = []
for cycl in right_D1[1:]:
    D1.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])

for elem in D1:
    plt.plot(elem)
plt.show()
##
max_length = return_max_length(D1)
xspan = range(0,max_length)
matx =  []
for elem in D1:
    to_pad = max_length - len(elem)
    elem_pad = np.pad(elem,(0,to_pad),'constant',constant_values=0)
    matx.append(elem_pad)
print(np.shape(matx))


##

kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(matx)
print(kmeans.labels_)
print("Out of ",len(kmeans.labels_),":",len(kmeans.labels_)-sum(kmeans.labels_),"has been attributed to cluster 0")
print("and ",sum(kmeans.labels_),"has been attributed to cluster 1")
colors = ['darkred','darkblue','darkgreen']
for i in range(len(kmeans.cluster_centers_)):
    plt.plot(xspan,kmeans.cluster_centers_[i],c= colors[i],linewidth=5,label="cluster"+str(i))

colors = ['red','blue','green']
for i in range(len(D1)):
    if kmeans.labels_[i] == 1:
        plt.plot(D1[i],c=colors[1],alpha=0.5)
    if kmeans.labels_[i]==0:
        plt.plot(D1[i],c=colors[0],alpha=0.5)
    if kmeans.labels_[i]==2:
        plt.plot(D1[i],c=colors[2],alpha=0.5)

plt.legend()
plt.show()
##
test = kmeans.transform(matx)
colors = ['red','blue','green']
for i in range(len(test)):
    plt.scatter(test[i][0],test[i][1],c=colors[kmeans.labels_[i]])

##

