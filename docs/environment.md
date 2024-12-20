# Setup Environment

After you are ssh'd into s3df and ssh'd into the psana computing pool, you will need to setup your environment for _python_, libraries like _psana_, etc:
```
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh
```

Then you can execute the following to setup some project-specific things (must be ran in each new terminal session and from _beamtime-calibration-suite_ folder):
```
source setup.sh
```

This script simplifies setting up the terminal environment and should be all most users will need to do

This script does the following:
  * appends your cloned location of this library to your _PYTHONPATH_, so scripts in _/suite_scripts_ and other locations on your machine can find the library code
  * sets the library's output-root to the shared dir used for the current experiment
  * sets the config file to the currently used config.

The rest of the page has more detail on configuring the scripts.

### Specifying Output Root

The environment variable _OUTPUT_ROOT_ determines where the library will look for output folders.

Setting the variable to . (by doing 'export _OUTPUT_ROOT=._') will have the library look for an output folder relative to the location of the current script being ran. ( . refers to current dir on linux)

For example, if the root is set to the default value `/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/`, the library will look for an output dir `../scan` in the location `/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/../scan`

Then to set the output-directory you can use the `-p <dir_name>` cmdline arg

### Point to Config File

Specify which config file for the library to use by setting the `SUITE_CONFIG` environment variable:
```
export SUITE_CONFIG="rixSuiteConfig.py"
```
_(relative or full paths should work)_

You can also set the config-file using the '-cf' or '--configFile' cmd-line arguments
_(note: if set, the environment variable will always override this cmd-line option)_

If neither of the above are set, the suite will try to use a default file named `suiteConfig.py`

If no config file can be found and read, the library will fail-out early
