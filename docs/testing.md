# Testing

The tests only really need to be run by those actively developing the suite.  
To setup the tests, run the following from the repo root dir:
```
source setup_developers.sh
```
This installs the 'pillow' python dependency (used for diffing .png files), and downloads the test_data submodule.  
_(note: only needs to be run once per-repo, unless you manually de-init'd the submodule and want it setup again)_  
_(note: this is unlike setup.sh, which needs to be run per-each terminal session (or added to ~/.bashrc))_  

Data for testing is stored in this repo: https://github.com/slaclab/beamtime-calibration-suite-test-data  
This repo is added as a [git submodule](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules) in the location: _tests/test\_data_.  
Since the test data is large, [LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) is used and needs to be installed. (LFS is installed already on _S3DF_)  


Some more info on testing, such as adding now data to the _test\_data_ submodule or add new _suite\_scripts_ tests, can be found [in this file](https://github.com/slaclab/beamtime-calibration-suite/blob/development/tests/test_SuiteScripts.py)