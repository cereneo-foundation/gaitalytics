# -*- coding: utf-8 -*-
import os
import pyCGM2
from pyCGM2.Utils import files
from pyCGM2.Tools import btkTools
from pyCGM2.ForcePlates import forceplates
from pyCGM2 import enums
from pyCGM2.Lib.CGM import cgm2_5

LOGGER = pyCGM2.LOGGER
###
# data
DATA_PATH = "C:\\Users\\simon\\OneDrive\\Bureau\\CERENEO\\Data\\pyCGM2\\26_01_pyCGM2_Simon\\"
staticFile ="Calib02.c3d" # static trial
trialName = "1min.c3d" # gait trial

datapath_settings= r"C:\Users\simon\anaconda3\envs\Gait_Analysis\Lib\site-packages\pyCGM2\Settings"

# setting
settings = files.loadModelSettings(datapath_settings,"CGM2_5-pyCGM2_bis.settings")

###
# CGM2.5 CALIBRATION
#-------------------

acqStatic = btkTools.smartReader(DATA_PATH+staticFile) # construct the btk.Acquisition instance

# calibration options from settings
leftFlatFoot = settings["Calibration"]["Left flat foot"]
rightFlatFoot= settings["Calibration"]["Right flat foot"]
headFlat= settings["Calibration"]["Head flat"]
translators = settings["Translators"]
markerDiameter = settings["Global"]["Marker diameter"]
HJC = settings["Calibration"]["HJC"]
pointSuffix = settings["Global"]["Point suffix"]
markerweight = settings["Fitting"]["Weight"]
# anthropometric parameters
required_mp = dict()
required_mp["Bodymass"] = 83.0
required_mp["Height"]= 1720
required_mp["LeftLegLength"] = 0
required_mp["LeftKneeWidth"] = 0
required_mp["RightLegLength"] = 0
required_mp["RightKneeWidth"] = 0
required_mp["LeftAnkleWidth"] = 0
required_mp["RightAnkleWidth"] = 0
required_mp["LeftSoleDelta"] = 0
required_mp["RightSoleDelta"] = 0
required_mp["LeftShoulderOffset"] = 0
required_mp["LeftElbowWidth"] = 0
required_mp["LeftWristWidth"] = 0
required_mp["LeftHandThickness"] = 0
required_mp["RightShoulderOffset"] = 0
required_mp["RightElbowWidth"] = 0
required_mp["RightWristWidth"] = 0
required_mp["RightHandThickness"]= 0

optional_mp = dict()
optional_mp["InterAsisDistance"]= 0
optional_mp["LeftAsisTrocanterDistance"]= 0
optional_mp["LeftTibialTorsion"]= 0
optional_mp["LeftThighRotation"]= 0
optional_mp["LeftShankRotation"]= 0
optional_mp["RightAsisTrocanterDistance"]= 0
optional_mp["RightTibialTorsion"]= 0
optional_mp["RightThighRotation"]= 0
optional_mp["RightShankRotation"]= 0
##
# calibrate function
model,finalAcqStatic,error = cgm2_5.calibrate(DATA_PATH,
    staticFile,
    translators,
    markerweight,
    required_mp,
    optional_mp,
    False,
    leftFlatFoot,
    rightFlatFoot,
    headFlat,
    markerDiameter,
    HJC,
    pointSuffix)
###
# CGM2.5 FITTING
#----------------

# fitting options from settings
momentProjection = enums.enumFromtext(settings["Fitting"]["Moment Projection"],enums.MomentProjection)
pointSuffix = settings["Global"]["Point suffix"]

# force plate assignement
acq = btkTools.smartReader(DATA_PATH+trialName) # btk.Acquisition instance
mfpa = forceplates.matchingFootSideOnForceplate(acq) #detect correct foot contact with a force plate
###
# fitting function

acqGait,detectAnomaly = cgm2_5.fitting(model,DATA_PATH, trialName,
    translators,
    markerweight,
    False,
    markerDiameter,
    pointSuffix,
    mfpa,
    momentProjection,
    frameInit= None, frameEnd= None )# acqGait updated with CGM2.1 ouputs ( kinematics and kinetics)

# EXPORT
# -------
btkTools.smartWriter(acqGait, DATA_PATH+trialName[:-4]+"-modelled.c3d") # save the btk.Acquisition instance as a new c3d with the suffix "-modelled"

###

from pyCGM2.Lib import eventDetector
from pyCGM2.Tools import btkTools
import unittest
from gait_analysis.events import GaitEventDetectorFactory
acqGait= btkTools.smartReader(DATA_PATH+"1min-modelled_event.c3d") # construct the btk.Acquisition instance

acqGait.ClearEvents()
eventDetector.zeni(acqGait,footStrikeOffset=50,footOffOffset=50)
btkTools.smartWriter(acqGait, DATA_PATH+trialName[:-4]+"-modelled_event.c3d")

###

from pyCGM2.Report import normativeDatasets
from pyCGM2.Lib import analysis
from pyCGM2.Lib import plot

# data
modelledFilenames = ["1min-modelled.c3d"] # two gait trials with both gait event and CGMi model ouptuts


analysisInstance = analysis.makeAnalysis(DATA_PATH, modelledFilenames,
                                          emgChannels=None) # construction of the analysis instance.
normativeDataset = normativeDatasets.NormativeData("Schwartz2008","Free") # selected normative dataset
###
# plots
plot.plot_DescriptiveKinematic(DATA_PATH,analysisInstance,"LowerLimb",normativeDataset)
###
plot.plot_DescriptiveKinetic(DATA_PATH,analysisInstance,"LowerLimb",normativeDataset)
plot.plot_spatioTemporal(DATA_PATH,analysisInstance)

# export as spreadsheet
analysis.exportAnalysis(analysisInstance,DATA_PATH,"spreadsheet")