# Logging

Logging calls are added to the library code, and also to some commonly used files in _/suite_scripts_ to act as [example](https://github.com/slaclab/beamtime-calibration-suite/blob/main/suite_scripts/TimeScanParallelSlice.py)

Using the following method will append log messages to the log-file if it already exists, or create a new log-file if the file doesn't exist

If you want a new log-file for each run of a high-level script, atm you will need to rename the log-file after each run so a new one will be generated

To have your high-level script generate logs from the calibrationSuite library code, add the following at the top of the script:
```
import os
import calibrationSuite.loggingSetup as ls
currFileName = os.path.basename(__file__)
ls.setupScriptLogging("../logs" + currFileName[:-3] + ".log", logging.ERROR)
```
Pass in _logging.INFO_ instead to get alot more output on the state of the program, while also still logging the _logging.ERROR_ messages

You can pass any chosen log-file name to the _setupScriptLogging_ function, but using the above will create and write to file named _beamtime-calibration-suite/logs/\<curr script name\>.log_

To add more logging from the high-level script itself (to the same file specified to _setupScriptLogging_), you can add the following to the top of the script:
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
_(Note: these must take a statement evaluating to a single string, if 'a', 'b', 'c' are strings you can't do 'logger.info(a,b,c)' but can do 'logger.info(a+b+c)'. And if 'a' is an int, must do 'logger.info(str(a)))_