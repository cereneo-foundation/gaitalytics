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
fig, ax = plt.subplots(nrows=3)
path_a = r"C:\ViconData\TMR\JiahuiA_TMR109\23_12_D2\23_12_D2_BaselinePiGwithEvents.c3d"
acq = btkTools.smartReader(path_a)
for i in range(3):
    ax[i].plot(acq.GetPoint("LFootProgressAngles").GetValues()[:,i][0:2000])
plt.show()

ax = plt.figure().add_subplot(projection='3d')
x = acq.GetPoint("LFootProgressAngles").GetValues()[:,0][0:2000]
y = acq.GetPoint("LFootProgressAngles").GetValues()[:,1][0:2000]
z = acq.GetPoint("LFootProgressAngles").GetValues()[:,2][0:2000]
ax.scatter(x,y,z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
##
colname = ["x","y","z"]
dataset = pd.DataFrame(columns=["x","y","z"], data=np.transpose([x,y,z]))
print(dataset)
tmp = dataset.loc[:, colname].values
tmp = StandardScaler().fit_transform(tmp)

normalised_dataset = pd.DataFrame(tmp, columns=colname)
print(normalised_dataset)

ax = plt.figure().add_subplot(projection='3d')

ax.scatter(normalised_dataset["x"],normalised_dataset["y"],normalised_dataset["z"])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

fig, ax = plt.subplots(nrows=3)
i=0
for name in colname:
    ax[i].plot(normalised_dataset[name])
    i+=1
plt.show()

##

pca = PCA(n_components=3)
principalComponents = pca.fit_transform(tmp)

principal_breast_Df = pd.DataFrame(data=principalComponents
                                   , columns=['principal component 1', 'principal component 2',
                                              'principal component 3'])
print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
pca.components_
print(principal_breast_Df["principal component 1"])
##
plt.plot(principal_breast_Df["principal component 1"])
plt.plot(normalised_dataset["x"])
##
fig, ax = plt.subplots(nrows=3,ncols=2)
i=0
for name in colname:
    ax[i,0].plot(normalised_dataset[name])
    ax[i, 1].plot(principal_breast_Df["principal component "+str(i+1)])
    i+=1
plt.show()

##
u = tmp
v = pca.components_[0]
e = np.dot(v,u.T)
plt.plot(e)
plt.plot(principal_breast_Df["principal component 1"])
##

