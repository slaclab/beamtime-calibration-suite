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

You can also set the config-file using the '-cf' or '--configFile' cmd-line arguments (note: if set, the environment variable overrides this cmd-line option)
If neither of the above are set, the suite will try to use suiteConfig.py. If no config file can be found and read, the library will fail-out early.