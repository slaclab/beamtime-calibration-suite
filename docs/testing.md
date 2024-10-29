# Testing

Tests usually only need to be ran by those actively developing the suite, especially after
resolving merge-conflicts, adding in large features, refactoring, etc.

Running on _S3DF_ and ssh'd into the _psana_ pool (to use psana library) is required to run the entire suite of the tests,
but a subset can still be run on a local machine (utilitiy-function tests, etc).
This non-psana subset runs automatically in [github actions](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

In short, running the following will do some useful check the code: (do so after commiting your current changes, since linting/format\ting will modify files):
```
# cd to project root
source setup_developers.sh # only need to run once when initially setting up suite
./lint_and_format.sh # note: will likely code style, but should not modify functionality
pytest .
```

# Details

To setup for running the tests, run the following cmd from the repo root dir:
```
source setup_developers.sh
```
This installs the 'pillow' python dependency (used for diffing .png files), the ruff formatter/linter, and downloads the /test_data submodule.
_(note: only needs to be run once per-repo, unless you manually de-init'd the submodule and want it setup again)_
_(note: this is unlike setup.sh, which needs to be run per-each terminal session (or added to ~/.bashrc))_


The code can be checked with linting by running:
```
./lint_and_format.sh
```
This will [lint](https://en.wikipedia.org/wiki/Lint_(software)) and attempt to auto-apply any fixes, and then format the code.
The script may output linting-errors that need to be manually fixed.
_(note: this will modify your local files, so reccomended to commit changes first -> run script -> commit changes from running script)_
_(note: running 'ruff --line-length 120' will lint the code without auto-fixing)_


You can run all the tests with the following:
```
pytest .
```
_(note: this works from either the project root-dir and also the /tests dir)_


You can run an individual test-file by specifying the path:
```
pytest tests/test_SuiteScripts.py
```

And run an individual test-case within the test-file by using '::':
```
pytest tests/test_SuiteScripts.py::test_Noise
```

These tests verify that the code in _/calibrationSuite_ and _/suite\_scripts_ is currently working as expected.

_test\_SuiteScripts.py_ runs the files in _/suite\_script_ and diffs their real output against expected output in _/tests/test\_data_

_/tests/test\_data_ stores data from this repo: <https://github.com/slaclab/beamtime-calibration-suite-test-data>
The repo is added as a [git submodule](https://gist.github.com/gitaarik/8735255), and will get setup by the _setup_developers.sh_ script.
Since the test data is large, [LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) is used and needs to be installed. (LFS is installed already on _S3DF_)

If you wish to run the tests without them diffing the output files against the golden data (and want to just test that the code runs to completion without crash/error), you can just remove the entire /tests/test_data dir manually and the tests will not attempt to diff. If you wish to redownload the /test_data dir, run `source setup_developers.sh` again.

Some more info on testing, such as adding now data to the _test\_data_ submodule or adding a new suite_script test, can be found in [test_SuiteScripts.py.](https://github.com/slaclab/beamtime-calibration-suite/blob/development/tests/test_SuiteScripts.py)
