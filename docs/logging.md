# Logging

Logging setup and calls have been added to the library code and to some commonly used high-level scripts in _/suite_scripts_, for [example](https://github.com/slaclab/beamtime-calibration-suite/blob/main/suite_scripts/TimeScanParallelSlice.py)

You can make logging calls using the _BasicSuiteScript_ class's _logger_ object.  
The logger can be called with a choice of 3 different logging-levels, depending on the type of output:

```
    bss.logger.info("useful info from the code")
    bss.logger.error("script hit an error")
    bss.logger.exception("script hit a python exception)
```

_logger_ calls are logged to file _log.txt_ _(located in the project's root directory_), and also outputted to the terminal.  
A different log file can be specified with the _--logFile_ cmdline arg _(note: this path gets interpreted as releative to the projects root dir)_. This log file will be created if it doesn't already exist.  
