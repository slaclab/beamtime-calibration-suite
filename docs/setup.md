# Github and Git Setup

these steps will get you setup for running and developing the calibration suite

## 1: Make a github.com account

* if you already have github account and want to use it, skip to step **2)**
* else to make a new account follow the steps here: [https://github.com/join](https://github.com/join)
* your username can be anything, some people at slac use _<username>-slac_ convention (ex: _nstelter-slac_)
* for email you can use your _@slac.stanford.edu_ address or any other address if you want (just make sure to use the same email in step **4)**
* you will need a code from your email for verification when creating the account

## 2: Register github account with ‘SLAC Lab’ github group

* first join ‘#comp-general’ channel on Slack
* when viewing this slack channel, should see ‘Pinned’ and next to it ‘Workflows’ at top of the page
* click ‘Workflows’ -> ‘SLAC GitHub Access’, and fill out the form with your info
* wait to receive an email asking you to join the ‘SLAC Lab’ group, and follow instructions in this email

## 3: Request write permissions for the repository

*  after completing step **2)**, your github account should be a member of the 'SLAC Lab' github group
*  now go to [https://github.com/orgs/slaclab/teams/beamtime_calibration_suite_devs](https://github.com/orgs/slaclab/teams/beamtime_calibration_suite_devs) and click the 'Request to join' button towards the upper-right of the page
*  this will grant you write access to the repository (used for development and sharing code-changes during beamtime)

## 4: Setup terminal for next steps

* For the following steps **5)**, **6)**, **7)**: make sure you terminal (linux or mac) is setup first with the following commands:
* (note: in the 1st command: replace \<slac-username\> with your slac unix account-name)
    ``` 
    ssh -Yt <slac-username>@s3dflogin.slac.stanford.edu
    source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh
    ```

## 5: Config local git settings

* Enter the following terminal commands:
``` 
git config --global user.name <github username>
git config --global user.email <email used to setup github account>
#run one of the following cmds, depending on your preferred editor 
#(editor is used for editing files during some git operations)
git config --global core.editor vim
git config --global core.editor emacs
```

## 6: Setup SSH Keys for github on s3df

* First make sure you are logged into github account in browser
* Follow instructions under “Generating a new SSH key” and “Adding your SSH key to the ssh-agent”: [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) _(make sure you have selected the 'Linux' tab near the top of the page, not 'Mac')_
* Follow instructions under “Adding a new SSH key to your account”: [https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account) _(make sure you have selected the 'Linux' tab near the top of the page, not 'Mac')_

## 5: Download repo

* cd to where you want the scripts to live (the scripts will be downloaded inside of a folder called ‘beamtime-calibration-suite’)
  * I suggest inside your home directory (_\~_), or inside a new folder you make like _~/repos/_
* to download the repository, run the following command: 
```
git clone git@github.com:slaclab/beamtime-calibration-suite.git
```
  * if an error occurs, SSH setup in step **6)** may have had an issue and needs to be debugged
* if command was successful, you should be able to cd into newly created ‘beamtime-calibration-suite’ folder and see subfolders containing python code
* now get the 'development' branch by running command (this will you get the most up-to-date code when it's not during a beamtime): 
```
git checkout development
```