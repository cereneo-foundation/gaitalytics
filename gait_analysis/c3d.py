#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from ezc3d import c3d
import tkinter
from tkinter import messagebox
from enum import Enum
from statistics import mean

import btk
import ezc3d
import numpy as np

ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


class PointDataType(Enum):
    Marker = 0
    Angles = 1
    Forces = 2
    Moments = 3
    Power = 4
    Scalar = 5
    Reaction = 6


class AxesNames(Enum):
    x = 0
    y = 1
    z = 2


class GaitEventContext(Enum):
    """
    Representation of gait event contexts. At the moment mainly left and right
    """
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def get_contrary_context(cls, context: str):
        if context == cls.LEFT.value:
            return cls.RIGHT
        return cls.LEFT


class C3dAquisition:
    """
    Parameters:
            FullPath:       String of the file path
    Return:
            GetC3DData:     c3d Object
    """

    def __init__(self, full_path):

        self.RetrieveC3dData(full_path)

    def RetrieveC3dData(self, full_path):

        # Create some dictionaries to store data
        self.Gen = {
            "PathName": [],
            "FileName": [],
            "SubjName": [],
            "SubjMass": [],
            "SubjHeight": [],
            "ModelUsed": [],
            "NumbItems": [],
            "Vid_FirstFrame": [],
            "Vid_LastFrame": [],
            "Vid_SampRate": [],
            "Analog_FirstFrame": [],
            "Analog_LastFrame": [],
            "Analog_SampRate": [],
            "Analog_NumbChan": [],
            "AnalogUnits": [],
            "PointsUnit": [],
            "AnglesUnit": [],
            "ForcesUnit": [],
            "MomentsUnit": [],
            "PowersUnit": [],
            "ScalarsUnit": [],
            "SubjLLegLength": [],
            "SubjRLegLength": [],
            "ForcePlateOrigin": [],
        }

        self.Labels = {
            "PointsName": [],
            "Markers": [],
            "Angles": [],
            "Scalars": [],
            "Powers": [],
            "Forces": [],
            "Moments": [],
            "AnalogsName": [],
            "EventLabels": [],
            "AnalysisNames": [],
        }

        self.Data = {
            "AllPoints": [],
            "Markers": [],
            "Angles": [],
            "Scalars": [],
            "Powers": [],
            "Forces": [],
            "Moments": [],
            "Analogs": [],
        }

        # returns a handle to RetrieveC3dData
        self.c3d = c3d(os.path.join(full_path))

        self.GetHeader(full_path)
        self.GetSubjects()
        self.GetPoint()
        self.GetAnalog()
        self.GetForcePlatForm()
        self.GetEventContext()
        self.GetAnalysis()
        self.GetProcessing()

    def GetHeader(self, fullPath):
        if "header" in self.c3d:
            self.Gen["PathName"] = fullPath  # get the fullPath to the file
            self.Gen["FileName"] = os.path.basename(fullPath)  # get only the file name
            if "points" in self.c3d["header"]:  # if points exist
                self.Gen["NumbItems"] = self.c3d["header"]["points"][
                    "size"
                ]  # get number items (markers, angles, moments, etc.)
                self.Gen["Vid_FirstFrame"] = self.c3d["header"]["points"]["first_frame"]  # get the cameras first frame
                self.Gen["Vid_LastFrame"] = self.c3d["header"]["points"]["last_frame"]  # get the cameras last frame
                self.Gen["Vid_SampRate"] = self.c3d["header"]["points"]["frame_rate"]  # get the cameras sample rate
            if "analogs" in self.c3d["header"]:  # if analogs exist
                self.Gen["Analog_FirstFrame"] = self.c3d["header"]["analogs"][
                    "first_frame"
                ]  # get the analogs first frame
                self.Gen["Analog_LastFrame"] = self.c3d["header"]["analogs"]["last_frame"]  # get the analogs last frame
                self.Gen["Analog_SampRate"] = self.c3d["header"]["analogs"]["frame_rate"]  # get the analogs sample rate
                self.Gen["Analog_NumbChan"] = self.c3d["header"]["analogs"][
                    "size"
                ]  # get the analogs number of channels

    def GetSubjects(self):
        if "SUBJECTS" in self.c3d["parameters"]:
            if self.c3d["parameters"]["SUBJECTS"]["USED"]["value"][0] > 0:  # if exist data
                self.Gen["ModelUsed"] = self.c3d["parameters"]["SUBJECTS"]["MARKER_SETS"]["value"]  # get the model used
                self.Gen["SubjName"] = self.c3d["parameters"]["SUBJECTS"]["NAMES"][
                    "value"
                ]  # get the name of the subject

    def GetPoint(self):
        if "POINT" in self.c3d["parameters"]:
            if self.c3d["parameters"]["POINT"]["USED"]["value"][0] > 0:  # if exist data
                self.Labels["PointsName"] = self.c3d["parameters"]["POINT"]["LABELS"][
                    "value"
                ]  # get all the labels (markers, angles, etc.)
                self.Gen["PointsUnit"] = self.c3d["parameters"]["POINT"]["UNITS"]["value"][
                    0
                ]  # get the units of the coodinates
                self.Data["AllPoints"] = self.GetPointData("PointsName")  # get data of all items (markers, angles,etc.)

                ExtList = list()  # temp list
                if "TYPE_GROUPS" in self.c3d["parameters"]["POINT"]:  # determine if groups exist (model outputs)
                    Groups = self.c3d["parameters"]["POINT"]["TYPE_GROUPS"]["value"]  # groups available in C3D
                    PGroups = ["ANGLES", "FORCES", "MOMENTS", "POWERS", "SCALARS"]  # possible groups available in C3D
                    GroupsInC3D = sorted(list(set(PGroups) & set(Groups)))  # determine the real groups in C3D

                    for k in range(0, len(GroupsInC3D)):
                        self.Labels[GroupsInC3D[k].title()] = self.GetLabels(GroupsInC3D[k])  # store group labels

                        # get the points for each item in TYPE_GROUPS available
                        MyList = self.GetLabels(GroupsInC3D[k])  # temp list
                        self.Data[GroupsInC3D[k].title()] = self.GetData_Groups(
                            MyList
                        )  # store the data for each group available in c3d

                        ExtList.extend(MyList)  # create a temp list of all labels in groups
                        self.GetUnits(GroupsInC3D[k])  # get the units of each group

                self.Labels["Markers"] = sorted(
                    list(set(self.Labels["PointsName"]) ^ set(ExtList))
                )  # add only the labels for markers
                self.Data["Markers"] = self.GetData_Groups(self.Labels["Markers"])  # add vectors XYZ of markers
            else:
                # hide tk main window
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showwarning("Warning", "No coordinates available in C3D File", parent=root)

    def GetAnalog(self):
        if "ANALOG" in self.c3d["parameters"]:
            if self.c3d["parameters"]["ANALOG"]["USED"]["value"][0] > 0:  # if data exist
                self.Labels["AnalogsName"] = self.c3d["parameters"]["ANALOG"]["LABELS"]["value"]  # get channel names
                self.Gen["AnalogUnits"] = self.c3d["parameters"]["ANALOG"]["UNITS"]["value"]  # get analog units
                self.Data["Analogs"] = self.GetAnalogData("AnalogsName")

    def GetForcePlatForm(self):
        if "FORCE_PLATFORM" in self.c3d["parameters"]:
            if self.c3d["parameters"]["FORCE_PLATFORM"]["USED"]["value"][0] > 0:  # if exist data
                self.Gen["ForcePlateOrigin"] = self.c3d["parameters"]["FORCE_PLATFORM"]["ORIGIN"][
                    "value"
                ]  # get the origin of force plate

    def GetEventContext(self):
        if "EVENT_CONTEXT" in self.c3d["parameters"]:
            if self.c3d["parameters"]["EVENT_CONTEXT"]["USED"]["value"][0] > 0:  # if exist data
                self.Labels["EventLabels"] = self.c3d["parameters"]["EVENT_CONTEXT"]["LABELS"][
                    "value"
                ]  # get the origin of force plate

    def GetAnalysis(self):
        if "ANALYSIS" in self.c3d["parameters"]:
            if self.c3d["parameters"]["ANALYSIS"]["USED"]["value"][0] > 0:  # if exist data
                self.Labels["AnalysisNames"] = self.c3d["parameters"]["ANALYSIS"]["NAMES"][
                    "value"
                ]  # get the origin of force plate

    def GetProcessing(self):
        if "PROCESSING" in self.c3d["parameters"]:
            self.Gen["SubjHeight"] = self.c3d["parameters"]["PROCESSING"]["Height"][
                "value"
            ]  # get the height of the subject
            self.Gen["SubjMass"] = self.c3d["parameters"]["PROCESSING"]["Bodymass"][
                "value"
            ]  # get the mass of the subject
            self.Gen["SubjLLegLength"] = self.c3d["parameters"]["PROCESSING"]["LLegLength"][
                "value"
            ]  # get the LLegLenght of the subject
            self.Gen["SubjRLegLength"] = self.c3d["parameters"]["PROCESSING"]["RLegLength"][
                "value"
            ]  # get the RLegLenght of the subject

    def GetAnalogData(self, Name):
        data = self.c3d["data"]["analogs"]
        dicts = {}
        for k in range(0, data.shape[1]):
            ListStr = self.Labels[Name][k]  # iterate over list and get keys
            dicts[ListStr] = data[0][k]
        return dicts

    def GetPointData(self, Name):
        data = self.c3d["data"]["points"]
        dicts = {}
        for k in range(0, data.shape[1]):
            ListStr = self.Labels[Name][k]
            dicts[ListStr] = data[0:4, k]
        return dicts

    def GetLabels(self, Names):
        if Names in self.c3d["parameters"]["POINT"]:
            return self.c3d["parameters"]["POINT"][Names]["value"]

    def GetData_Groups(self, Item):
        dicts = {}
        for key in Item:
            dicts[key] = self.Data["AllPoints"][key]
        return dicts

    def GetUnits(self, GroupsInC3D):
        GroupsUnit = ["AnglesUnit", "ForcesUnit", "MomentsUnit", "PowersUnit", "ScalarsUnit"]  # temp variable
        Units = ["ANGLE_UNITS", "FORCE_UNITS", "MOMENT_UNITS", "POWER_UNITS", "SCALAR_UNITS"]  # temp variable
        for kk in range(0, len(GroupsUnit)):
            if GroupsUnit[kk].lower().find(GroupsInC3D.lower(), 0, len(GroupsInC3D)) != -1:
                self.Gen[GroupsUnit[kk]] = self.c3d["parameters"]["POINT"][Units[kk]]["value"][
                    0
                ]  # add the group units to the header
                break


if __name__ == "__main__":
    C3DData(None, path_to_c3d)


class C3dAcquisition:
    """
    Main entry point to handle c3d files
    """

    def __init__(self, acq: ezc3d.c3d):
        self.acq = acq

    @property
    def acq(self) -> ezc3d.c3d:
        return self._acq

    @acq.setter
    def acq(self, acq: ezc3d.c3d):
        self._acq = acq

    def get_number_of_points(self) -> int:
        """
        Returns the amount of stored points in c3d
        :return: amount of stored points
        """
        return self.acq['header']['points']['size']

    def get_point_frame_number(self) -> int:
        """
        Returns the number of frames in points
        :return: number of frames
        """
        return self.acq['parameters']['POINT']['FRAMES']['value'][0]

    def get_point_first_frame(self) -> int:
        """
        Get index of first frame
        :return:  index of first frame
        """
        return self.acq['header']['points']['first_frame']

    def get_point_last_frame(self) -> int:
        """
        Get index of last frame
        :return:  index of last frame
        """
        return self.acq['header']['points']['last_frame']

    def get_point(self, index) -> btk.btkPoint:
        """
        Returns a specific point either py name or index
        :param index: name or index of the required point
        :return: point object
        """
        if index is Enum:
            index = self.acq.get("parameters").get("POINT").get("LABELS").get("value").index(index.value)
        elif index is str:
            index = self.acq.get("parameters").get("POINT").get("LABELS").get("value").index(index)

        self.acq.get("data")
        print(index)
        return None

    @staticmethod
    def read_btk(filename) -> C3dAcquisition:
        """
        read a c3d with btk

        Args:
            filename (str): filename with its path
        """
        c3d = ezc3d.c3d(filename)
        acq = C3dAcquisition(c3d)
        # sort events
        #        acq.sort_events()

        return acq

    def write_btk(self, filename):
        """
        write a c3d with Btk

        Args:
            acq (btk.acquisition): a btk acquisition instance
            filename (str): filename with its path
        """
        self.acq.write(filename)

    def sort_events(self):
        """
        sort events in acquisition

        Args:
            acq (btkAcquisition): a btk acquisition instance

        """
        events = self.acq.GetEvents()

        value_frame = {}
        for event in btk.Iterate(events):
            if event.GetFrame() not in value_frame:
                value_frame[event.GetFrame()] = event

        sorted_keys = sorted(value_frame)

        newEvents = btk.btkEventCollection()
        for key in sorted_keys:
            newEvents.InsertItem(value_frame[key])

        self.acq.ClearEvents()
        self.acq.SetEvents(newEvents)


class C3dPoint:
    """
    Class to store c3d Point information
    """

    def get_values(self) -> np.ndarray:
        pass


def is_progression_axes_flip(left_heel, left_toe):
    return 0 < mean(left_toe[AxesNames.y.value] - left_heel[AxesNames.y.value])


def correct_points_frame_by_frame(acq: C3dAcquisition):
    frame_size = acq.get_point_frame_number()
    correction = get_fastest_point_by_frame(acq, 1)
    for frame_number in range(1, frame_size):
        if (frame_number + 2) < frame_size:
            correction_new = get_fastest_point_by_frame(acq, frame_number + 1)
        correct_points_in_frame(acq, frame_number, correction)
        correction += correction_new


def correct_points_in_frame(acq_trial: C3dAcquisition, frame_number: int, correction: float):
    print(f"{frame_number}:{correction}")
    for point_number in range(0, acq_trial.get_number_of_points()):
        acq_trial.get_point(point_number).SetValue(frame_number, 1,
                                                   (acq_trial.get_point(point_number).GetValue(frame_number,
                                                                                               1) + correction))


def get_fastest_point_by_frame(acq_trial: C3dAcquisition, frame_number: int) -> float:
    rfmh_point = acq_trial.get_point("RFMH")
    rhee_point = acq_trial.get_point("RHEE")
    lfmh_point = acq_trial.get_point("LFMH")
    lhee_point = acq_trial.get_point("LHEE")
    lfmh_dist = lfmh_point.GetValue(frame_number - 1, 1) - lfmh_point.GetValue(frame_number, 1)
    lhee_dist = lhee_point.GetValue(frame_number - 1, 1) - lhee_point.GetValue(frame_number, 1)
    rfmh_dist = rfmh_point.GetValue(frame_number - 1, 1) - rfmh_point.GetValue(frame_number, 1)
    rhee_dist = rhee_point.GetValue(frame_number - 1, 1) - rhee_point.GetValue(frame_number, 1)
    return np.min([lfmh_dist, lhee_dist, rfmh_dist, rhee_dist])
