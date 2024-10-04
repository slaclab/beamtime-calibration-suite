# Github and Git Setup

These steps will get you setup for running and developing the calibration suite!

These steps describe the setup for running on the [SLAC Shared Scientific Data Facility (S3DF)](https://s3df.slac.stanford.edu/public/doc/#/) A S3DF account is needed before following these steps, and info on how to get one is [here](https://s3df.slac.stanford.edu/public/doc/#/accounts-and-access)

The only other prerequisites should be a terminal that can run Unix commands (mac and linux have this by default), and basic knowledge of using this terminal

## 1: Make a github.com account

* if you already have github account and want to use it, skip to step **2)**
* else to make a new account following the steps here: [https://github.com/join](https://github.com/join)
* your username can be anything, some people like to use the `<username>-slac` convention (ex: _nstelter-slac_)
* for the email you can use your _@slac.stanford.edu_ address or any other address if you want (just make sure to use the same email in step **5)**
* you will need a code from your email when creating the account

## 2: Register your github account with ‘SLAC Lab’ github group

* first join ‘#comp-general’ channel on Slack
* now when viewing this slack channel you should see ‘Pinned’ and next to it ‘Workflows’ at top of the page
* click ‘Workflows’ -> ‘SLAC GitHub Access’, and fill out the form with your info
* wait to receive an email asking you to join the ‘SLAC Lab’ group, and follow instructions in this email

## 3: Request write permissions for the repository

* after completing step **2)**, your github account should now be a member of the 'SLAC Lab' github group
*  now go to [https://github.com/orgs/slaclab/teams/beamtime_calibration_suite_devs](https://github.com/orgs/slaclab/teams/beamtime_calibration_suite_devs) and click the 'Request to join' button towards the upper-right of the page
*  this will grant you write access to the repository (used for development and sharing code-changes during beamtime)

## 4: Setup your terminal for next steps

* for the following steps **5)**, **6)**, **7)**, **8)**, make sure you terminal is setup first with the following commands:  
(note: in the 1st command replace `<slac-username>` with your slac unix account-name)  
``` 
ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu
# now enter your info to login to s3df...
ssh psana // to access data on s3df
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh
```
* all commands entered in the following steps should be done so in this setup terminal _(the terminal should now have an active ssh session into S3DF)_

## 5: Config your local git settings

* Run the following terminal commands:
``` 
git config --global user.name <github username>
git config --global user.email <email used to setup github account>
# run one of the following cmds, depending on your preferred editor 
# (the editor is used during some git operations)
git config --global core.editor vim
git config --global core.editor emacs
```

## 6: Setup SSH Keys for github on s3df

* first make sure you are logged into your github account in your web browser
* for the next two bullet-points, make sure you have selected the 'Linux' tab near the top of the page, not 'Mac'!
  * note: the commands on the following pages have to be ran in the terminal setup in step **4)**, which is ssh'd into S3DF
* Follow instructions under “Generating a new SSH key” and “Adding your SSH key to the ssh-agent”: [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) 
* Follow instructions under “Adding a new SSH key to your account”: [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account)
* To check if this worked, run:
```
ssh -T git@github.com
# if SSH is working, you should get the following output:
# 'Hi <github_username>! You've successfully authenticated, but GitHub does not provide shell access.'
```

## 7: Download the repo

* run the following terminal commands:
```
cd ~
mkdir repos
cd repos
git clone git@github.com:slaclab/beamtime-calibration-suite.git
# wait for download to finish...
cd beamtime-calibration-suite
git switch development
ls
# should see a bunch of folders
cd suite_scripts
ls
# now should see a bunch of python scripts
```
* if an error occurs with these commands, SSH setup in step **6)** may have had an issue and might need to be debugged


## 8: Run an example script

* run the following terminal commands:
```
cd ~/repos/beamtime_calibtation_suite
source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh
source setup.sh // must be run in each new terminal session (or added to ~/bashric)
cd suite_scripts
mkdir setup_test_output
# OUTPUT_ROOT=. makes the script to look relative to the current directory for the output-folder
OUTPUT_ROOT=. python EventScanParallelSlice.py -r 102 --maxNevents 500 -p /setup_test_output
# let the script run to completion...
ls -lt setup_test_output
# if ran correctly, should see some non-empty files in the output dir:
eventNumbers_c0_r102_rixx1005922.npy  EventScanParallel_c0_r102__n666.h5  means_c0_r102_rixx1005922.npy
```

## 9: Run the tests (optional, mainly for use during development):
* run the following terminal commands:
```
cd ~/repos/beamtime_calibtation_suite
# setup the test dependencies and test_data submodule
source setup_developers.sh
pytest .
```
