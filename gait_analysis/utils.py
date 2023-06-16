
def min_max_norm(data):
    scale_min = -1
    scale_max = 1
    max_data = max(data)
    min_data = min(data)
    diff = max_data - min_data
    return [((entry - min_data) * (scale_max - scale_min) / diff) + scale_min for entry in data]




