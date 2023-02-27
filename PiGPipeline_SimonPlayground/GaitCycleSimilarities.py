import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
from PiGPipeline_SimonPlayground.Pipeline_make_PiGfiles import make_PiG_conversion
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles

from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
import matplotlib.pyplot as plt

##
last_sess_D1 = r"C:/ViconData/TMR/SaskiaN_TMR102/20_12_D1/GameSession06PiGwithEvents.c3d"
acq_D1 = btkTools.smartReader(last_sess_D1)

gait_cycle_D1 = correct_gaitcycles(acq_D1)
##

first_sess_D2 = r"C:/ViconData/TMR/SaskiaN_TMR102/21_12_D2/GameSession01PiGwithEvents.c3d"
acq_D2 = btkTools.smartReader(first_sess_D2)

gait_cycle_D2 = correct_gaitcycles(acq_D2)


##
def return_last_n_gait_cycleD1(gait_list, context,n=50):
    last_fifty = list()
    i = 1
    while len(last_fifty) < n:
        if gait_list[-i].getEvents("All")[-1].GetFrame()<30000:
            if gait_list[-i].getEvents("All")[0].GetContext() == context:
                last_fifty.append(gait_list[-i])

            if i >= len(gait_list) - 1:
                print("could not find fifty gait cycle starting from side", context)
                last_fifty = list()
                break
        i += 1
    return last_fifty


###
last_D1= return_last_n_gait_cycleD1(gait_cycle_D1, "Right",n=50)
last_D1.reverse()
##
for elem in last_D1:
    first_ev = elem.getEvents("All")[0]
    print(first_ev.GetContext())
    print(first_ev.GetLabel())
    print(first_ev.GetFrame())
print(len(last_D1))


##
def tolerant_mean(arrs):
    lens = [len(i) for i in arrs]
    arr = np.ma.empty((np.max(lens), len(arrs)))
    arr.mask = True
    for idx, l in enumerate(arrs):
        arr[:len(l), idx] = l
    return arr.mean(axis=-1), arr.std(axis=-1)

##


##
def return_max_length(arrs):
    return len(max(arrs,key=len))

##
names_R = ["RAnkleAngles", "RFootProgressAngles", "RHipAngles", "RKneeAngles", "RPelvisAngles", "RSpineAngles",
           "RThoraxAngles"]
names_L = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles", "LKneeAngles", "LPelvisAngles", "LSpineAngles",
           "LThoraxAngles"]
pt=[]
for cycl in last_D1:
    pt.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])
i=0


for elem in pt:
    plt.plot(elem)
plt.show()
##
max_length = return_max_length(pt)
xspan = np.linspace(1,max_length,max_length)
matx =  []
for elem in pt:
    to_pad = max_length - len(elem)
    elem_pad = np.pad(elem,(0,to_pad),'constant',constant_values=0)
    matx.append(elem_pad)
print(np.shape(matx))

##

from sklearn.cluster import KMeans
import numpy as np
X = matx
kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(X)
print(kmeans.labels_)
print("Out of ",len(kmeans.labels_),":",len(kmeans.labels_)-sum(kmeans.labels_),"has been attributed to cluster 0")
print("and ",sum(kmeans.labels_),"has been attributed to cluster 1")
##
colors = ['darkred','darkblue']
for i in range(len(kmeans.cluster_centers_)):
    plt.plot(xspan,kmeans.cluster_centers_[i],c= colors[i],linewidth=5,label="cluster"+str(i))

colors = ['red','blue']
for i in range(len(pt)):
    if kmeans.labels_[i] == 1:
        plt.plot(pt[i],c=colors[1],alpha=0.5)
    if kmeans.labels_[i]==0:
        plt.plot(pt[i],c=colors[0],alpha=0.5)

plt.legend()
plt.show()
##
print(len(kmeans.cluster_centers_))
##
test = kmeans.transform(X)
print(len(test))
##
colors = ['red','blue']
for i in range(len(test)):
    plt.scatter(test[i][0],test[i][1],c=colors[kmeans.labels_[i]])

##
pt2=[]
for cycl in gait_cycle_D2[:100]:
    pt2.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])
i=0


for elem in pt2:
    plt.plot(elem)
plt.show()
##
max_length = return_max_length(pt)
xspan = np.linspace(1,max_length,max_length)
matx2 =  []
for elem in pt2:
    to_pad = max_length - len(elem)
    if to_pad<0:
        elem_pad=elem[:max_length]
    else:
        elem_pad = np.pad(elem,(0,to_pad),'constant',constant_values=0)
    matx2.append(elem_pad)
print(np.shape(matx2))

##
# Fit D2 on D1
fitt = kmeans.predict(matx2)
trans = kmeans.transform(matx2)

indx_alpha = np.linspace(0.1,1,len(fitt))
colors = ['red','blue']
for i in range(len(test)):
    plt.scatter(test[i][0],test[i][1],c=colors[kmeans.labels_[i]])
for i in range(len(trans)):
    plt.scatter(trans[i][0],trans[i][1],c='black',alpha=indx_alpha[i])
plt.legend()
##
print(np.linspace(0.1,10,5))

##
colors = ['red','blue']
for i in range(len(test)):
    plt.scatter(test[i][0],test[i][1],c=colors[kmeans.labels_[i]])

##
colors = ["r","b","g","black"]
i=0
for elem in pt:
    if i <= len(pt)/4:
        c = colors[0]
    if i >= len(pt)/4 and i < len(pt)/2:
        c = colors[1]
    if i >= len(pt)/2 and i < 3*len(pt)/4:
        c = colors[2]
    if i >= 3*len(pt)/4:
        c=colors[3]
    plt.plot(elem,c =c,alpha=0.5)
    i+=1
plt.legend()
plt.show()

##
fig, ax = plt.subplots(nrows=3)
x_arr = []
y_arr = []
z_arr = []
maxi = 0
name = "RFootProgressAngles"
for cycl in last_D1:
    length = len(cycl.getPointTimeSequenceData(name)[:, 0])
    print(length,maxi)
    if length > maxi:
        maxi = length
    x_arr.append(cycl.getPointTimeSequenceData(name)[:, 0])
    y_arr.append(cycl.getPointTimeSequenceData(name)[:, 1])
    z_arr.append(cycl.getPointTimeSequenceData(name)[:, 2])

x_m,x_std = tolerant_mean(x_arr)
y_m,y_std = tolerant_mean(y_arr)
z_m,z_std = tolerant_mean(z_arr)
xspan = np.linspace(1,maxi,maxi)
ax[0].plot(xspan,x_m)
ax[0].fill_between(xspan,x_m-x_std,x_m+x_std,alpha=0.3)

ax[1].plot(xspan,y_m)
ax[1].fill_between(xspan,y_m-y_std,y_m+y_std,alpha=0.3)

ax[2].plot(xspan,z_m)
ax[2].fill_between(xspan,z_m-z_std,z_m+z_std,alpha=0.3)
##
i= 0
for i in range(10):
    y = last_D1[i+40].getPointTimeSequenceData("RAnkleAngles")[:,0]
    evo = last_D1[i+40].getEvents("All")[0].GetFrame()
    plt.plot(y,label = str(evo))
plt.legend()
plt.show()
##
delta = []
for elem in last_D1:
    first_ev = elem.getEvents("All")[0].GetFrame()
    last_ev = elem.getEvents("All")[-1].GetFrame()
    delta.append(last_ev-first_ev)
    print(last_ev-first_ev)
print(np.mean(delta))
##


##

