# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

# Docs: https://slaclab.github.io/beamtime-calibration-suite/

# Step-by-step to get running quick!
* First, follow steps **1** through **4**: [setup git and github](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060)
* Next, run the following commands in a terminal (linux or mac terminal should work):  
&emsp;-_(note: lines starting with '#' are comments with explanation and don't need to be ran)_  
&emsp;-_(note: in the 1st command: replace \<slac-username> with your slac linux-username)_
```
# ssh into the s3df machines
ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu
ssh psana

# do setup for s3df environment
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

# download the code
mkdir repos && cd repos
git clone git@github.com:slaclab/beamtime-calibration-suite.git
cd beamtime-calibration-suite
git switch development

# do more environment setup for suite-scripts
source setup.sh

# run an example script
cd suite_scripts
python EventScanParallel.py -r 457
```
If everything is working, the script should start spitting terminal-output like:
```
...
3259 True
3257 True
3256 True
3260 True
Event number foo
```
_Done with step-by-step setup. The following sections provide more detail on the setup process and the code._

## General setup
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

* /suite_scripts: scripts that use the calibrationSuite library code ('high-level scripts')

* /standalone_scripts: scripts that do not use the calibrationSuite library code ('high-level scripts')

* /tests: tests files, can be ran with 'pytest .' from the root project directory 
_(Currently only test for the fitFunctions library file is running, more tests are to be added)_

* /data: example data-files used for running the scripts

## Current Status:

main branch tag v1.0.0 are the scripts used for the 2/17/24 beamtime 
* only changes made are to file organization, and to import statements so work with new organization 
* large changes will be merged into ontop of this, but original scripts can be accessed by checking out this tag
* future beamtimes can be tagged as well

## Developers:

If you are new to git/github, start here: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060)

Then read the following for an overview of the development process: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464)

For commit messages, we can try to follow the PyDM guidelines: https://slaclab.github.io/pydm/development/development.html#commit-guidelines


### Logging

Loggings calls are added to the library code, and also to the [EventScanParallelSlice.py](https://github.com/slaclab/beamtime-calibration-suite/blob/main/suite_scripts/EventScanParallelSlice.py) and
[AnalyzeH5.py](https://github.com/slaclab/beamtime-calibration-suite/blob/main/suite_scripts/AnalyzeH5.py) files in /suite_scripts to act as examples of generating logs from both the library
and high-level scripts.

Using the following method will append log messages to the log-file if it already exists, or create a new
log-file if the file doesn't exist. If you want a new log-file for each run of a high-level script, 
atm you will need to rename the log-file after each run so a new one will be generated.

To have your high-level script generate logs from the calibrationSuite library code, add the following at the top of the script:

```
import os
import calibrationSuite.loggingSetup as ls
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(currFileName[:-3] + ".log", logging.INFO)
```

You can pass a chosen log-file name to the setupScriptLogging function,
but using the above will create and write to file named _\<curr script name>.log_
 
To add additional logging from the high-level script itself(to the same file specified to setupScriptLogging),
you can also add the following to the top of the script:

``` 
import logging
logger = logging.getLogger(__name__)
```

Then can add log statements throughout the script with:

``` 
logger.error("Example error msg!") # for logging when the program goes wrong
logger.exception("Example exception msg!) # for logging error and also including stack-trace in log 
logger.info("Example info msg!") # for logging useful info on the state of the program
```

_(Note: these must take a statement evaluating to a single string, if a,b,c are strings can't do 'logger.info(a,b,c)' but can do 'logger.info(a+b+c)'. Also for example if a is an int, must do 'logger.info(str(a)))_
