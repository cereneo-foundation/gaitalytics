# Gait_Analysis

This Python package delivers tools and state-of-the-art
algorithms to analyze 3D motion capture data.
This library is currently only adapted for sensor data
from a Motek CAREN system.

## Installation

Please use anaconda other any other conda distribution to set up the required environment. To install libraries please
use following cli command:

````shell
conda env update --file ./environment.yml
````

After successfully installing the necessary libraries you need to manually install opensim 4.4
https://simtk.org/frs/?group_id=91.
Then manually proceed in following tasks

1. Add OpenSim bin to windows path
2. install opensim lib into conda

   You will find the instructions on this website with title Installing Anaconda and the "opensim" Python package
   https://simtk-confluence.stanford.edu:8443/display/OpenSim/Scripting+in+Python

## Usage

Please take the resources in the example folder for advice.