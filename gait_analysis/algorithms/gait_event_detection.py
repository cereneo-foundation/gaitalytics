# Code a function which is able to detect gait events (Zeni et al., 2008)
# Heel Strike, Toe off
# As input you will probably need 3 nparray's (numpy) of the same length
# hip points, heel point and frame number
# As output i want lists of the events with the frame number in it
def zenis_gait_event_detection(heel_point_array=[], hip_point_array=[], frame_no=[]):
    HS = [1, 23, 56]
    TO = [12, 45, 65]
    return [HS, TO]

