# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

# Docs: https://slaclab.github.io/beamtime-calibration-suite/

# Step-by-step to get running quick!
* First, follow steps **1** through **7**: [Github and Git Setup](https://slaclab.github.io/beamtime-calibration-suite/setup/)
* Next, run the following commands in a terminal (linux or mac terminal should work):  
&emsp;-_(note: lines starting with '#' are comments with explanation and don't need to be ran)_  
&emsp;-_(note: in the 1st command: replace \<slac-username> with your slac linux-username)_
```
# ssh into the s3df machines
ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu
ssh psana

# do setup for s3df environment
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh

# download the code
mkdir repos && cd repos
git clone git@github.com:slaclab/beamtime-calibration-suite.git
cd beamtime-calibration-suite
git fetch
git switch development

# do more environment setup for suite-scripts
source setup.sh

# run an example script
cd suite_scripts
python EventScanParallel.py -r 457
```
If everything is working, the script should start spitting terminal-output like:
```
...
3259 True
3257 True
3256 True
3260 True
Event number foo
```
 
## Developers:

If you are new to git/github, start [here](https://slaclab.github.io/beamtime-calibration-suite/learning_git/)

An overview of the development process is found [here](https://slaclab.github.io/beamtime-calibration-suite/workflow/)

For commit messages, we can try to follow the PyDM guidelines: https://slaclab.github.io/pydm/development/development.html#commit-guidelines