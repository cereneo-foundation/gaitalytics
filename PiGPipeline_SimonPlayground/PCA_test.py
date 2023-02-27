import pandas as pd
import os
from PiGPipeline_SimonPlayground.Pipeline_make_PiGfiles import make_PiG_conversion
from PiGPipeline_SimonPlayground.Pipeline_Event import add_event, correct_gaitcycles

from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle

##
path_a = "C:/ViconData/TMR/SaskiaN_TMR102/21_12_D2"
file_list = []
for root, dirs, files_ in os.walk(path_a):
    # select file name
    for file in files_:
        # check the extension of files
        if file.endswith('.c3d') and ("PiGwithEvents" in file) and ("Baseline" not in file):
            # print whole path of files
            print(os.path.join(root, file))
            file_list.append(os.path.join(root, file))
##
acq= btkTools.smartReader(file_list[0])
correct_length = len(acq.GetPoint("LFootProgressAngles").GetValues()[:,0])
print(correct_length)


##

# PCA on model output
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

PM = []
for fichier in file_list:
    print(fichier)
    acq = btkTools.smartReader(fichier)

    matx = []
    full_names = []
    names_R = ["RAnkleAngles", "RFootProgressAngles", "RHipAngles","RKneeAngles", "RPelvisAngles", "RSpineAngles", "RThoraxAngles"]
    names_L = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles","LKneeAngles", "LPelvisAngles", "LSpineAngles", "LThoraxAngles"]
    names = names_R+names_L
    for name in names_R:
        matx.append(acq.GetPoint(name).GetValues()[:,0][:correct_length])
        matx.append(acq.GetPoint(name).GetValues()[:, 1][:correct_length])
        matx.append(acq.GetPoint(name).GetValues()[:, 2][:correct_length])

        full_names.append(name+"_x")
        full_names.append(name + "_y")
        full_names.append(name + "_z")
    print(np.shape(np.transpose(matx)))
    print(np.shape(full_names))

    dataset = pd.DataFrame(columns=full_names, data=np.transpose(matx))
    features = full_names



    x = dataset.loc[:, features].values
    x = StandardScaler().fit_transform(x)

    feat_cols = ['feature' + str(i) for i in range(x.shape[1])]
    normalised_dataset = pd.DataFrame(x, columns=feat_cols)


    pca = PCA(n_components=10)
    principalComponents = pca.fit_transform(x)

    principal_breast_Df = pd.DataFrame(data=principalComponents
                                       , columns=['principal component 1', 'principal component 2',
                                                  'principal component 3', 'principal component 4',
                                                  'principal component 5','principal component 6',
                                                  'principal component 7','principal component 8',
                                                  'principal component 9','principal component 10'])
    PM.append(principal_breast_Df)
    print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
###
import matplotlib.pyplot as plt
i=1
for elem in PM[:2]:
    plt.plot(elem['principal component 1'][0:1000],label = "game session "+str(i))
    i+=1
plt.legend()

###
u = acq.GetPoint("RAnkleAngles").GetValues()[:,0][0:correct_length]
v = PM[-1]['principal component 1']
v_norm = np.sqrt(sum(v**2))
proj_of_u_on_v = (np.dot(u, v) / v_norm ** 2) * v

print("Projection of Vector u on Vector v is: ", proj_of_u_on_v)
plt.plot(proj_of_u_on_v[0:1000],label = "proj u on v")
plt.plot(u[0:1000],label = "u")
plt.plot(v[0:1000],label = "v")
plt.legend()

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
def return_marker_side(list_names,side):
    marker_on_side = []
    for name in list_names:
        if side in name:
            marker_on_side.append(name)
    return marker_on_side
##

PM = []
for fichier in file_list:
    print(fichier)
    acq = btkTools.smartReader(fichier)

    matx = []
    full_names = []
    names = ['LASI', 'RASI', 'LPSI', 'RPSI', 'LTHI', 'LKNE', 'LTIB', 'LANK', 'LHEE', 'LTOE', 'RTHI', 'RKNE', 'RTIB',
             'RANK', 'RHEE', 'RTOE']
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

    feat_cols = ['feature' + str(i) for i in range(x.shape[1])]
    normalised_dataset = pd.DataFrame(x, columns=feat_cols)


    pca = PCA(n_components=10)
    principalComponents = pca.fit_transform(x)

    principal_breast_Df = pd.DataFrame(data=principalComponents
                                       , columns=['principal component 1', 'principal component 2',
                                                  'principal component 3', 'principal component 4',
                                                  'principal component 5','principal component 6',
                                                  'principal component 7','principal component 8',
                                                  'principal component 9','principal component 10'])
    PM.append(principal_breast_Df)
    print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))

##
#/BaselinePiGwithevent.c3d"
acq = btkTools.smartReader(file_a)

gait_cycle = correct_gaitcycles(acq)

##
import matplotlib.pyplot as plt
plt.plot(acq.GetPoint("LFootProgressAngles").GetValues()[:,1])
##
import numpy as np
import sklearn
from sklearn.decomposition import PCA
X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
pca = PCA(n_components=2)
pca.fit(X)
print(pca.explained_variance_ratio_)
##
matx = []
full_names = []
names = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles","LKneeAngles", "LPelvisAngles", "LSpineAngles", "LThoraxAngles"]
for name in names:
    matx.append(acq.GetPoint(name).GetValues()[:,0])
    matx.append(acq.GetPoint(name).GetValues()[:, 1])
    matx.append(acq.GetPoint(name).GetValues()[:, 2])

    full_names.append(name+"_x")
    full_names.append(name + "_y")
    full_names.append(name + "_z")
print(np.shape(np.transpose(matx)))
print(np.shape(full_names))
##

dataset = pd.DataFrame(columns = full_names,data=np.transpose(matx))
print(dataset)
features = full_names
##
from sklearn.preprocessing import StandardScaler
x = dataset.loc[:, features].values
x = StandardScaler().fit_transform(x) # normalizing the features
x.shape
###
np.mean(x),np.std(x)

##
feat_cols = ['feature'+str(i) for i in range(x.shape[1])]
normalised_dataset = pd.DataFrame(x,columns=feat_cols)
print(normalised_dataset.tail())

##
from sklearn.decomposition import PCA
pca = PCA(n_components=5)
principalComponents = pca.fit_transform(x)

##
principal_breast_Df = pd.DataFrame(data = principalComponents
             , columns = ['principal component 1', 'principal component 2','principal component 3','principal component 4','principal component 5'])
print(principal_breast_Df.tail())
print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
##
plt.plot(principal_breast_Df['principal component 1'][0:1000])
plt.plot(principal_breast_Df['principal component 2'][0:1000])
plt.plot(principal_breast_Df['principal component 3'][0:1000])
##

matx = []
names = [ "LAnkleAngles", "LFootProgressAngles", "LHipAngles","LKneeAngles", "LPelvisAngles", "LSpineAngles", "LThoraxAngles"]
for name in names:
    matx.append([name+"_x",acq.GetPoint(name).GetValues()[:,0]])
    matx.append([name+"_y",acq.GetPoint(name).GetValues()[:, 1]])
    matx.append([name+"_z",acq.GetPoint(name).GetValues()[:, 2]])
##
import pandas as pd
df = pd.DataFrame(matx)
print(df)
##

pca = PCA()
pca.fit(matx)
print(pca.explained_variance_ratio_)
print(pca.singular_values_)
##
compo = pca.components_
print(compo.shape)
print(compo[0].shape)
##
plt.plot(compo[0][0:1000])
plt.plot(compo[1][0:1000])

##

