# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

# Docs: https://slaclab.github.io/beamtime-calibration-suite/

# Step-by-step to get running quick!
* First, follow steps **1** through **7**: [Github and Git Setup](https://slaclab.github.io/beamtime-calibration-suite/setup/)
* Next, run the following commands in a terminal (linux or mac terminal should work):  
&emsp;-_(note: lines starting with '//' are comments with explanation and don't need to be ran)_  
```
// ssh into the s3df machines
ssh -Yt <slac-linux-username>@s3dflogin.slac.stanford.edu
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
cd suite_scripts
mkdir setup_test_output

// run an example script
OUTPUT_ROOT=. python EventScanParallelSlice.py -r 102 --maxNevents 500 -p /setup_test_output
//let the script run to completion...

// now check the example ran correctly
ls setup_test_output
//if things are working correctly, you should see these non-empty files:
eventNumbers_c0_r102_rixx1005922.npy  EventScanParallel_c0_r102__n666.h5
means_c0_r102_rixx1005922.npy
```
 
## Developers:

If you are new to git/github, start with [Learning Git](https://slaclab.github.io/beamtime-calibration-suite/learning_git/)

An overview of the development process is found [here](https://slaclab.github.io/beamtime-calibration-suite/workflow/)

For commit messages, we can try to follow the PyDM guidelines: https://slaclab.github.io/pydm/development/development.html#commit-guidelines
