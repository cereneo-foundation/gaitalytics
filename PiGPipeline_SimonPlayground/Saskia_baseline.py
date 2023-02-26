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
path_a = r"C:/ViconData/TMR/SaskiaN_TMR102/21_12_D2/GameSession06PiGwithEvents.c3d"

acq= btkTools.smartReader(path_a)
fig, ax = plt.subplots(nrows=3)
for i in range(3):
    ax[i].plot(acq.GetPoint("LFootProgressAngles").GetValues()[:,i][0:2000])
plt.show()
correct_length = 2000

ax = plt.figure().add_subplot(projection='3d')
x = acq.GetPoint("LFootProgressAngles").GetValues()[:,0][0:correct_length]
y = acq.GetPoint("LFootProgressAngles").GetValues()[:,1][0:correct_length]
z = acq.GetPoint("LFootProgressAngles").GetValues()[:,2][0:correct_length]
ax.scatter(x,y,z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

##
def calculate_mean_position_vector(acq,length_of_rec,pelvis_marker=['LASI','RASI','LPSI','LTHI']):
    pelvis_x = []
    pelvis_y = []
    pelvis_z = []
    for marker in pelvis_marker:
        pelvis_x.append(acq.GetPoint(marker).GetValues()[:,0][:length_of_rec])
        pelvis_y.append(acq.GetPoint(marker).GetValues()[:, 1][:length_of_rec])
        pelvis_z.append(acq.GetPoint(marker).GetValues()[:, 2][:length_of_rec])
    return [np.mean(pelvis_x,axis=0),np.mean(pelvis_y,axis=0),np.mean(pelvis_z,axis=0)]
##


matx = []
full_names = []
names = ['LASI', 'RASI', 'LPSI', 'RPSI', 'LTHI', 'LKNE', 'LTIB', 'LANK', 'LHEE', 'LTOE', 'RTHI', 'RKNE', 'RTIB', 'RANK', 'RHEE', 'RTOE']

mean_position = calculate_mean_position_vector(acq,correct_length)

for name in names:
    matx.append(acq.GetPoint(name).GetValues()[:,0][:correct_length]-mean_position[0])
    matx.append(acq.GetPoint(name).GetValues()[:, 1][:correct_length]-mean_position[1])
    matx.append(acq.GetPoint(name).GetValues()[:, 2][:correct_length]-mean_position[2])

    full_names.append(name+"_x")
    full_names.append(name + "_y")
    full_names.append(name + "_z")
print(np.shape(np.transpose(matx)))
print(np.shape(full_names))

dataset = pd.DataFrame(columns=full_names, data=np.transpose(matx))
features = full_names



x = dataset.loc[:, features].values
x = StandardScaler().fit_transform(x)

normalised_dataset = pd.DataFrame(x, columns=full_names)


pca = PCA(n_components=10)
principalComponents = pca.fit_transform(x)

principal_breast_Df = pd.DataFrame(data=principalComponents
                                   , columns=['principal component 1', 'principal component 2',
                                              'principal component 3', 'principal component 4',
                                              'principal component 5','principal component 6',
                                              'principal component 7','principal component 8',
                                              'principal component 9','principal component 10'])

print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))

##
ax = plt.figure().add_subplot(projection='3d')

for name in names:
    x_ = acq.GetPoint(name).GetValues()[:, 0][:correct_length]
    y_ = acq.GetPoint(name).GetValues()[:, 1][:correct_length]
    z_ = acq.GetPoint(name).GetValues()[:, 2][:correct_length]
    ax.scatter(x_,y_,z_)


ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')


##

normalised_dataset
