# Git/GitHub Workflow

We should try to generally follow the branching and pull-request workflow described in this SLAC [presentation](https://docs.google.com/presentation/d/1AXcH17xDfum4mZsdV5lfjn_mvSMp2ye796xrVuSM3w8/edit#slide=id.gf4dca9affc_0_7)
  * in our case the two important branches will be `main` and `development`
  * in-between beamtimes, `development` is used for pushing work
  * right before beamtimes, `development` is merged into `main`
  * then a branch named `beamtime_<month>_<day>_<year>_` is branched off main
    * this branch is used for sharing code fixes/changes (pushing-to and pulling-from) during beamtime
  * after beamtimes, we merge `beamtime_<month>_<day>_<year>` back into `main` and tag it

### Before Beamtime:
* checkout `development` (or a earlier stable point of `development`)
* use a pull request to merge `development`  into `main`
  * to do this follow the instructions in section **F)** of the doc page [Git Commands for Common Tasks](https://slaclab.github.io/beamtime-calibration-suite/commands/)
* make a branch for work during this specific beamtime
```
git checkout -b main beamtime_<month>_<day>_<year>
git push origin beamtime_<month>_<day>_<year>
```
* Now run the tests with the following cmd:
_(assuming the tests have been setup already with setup_developers.sh)_
```
pytest .
```
* Then see that all tests are passing (unless there are any expected failures)
* If any new test-less scripts are planned to be used (or have too many expected test-failures), manually run any scripts we plan to use to verify they still work

### During Beamtime:
* at start of beamtime, everyone needs to download the branch for this beamtime:
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
* make sure all the changes that need to be saved are commited to `beamtime_<month>_<day>_<year>`
* use a pull request to merge `beamtime_<month>_<day>_<year>` into `main`
* add a tag for the beamtime, named with date of beamtime: `v<month>.<day>.<year>`
* _(if beamtime is multiple days, use the 1st day's date)_

```
git tag <tag_name> -a //an example tag number would be 1.0.3
# this will open your editor to write a description
# the description should be 'Beamtime <Month> <Day> <Year>'

# push tag <tag_name>
git push origin <tag_name>
```

* lastly, use a pull request to merge _main_ into `development`
  * this is kinda sloppy, but seems like easy enough 'reset' things after beamtime
