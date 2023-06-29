
# Gaitalytics
<img src="resources/logos/Gaitalytics_noBackground.png" alt="Gaitalytics logo" width="200"/>

This Python package provides a comprehensive set of tools and advanced algorithms for analyzing 3D motion capture data.
It is specifically designed to process gait data stored in c3d format. Prior to utilizing the features of gaitalytics,
it is necessary to perform data labeling, modeling, and filtering procedures. The library's versatility allows it to be
adaptable to various marker sets and modeling algorithms, offering high configurability.

## Functionalities

### Event Detection

| Method     | Description      | options                                                                                                                                                                                                  |
|:-----------|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Marker     | Zenis 2006       | min_distance = 100: minimum of frames between same event on same context<br/>foot_strike_offset = 0: Amount of frames to offset foot strike<br/>foot_off_offset = 0: Amount of frames to offset foot off | 
| ForcePlate | Split ForcePlate | -                                                                                                                                                                                                        |

### Event Detection Check

| Method  | Description                                      |
|---------|--------------------------------------------------|
| context | Checks Event Sequence HS TO HS TO                |
| spacing | Checks Frames between same event on same context |

### Modelling

| Methode | Description                                               |
|---------|-----------------------------------------------------------|
| com     | creates Center of Mass Marker in c3d                      |
| cmos    | create Continuous Margin of Stability AP ML Marker in c3d |

### Analysis

| Methode        | Description                                                                                                                                        | options                                                                          |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| angles         | min, max, mean, sd, amplitude,<br/>min velocity, max velocity, sd velocity                                                                         | by_phase = True : If metrics should be calculated by standing and swinging phase |
| forces         | min, max, mean, sd, amplitude                                                                                                                      | by_phase = True : If metrics should be calculated by standing and swinging phase |
| moments        | min, max, mean, sd, amplitude                                                                                                                      | by_phase = True : If metrics should be calculated by standing and swinging phase |
| powers         | min, max, mean, sd, amplitude                                                                                                                      | by_phase = True : If metrics should be calculated by standing and swinging phase |
| cmos           | min, max, mean, sd, amplitude                                                                                                                      | by_phase = True : If metrics should be calculated by standing and swinging phase |
| mos            | HS mos, TO mos, HS contra mos,<br/>TO contra mos for both sides                                                                                    | -                                                                                |
| toe_clearance  | minimal toe clearance, <br/>percent swing phase when min toe clearance happened,<br/>toe clearance HS,                                             |
| spatiotemporal | step_length,stride length, cycle duration,<br/>step duration percent, swing duration percent, stance duration percent,<br/>step height, step width |

## Installation

Please be aware of the dependency of gaitalytics to Biomechanical-ToolKit (BTK). To install follow the
instructions [here](https://biomechanical-toolkit.github.io/docs/Wrapping/Python/_build_instructions.html) or use
conda-forge
version [here](https://anaconda.org/conda-forge/btk)

Fast install with anaconda:

````shell
pip install gaitalytics
conda install -c conda-forge btk
````

## Usage

Please take the resources in the example folder for advice.

###