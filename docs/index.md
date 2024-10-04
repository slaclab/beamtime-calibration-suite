# Beamtime calibration suite
This repository contains scripts ran during (or in-between) beamtimes to support calibrating LCLS detectors.

Some more general info can be found on the team's confluence [page](https://confluence.slac.stanford.edu/display/LCLSDET/LCLS+Detector+Department+Home) 


### File organization:

The following describes what and where things are:

* _/calibrationSuite_: The library code lives here, and the functions are able to be imported into other scripts as such:
```
from calibrationSuite.basicSuiteScript import BasicSuiteScript
from calibrationSuite import ancillaryMethods
import calibrationSuite.fitFunctions as fitFunctions
...
```
_(documentation on the library functionality is still to come, but example usage is seen by scripts in the suite_scripts folder)_

* _/suite_scripts_: scripts that use the calibrationSuite library code (these can be called 'high-level scripts')
* _/config_files_: files that set values used by the calibrationSuite, which config-file to use is specified by env variable $SUITE_CONFIG
* _/standalone_scripts_: scripts that do not use the calibrationSuite library code (also 'high-level scripts')
* _/tests_: tests files, can be ran with 'pytest .' from the root project directory or from the _tests_ directory.
* _/data_: example data-files used for running the scripts


### Important branches:

* `development`: contains the newest 'good' code, usually has new changes and bug fixes. This is also the default branch for the repo
* `main`: stable code that's used during beamtimes. The code from each beamtime (including the changes made during) is tagged
* `beamtime_<month>_<day>_<year>`: branch we will checkout and push to during a specific beamtime. The date should be the first day of the beamtime.