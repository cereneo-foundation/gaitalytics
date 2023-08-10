# Gaitalytics

[<img src="https://github.com/cereneo-foundation/gaitalytics/blob/6d88443708bab2dbe300534bd52262d973397bcb/resources/logos/Gaitalytics_noBackground.png" alt="Gaitalytics logo" width="200"/>](https://github.com/cereneo-foundation/gaitalytics)

This Python package provides a comprehensive set of tools and advanced algorithms for analyzing 3D motion capture data.
It is specifically designed to process gait data stored in c3d format. Prior to utilizing the features of gaitalytics,
it is necessary to perform data labeling, modeling, and filtering procedures.

The library's versatility allows it to be adaptable to various marker sets and modeling algorithms,
offering high configurability.

> **Note**
> Current pre-release is only tested with data acquired with Motek Caren, HBM2 Lower Body Trunk and PIG. 

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



## Usage

### Installation

Please be aware of the dependency of gaitalytics to Biomechanical-ToolKit (BTK). To install follow the
instructions [here](https://biomechanical-toolkit.github.io/docs/Wrapping/Python/_build_instructions.html) or use
conda-forge
version [here](https://anaconda.org/conda-forge/btk)

Fast install with anaconda:

````shell
pip install gaitalytics
conda install -c conda-forge btk
````

### Configuration

Gaitalytics can be used with any marker set, which at least includes four hip markers (left front/back, right
front/back)
and four foot markers (left heel/toe, right heel/toe) and four ankle makers (left medial/lateral, right medial lateral).

All functionalities in the libraries only take points into account which are configured in as specific yaml file. 
Working example file can be found [here](https://github.com/cereneo-foundation/gaitalytics/blob/94bbc73072535d7f1e53ea935b6145194b137f09/settings/hbm_pig.yaml)



Minimal requirements would look like this:
````yaml
marker_set_mapping:
  left_back_hip: LASIS
  right_back_hip: RASIS
  left_front_hip: LPSIS
  right_front_hip: RPSIS
  
  left_lat_malleoli: LLM
  right_lat_malleoli: RLM
  left_med_malleoli: LMM
  right_med_malleoli: RMM

  right_heel: RHEE
  left_heel: LHEE
  right_meta_2: RMT2
  left_meta_2: LMT2
  
  com: COM
  left_cmos: cmos_left
  right_cmos: cmos_right
  
model_mapping:
````
> **Warning**
> Do not rename keys of the minimal setting

### Pipline

Please take the resources in
the [example folder](https://github.com/cereneo-foundation/gaitalytics/tree/94bbc73072535d7f1e53ea935b6145194b137f09/examples)
for advice.
###
