# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

# Docs: https://slaclab.github.io/beamtime-calibration-suite/

# Step-by-step to get running quick!
* First, follow steps **1** through **7**: [Github and Git Setup](https://slaclab.github.io/beamtime-calibration-suite/setup/)
* Next, run the following commands in a terminal (linux or mac terminal should work):  
&emsp;-_(note: lines starting with '//' are comments with explanation and don't need to be ran)_  
&emsp;-_(note: in the 1st command: replace \<slac-username> with your slac linux-username)_  
```
// ssh into the s3df machines
ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu
ssh psana

// do setup for s3df environment
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

// download the code
mkdir repos && cd repos
git clone git@github.com:slaclab/beamtime-calibration-suite.git
cd beamtime-calibration-suite

// do more environment setup for suite-scripts
source setup.sh

// setup for running an example script
mkdir setup_test_output
cd suite_scripts

// run an example script
OUTPUT_ROOT= python EventScanParallelSlice.py -r 457 -p ../setup_test_output
//let the script run to completion...

// now check the example ran correctly
ls ../setup_test_output
//if things are working correctly, you should see these non-empty files:
eventNumbers_c0_r457_rixx1003721.npy  means_c0_r457_rixx1003721.npy
EventScanParallel_c0_r457_n1.h5
```
 
## Developers:

If you are new to git/github, start with [Learning Git](https://slaclab.github.io/beamtime-calibration-suite/learning_git/)

An overview of the development process is found [here](https://slaclab.github.io/beamtime-calibration-suite/workflow/)

For commit messages, we can try to follow the PyDM guidelines: https://slaclab.github.io/pydm/development/development.html#commit-guidelines
