# Git Commands for Common Tasks

**A)** Getting the latest changes for use at a beamtime
```
git fetch
//if beamtime is across multiple days, use 1st day date
git switch beamtime_<month>_<day>_<year>
```

**B)** Getting the latest changes from the _development_ branch
```
git pull origin development
```
    
**C)** Saving a new feature/script/bugfix/etc:
* make sure you have the latest changes from the remote:
```
git pull origin development
```
* make a branch for your feature off of the _development_ branch:
```
git checkout -b <feature_branch_name> development
```
* modify and commit the code, which will probably involve usage of the following commands:
```
git status
git add <filename>
git commit -m <commit-message>
```
* push your feature branch to remote
```
git push origin <feature_branch_name>
```
* if want to merge your changes into the _development_ branch (and keep them long-term)
  * follow **F)** and make a pull-request from your feature-branch into _development_

**D)** If pulling down someone else's branch (non main/development branch):
* get updated branch info from remote
```
git fetch origin
```
* see list of remote branches (optional)
```
git branch -r
```
* checkout their branch (use the branch name without the 'oriogin/' prefix)
```
git checkout <other_person_branch_name>
```

**E)** Switching between two branches:
* if the following command lists two branches:
```
git branch
```
* you can switch between them with:
```
git checkout <branch_want_to_switch_to>
```

**F)** Making pull request (one branch has been pushed to the remote):
* go to: https://github.com/slaclab/beamtime-calibration-suite/pulls  
* click green 'New pull request' button in upper right  
* you will see two grey boxes containing branch names and an arrow pointing from one box to the other  
  * the "compare:..." box is the branch that will get merged into the "base:..." box's branch  
  * the base should be the branch named _development_  
* once the grey boxes are set correctly, click the green 'Create pull request' button  
* once branch is ready to merge, you can click the ''Merge pull request' button to merge the commit  
  * being ready means: potentially reviewed (if big change), passing any automated checks/tests, etc  
* if github is not allowing the merge automatically, you will need to merge or rebase locally and manually handle the conflicts  

**G)** Check out tagged commit (old beamtime code is tagged):

* same syntax as checking-out a branch, but use tag name instead:
```
git checkout <tag_name>
//ex: 'git checkout v1.0.0'
```