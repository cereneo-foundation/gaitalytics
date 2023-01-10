# Code a function which is able to detect gait events (Zeni et al., 2008)
# Heel Strike, Toe off
# As input you will probably need 3 nparray's (numpy) of the same length
# hip points, heel point and frame number
# As output i want lists of the events with the frame number in it
import pandas as pd


def get_gait_events(data: pd.DataFrame, method: str) -> pd.DataFrame:
    pass


def zenis_gait_event_detection(heel_point_array: pd.DataFrame, hip_point_array: pd.DataFrame) -> pd.DataFrame:
    HS = [1, 23, 56]
    TO = [12, 45, 65]
    return [HS, TO]

