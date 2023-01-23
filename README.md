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
from pyCGM2.Tools import btkTools
path = "test/data/test.c3d"
acq = btkTools.smartReader(path)
```