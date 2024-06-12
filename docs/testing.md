# Testing

Tests are only need to be run by those actively developing the suite.  
To setup for running the tests, run the following cmd from the repo root dir:
```
source setup_developers.sh
```
This installs the 'pillow' python dependency (used for diffing .png files), and downloads the test_data submodule.  
_(note: only needs to be run once per-repo, unless you manually de-init'd the submodule and want it setup again)_  
_(note: this is unlike setup.sh, which needs to be run per-each terminal session (or added to ~/.bashrc))_  

You can run all the tests with the following:
```
pytest .
```
_(note: this works from either the project root-dir and also the /tests dir)_

Running on _S3DF_ (to use psana library) is required to run all of the tests, but a subset can still be run without.

You can run an individual test-file by specifying the path:
```
pytest tests/test_SuiteScripts.py
```

And run an individual test-case within the test-file by using the '-k' flag:
```
pytest tests/test_SuiteScripts.py -k test_Noise
```

These tests verify that the code in _/calibrationSuite_ and _/suite\_scripts_ is currently working as expected.  

_test\_SuiteScripts.py_ runs the files in _/suite\_script_ and diffs their real output against expected output in _/tests/test\_data_  

_/tests/test\_data_ stores data from this repo: <https://github.com/slaclab/beamtime-calibration-suite-test-data>
The repo is added as a [git submodule](https://gist.github.com/gitaarik/8735255), and should be setup by the _setup_developers.sh_ script.  
Since the test data is large, [LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) is used and needs to be installed. (LFS is installed already on _S3DF_)  


Some more info on testing, such as adding now data to the _test\_data_ submodule or add a new test-case to_suite\_scripts_ tests, can be found [in this file.](https://github.com/slaclab/beamtime-calibration-suite/blob/development/tests/test_SuiteScripts.py)
