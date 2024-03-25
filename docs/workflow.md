# Git/GitHub Workflow

We should try to generally follow the branching and pull-request workflow described in this [presentation](https://docs.google.com/presentation/d/1AXcH17xDfum4mZsdV5lfjn_mvSMp2ye796xrVuSM3w8/edit#slide=id.gf4dca9affc_0_7).
* in our case the two important branches will be _main_ and _development_
* in-between beamtimes, _development_ is used for pushing work 
* right before beamtimes, _development_ is merged into _main_ 
* then a branch named _beamtime\_\<month\>\_\<day\>\_\<year\>_ is branched off main
  * this branch is used for sharing code fixes/changes (pushing-to and pulling-from) during beamtime
* after beamtimes, we merge _beamtime\_\<month\>\_\<day\>\_\<year\>_ back into _main_ and tag it

(img: https://www.pablogonzalez.io/salesforce-git-branching-strategies/)

### Before Beamtime:
* checkout _development_ (or a earlier stable point of _development_) 
* manually run and check the output of script planned for use on the beamtime, as a final sanity check
* use a pull request to merge _development_  into _main_
  * to do this follow the instructions in section **F)** of [https://slaclab.github.io/beamtime-calibration-suite/commands/](https://slaclab.github.io/beamtime-calibration-suite/commands/)
  * _main_ is safeguarded and will require a +1 from another developer
* make a branch for work during this specific beamtime
```
git checkout -b main beamtime_<month>_<day>_<year>
git push origin beamtime_<month>_<day>_<year>
```

### During Beamtime:
* At start of beamtime, everyone needs to download the branch for this beamtime:
```
git fetch
git switch beamtime_<month>_<day>_<year>
```

* If you need to make changes to the code, first make sure your files are up to date:
```
git pull
```
* Now make your changes and upload them:
```
git add -u
git commit -m "<description of changes made>"
git push origin beamtime_<month>_<day>_<year>
```

* If someone else made and upload changes, you can download them by doing:
```
git pull
```

### After Beamtime:
* make sure all the changes that need to be saved are commited to _beamtime\_\<month\>\_\<day\>\_\<year\>_ 
* use a pull request to merge _beamtime\_\<month\>\_\<day\>\_\<year\>_  into _main_
* add a tag for the beamtime
```
//tag number is arbitrary at this point, just look at last tag and increment one of the values
git tag v<tag number> -a //an example tag number would be 1.0.3
//this will open your editor to write a description
//the description should be 'Beamtime <Month> <Day> <Year>'
//(if beamtime is multiple days, use the 1st day's date)
```
* use a pull request to merge _main_ into _development_
  * this is kinda sloppy, but seems like easiest way to 'reset' things after beamtime