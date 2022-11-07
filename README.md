# Gait_Analysis

This Python package delivers tools and state-of-the-art
algorithms to analyze 3D motion capture data.
This library is currently only adapted for sensor data
from a Motek CAREN system.

## Installation

This library depends on ezc3d  (https://github.com/pyomeca/ezc3d)
please follow the instructions on their site to install the dependency

## Usage

### C3DFileWrapper

```python
import ezc3d
from gait_analysis.file_utils import C3dFileWrapper

c3d_file = ezc3d.c3d("path/to/c3d_file.c3d", extract_forceplat_data=True)
c3d_wrapper = C3dFileWrapper(c3d_file)
point_labels = c3d_wrapper.get_point_labels()
# returns data of all points and directions
c3d_wrapper.get_points(point_labels)
```