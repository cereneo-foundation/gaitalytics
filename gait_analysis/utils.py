import numpy
def FS_or_FO(FP_signal: numpy.ndarray, FP_detection: numpy.ndarray):
    """Iterate through each event detected by detect_onset and determine if the event is a FootStrike
        or a FootOff. Return array of ["Type of event":str,index of event:int]
            Args:
                FP_signal (array): Signal of the force plate
                FP_detection (array): detection from detect_onset
            """
    len_FP_signal = len(FP_signal)
    detected_FS_or_FO = []
    for couple_indx in FP_detection:
        for indx in couple_indx:
            if indx > 20 and indx < len_FP_signal - 20:  # Avoid to take the edge (detected as event) in consideration

                diff = FP_signal[indx - 20] - FP_signal[indx + 20]  # positive or negative slope (FeetOff or FeetStike)
                if diff > 0:
                    detected_FS_or_FO.append(["Foot Off", indx])
                else:
                    detected_FS_or_FO.append(["Foot Strike", indx])
    return detected_FS_or_FO  # Contain the label of the event and the corresponding index
