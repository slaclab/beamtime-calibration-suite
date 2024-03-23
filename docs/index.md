# Beamtime calibration suite
This repository contains scripts ran during (or in-between) beamtimes to support calibrating LCLS detectors.

Some more general info can be found on the team's confluence page: [https://confluence.slac.stanford.edu/display/LCLSDET/LCLS+Detector+Department+Home](https://confluence.slac.stanford.edu/display/LCLSDET/LCLS+Detector+Department+Home) 


### File organization:

The following describes what and where things are:

* /calibrationSuite: The library code lives here, and the functions can be imported into other scripts as such:
```
from calibrationSuite.basicSuiteScript import * 
from calibrationSuite.fitFunctions import * 
from calibrationSuite.Stats import * 
from calibrationSuite.cluster import *
```
_(documentation on the library functionality is still to come, but example usage is seen in the /suite_scripts folder)_

* /suite_scripts: scripts that use the calibrationSuite library code ('high-level scripts')
* /standalone_scripts: scripts that do not use the calibrationSuite library code ('high-level scripts')
* /tests: tests files, can be ran with 'pytest .' from the root project directory (Currently only test for the fitFunctions library file is running, more tests are to be added)
* /data: example data-files used for running the scripts


### Important branches:

* development: Contains the newest 'good' code, usually has new changes and bug fixes.
* main: Stable code used during beamtimes. The code from each beamtime (including the changes made during) is tagged.
