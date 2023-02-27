import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os
from PiGPipeline_SimonPlayground.Pipeline_make_PiGfiles import make_PiG_conversion
from PiGPipeline_SimonPlayground.Pipeline_Event import correct_gaitcycles, return_gait_one_side
from gait_analysis.utils import return_max_length, create_matrix_padded
from pyCGM2.Tools import btkTools
from pyCGM2.Processing import cycle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from scipy import interpolate
from scipy.ndimage import gaussian_filter1d
from sklearn.metrics import mean_squared_error
from kneed import KneeLocator
from sklearn.metrics import silhouette_score
from PiGPipeline_SimonPlayground.DFLOW_code.helper_DFlow import create_datastructure_DFlow,return_match

names_R = ["RAnkleAngles", "RFootProgressAngles", "RHipAngles", "RKneeAngles", "RPelvisAngles", "RSpineAngles",
           "RThoraxAngles"]
names_L = ["LAnkleAngles", "LFootProgressAngles", "LHipAngles", "LKneeAngles", "LPelvisAngles", "LSpineAngles",
           "LThoraxAngles"]
##
session = "C:/ViconData/TMR/SaskiaN_TMR102/20_12_D1/"
baseline_name = "BaselinePiGwithEvents.c3d"
acq_D1 = btkTools.smartReader(session + baseline_name)

gait_cycle_D1 = correct_gaitcycles(acq_D1)
right_side_D1 = return_gait_one_side(gait_cycle_D1, "Right")
##

file_list = []
for root, dirs, files_ in os.walk(session):
    # select file name
    for file in files_:
        # check the extension of files
        if file.endswith('.c3d') and ("PiG" in file) and ("Calib" not in file) and ("Events" in file) and (
                "Baseline" not in file):
            # print whole path of files
            print(os.path.join(root, file))
            file_list.append(os.path.join(root, file))

##
pathDF = r"C:\Users\simon\Desktop\Gait_Analysis\PiGPipeline_SimonPlayground\DFLOW_code\Data"
file_list_df = []
for root, dirs, files_ in os.walk(pathDF):
    # select file name
    for file in files_:
        # check the extension of files
        if file.endswith('.txt') :
            # print whole path of files
            print(os.path.join(root, file))
            file_list_df.append(os.path.join(root, file))
##
game_sessions = []

for i in range(len(file_list)):
    print("extracting gait cycle from ", file_list[i])
    acq = btkTools.smartReader(file_list[i])
    gait_cycle = correct_gaitcycles(acq)

    tmp = list()
    for cycl in gait_cycle:
        if cycl.getEvents("All")[-1].GetFrame()<=30000:
            tmp.append(cycl)
    side_cycle = return_gait_one_side(tmp,"Right")

    cycle_df = create_datastructure_DFlow(file_list_df[i])
    matching = return_match(side_cycle[1:], cycle_df)
    print("Finished matched with",file_list_df[i])
    print("number of matched",len(matching[0]))
    game_sessions.append(matching)

##
def extract_trace(list_cycle, label, dimension):
    dim = {"x": 0, "y": 1, "z": 2}
    trace = []
    for cycl in list_cycle:
        trace.append(cycl.getPointTimeSequenceData(label)[:, dim[dimension]])
    return trace


##

D1 = extract_trace(right_side_D1, "RAnkleAngles", 'x')[1:]

for elem in D1:
    plt.plot(elem)
plt.show()

##
trace_sessions = []

for session in game_sessions:
    trace = extract_trace(session[0], "RAnkleAngles", 'x')
    trace_sessions.append(trace)
##
for tra in trace:
    plt.plot(tra)
##
maxi = [return_max_length(D1)]
for elem in trace_sessions:
    maxi.append(return_max_length(elem))
max_length = np.max(maxi)
print(max_length)


##

def scale_and_pad_matrix(matrix, max_length):
    scaled = []
    for arr in matrix:
        scaled.append(StandardScaler().fit_transform(arr.reshape(-1, 1)))
    scaled_padded = create_matrix_padded(scaled, max_length)
    return scaled_padded

##
D1_scaled_padded = scale_and_pad_matrix(D1,max_length)
feat_cols = ['feature' + str(i) for i in range(len(D1_scaled_padded))]
normalised_dataset = pd.DataFrame(np.transpose(D1_scaled_padded), columns=feat_cols)
print(normalised_dataset)
##

pca = PCA(n_components=2)
principalComponents = pca.fit_transform(D1_scaled_padded)

principal_breast_Df = pd.DataFrame(data=principalComponents
                                   , columns=['principal component 1', 'principal component 2'])
print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
plt.scatter(principal_breast_Df["principal component 1"],principal_breast_Df["principal component 2"])
plt.xlabel('Principal Component - 1',fontsize=20)
plt.ylabel('Principal Component - 2',fontsize=20)
##
plt.plot(principal_breast_Df["principal component 1"])
plt.plot(principal_breast_Df["principal component 2"])
##
session_transformed_pca = []
for session in trace_sessions:
    session_scaled_padded = scale_and_pad_matrix(session,max_length)
    session_transformed_pca.append(pca.transform(session_scaled_padded))

##
colors = ['green','yellow','orange','red','blue','purple']
plt.scatter(principal_breast_Df["principal component 1"],principal_breast_Df["principal component 2"],c="black",label = "Baseline")
plt.xlabel('Principal Component - 1',fontsize=20)
plt.ylabel('Principal Component - 2',fontsize=20)

for i in range(len(session_transformed_pca)):
    for j in range(len(session_transformed_pca[i])):
        mse = game_sessions[i][1][j]
        plt.plot(session_transformed_pca[i][j, 0], session_transformed_pca[i][j, 1], c=colors[i],marker = 'o',markersize=10/mse,alpha=0.5)
plt.legend()

##
game_sessions[0]
##

