# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

## Environment Variables

In order to run the library code, first execute the following cmd:
``` 
source setup.sh
```
_(This must be ran in each new terminal session, or added to your ~/.bashrc file using the full path to setup.sh)_

This script just appends your cloned location of this library to your PYTHONPATH, so scripts in /suite_scripts and other locations on your machine can find the library code.

Additionally you can specify which config file to use by setting the 'SUITE_CONFIG' environment variable, for example:
``` 
export SUITE_CONFIG="rixSuiteConfig.py" 
```
_(relative or full paths work)_  
You can also set the config-file using the '-cf' or '--configFile' cmd-line arguments _(note: if set, the environment variable overrides this cmd-line option)_  
If neither of the above are set, the suite will try to use _suiteConfig.py_. If no config file can be found and read, the library will fail-out early.

## File organization: 
* /calibrationSuite: The library code lives here, and the functions can be imported into other scripts as such:
```
	from calibrationSuite.basicSuiteScript import * 
	from calibrationSuite.fitFunctions import * 
	from calibrationSuite.Stats import * 
	from calibrationSuite.cluster import *
```
_(documentation on the library functionality is still to come, but example usage is seen in the /suite_scripts folder)_

* /suite_scripts: scripts that use the calibrationSuite library code

* /standalone_scripts: scripts that do not use the calibrationSuite library code

* /tests: tests files, can be ran with 'pytest .' from the root project directory 
_(Currently only test for the fitFunctions library file is running, more tests are to be added)_

* /data: misc data files from the rixx1003721 scripts directory, saving for now but most files will probably be deleted later

## Current Status:

main branch tag v1.0.0 are the scripts used for the 2/17/24 beamtime 
* only changes made are to file organization, and to import statements so work with new organization 
* large changes will be merged into ontop of this, but original scripts can be accessed by checking out this tag
* future beamtimes can be tagged as well

## Developers:

If you are new to git/github, start here: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060)

Then read the following for an overview of the development process: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464)