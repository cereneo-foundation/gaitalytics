import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

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

GS_D1 = r"C:/ViconData/TMR/SaskiaN_TMR102/20_12_D1/GameSession01PiGwithEvents.c3d"
GS1_D1 = btkTools.smartReader(GS_D1)

gait_cycle_GS11 = correct_gaitcycles(GS1_D1)

##
def return_gait_one_side(list_gait_cycle, context):
    list_side = list()
    for cycle in list_gait_cycle:
        if cycle.getEvents("All")[0].GetContext() == context:
            list_side.append(cycle)
    return list_side


##
right_D1 = return_gait_one_side(gait_cycle_D1, "Right")
right_D2 = return_gait_one_side(gait_cycle_D2, "Right")
right_GS11 = return_gait_one_side(gait_cycle_GS11, "Right")

##
D1 = []
for cycl in right_D1[1:]:
    D1.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])

for elem in D1:
    plt.plot(elem)
plt.show()

##
##
D2 = []
for cycl in right_D2[1:]:
    D2.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])

for elem in D2:
    plt.plot(elem)
plt.show()
##
GS11 = []
for cycl in right_GS11[1:]:
    GS11.append(cycl.getPointTimeSequenceData("RAnkleAngles")[:,0])

for elem in GS11:
    plt.plot(elem)
plt.show()

##
max_length = np.max([return_max_length(D1),return_max_length(D2),return_max_length(GS11)])
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
def create_matrix_padded(matrix,max_length):
    matx = []
    lin_array = len(np.shape(matrix[0]))==1
    for array in matrix:
        to_pad = max_length - len(array)
        if lin_array:
            array_pad = np.pad(array, (0, to_pad), 'constant', constant_values=0)
        else:
            array_pad = np.pad(array[:,0], (0, to_pad), 'constant', constant_values=0)
        matx.append(array_pad)
    return matx
##
# Testing PCA idea
raw =[]
for elem in D1:
    raw.append(StandardScaler().fit_transform(elem.reshape(-1, 1)))
print(raw)


##
matx_norm =  []
for elem in raw:
    to_pad = max_length - len(elem)
    elem_pad = np.pad(elem[:,0],(0,to_pad),'constant',constant_values=0)
    matx_norm.append(elem_pad)
print(np.shape(matx_norm))
feat_cols = ['feature' + str(i) for i in range(len(matx_norm))]

normalised_dataset = pd.DataFrame(np.transpose(matx_norm), columns=feat_cols)
print(normalised_dataset)
##
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(matx_norm)

principal_breast_Df = pd.DataFrame(data=principalComponents
                                   , columns=['principal component 1', 'principal component 2'])
print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
##
plt.scatter(principal_breast_Df["principal component 1"],principal_breast_Df["principal component 2"])
plt.xlabel('Principal Component - 1',fontsize=20)
plt.ylabel('Principal Component - 2',fontsize=20)

##
raw =[]
for elem in D2:
    raw.append(StandardScaler().fit_transform(elem.reshape(-1, 1)))
print(raw)

matx_norm = create_matrix_padded(raw,max_length)
print(np.shape(matx_norm))
##
feat_cols = ['feature' + str(i) for i in range(len(matx_norm))]
normalised_dataset = pd.DataFrame(np.transpose(matx_norm), columns=feat_cols)
print(normalised_dataset)

tt =pca.transform(matx_norm)

##
print(tt)

##
plt.scatter(principal_breast_Df["principal component 1"],principal_breast_Df["principal component 2"],c='black')
plt.scatter(tt[:,0],tt[:,1],c='r')
plt.xlabel('Principal Component - 1',fontsize=20)
plt.ylabel('Principal Component - 2',fontsize=20)

##
print(len(tt))
print(len(principal_breast_Df["principal component 1"]))

##

raw =[]
for elem in GS11:
    raw.append(StandardScaler().fit_transform(elem.reshape(-1, 1)))
print(raw)

matx_norm = create_matrix_padded(raw,max_length)
print(np.shape(matx_norm))
GS11_tt =pca.transform(matx_norm)
##
indx_alpha = np.linspace(0.1,1,len(GS11_tt))

plt.scatter(principal_breast_Df["principal component 1"],principal_breast_Df["principal component 2"],c='black')
plt.scatter(tt[:,0],tt[:,1],c='r')
for i in range(len(GS11_tt)):
    plt.scatter(GS11_tt[i,0],GS11_tt[i,1],c='g',alpha=indx_alpha[i])
plt.xlabel('Principal Component - 1',fontsize=20)
plt.ylabel('Principal Component - 2',fontsize=20)

##
m_ = []
for i in range(len(GS11)):
    m_.append(len(GS11[i]))
##
plt.hist(m_)
print(np.mean(m_))
print(np.std(m_))
##