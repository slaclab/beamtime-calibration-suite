# beamtime-calibration-suite
[![Build Status](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/slaclab/beamtime-calibration-suite/actions/workflows/run-tests.yml)

# Docs: https://slaclab.github.io/beamtime-calibration-suite/

# Step-by-step to get running quick!
* First, follow steps **1** through **4**: [setup git and github](https://slaclab.github.io/beamtime-calibration-suite/setup/)
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
_Done with step-by-step setup. The following sections provide more detail on the setup process and the code._
 
## Developers:

If you are new to git/github, start here: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=428802060)

Then read the following for an overview of the development process: [https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464](https://confluence.slac.stanford.edu/pages/viewpage.action?pageId=429562464)

For commit messages, we can try to follow the PyDM guidelines: https://slaclab.github.io/pydm/development/development.html#commit-guidelines