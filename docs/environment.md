# Setup Environment

When running on S3DF, you will first need to setup your environment so you can run _python_, _psana_, and other need programs:
```
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh
```

Then you can execute the following to setup some project-specific things:
```
source setup.sh
```
_(This must be ran in each new terminal session, or added to your ~/.bashrc file using the full path to setup.sh)_

This script simplifies setting up the terminal environment and will be all that most script users will need to do. 

This script does the following:
* appends your cloned location of this library to your _PYTHONPATH_, so scripts in _/suite_scripts_ and other locations on your machine can find the library code.
* sets the library's output-root to the shared /rix dir used for the current experiment. 
* sets the config file to the currently used _rixSuiteConfig.py_ file.

The rest of the page has more detail on configuring the scripts.

### Specify Output Root

The output-root determines where the library will look for an output folder. 

For example, if the root is set to the default value _/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/_, the library will look for an output dir _../scan_ in the location _/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/../scan_.

The output-directory can be set using the _-p \<dir_name>_ cmdline arg.

Setting the var to nothing (_export OUTPUT_ROOT=_) will have the library look for an output folder relative to the location of the current script being ran.  


### Point to Config File

Specify which config file for the library to use by setting the 'SUITE_CONFIG' environment variable:
```
export SUITE_CONFIG="rixSuiteConfig.py" 
```
_(relative or full paths should work)_

You can also set the config-file using the '-cf' or '--configFile' cmd-line arguments 
_(note: if set, the environment variable will always override this cmd-line option)_

If neither of the above are set, the suite will try to use a default file named _suiteConfig.py_. 

If no config file can be found and read, the library will fail-out early.