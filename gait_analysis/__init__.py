import os

try:
    os.add_dll_directory("C:/OpenSim 4.4/bin")
except FileNotFoundError as e:
    print("Error loading opensim")
