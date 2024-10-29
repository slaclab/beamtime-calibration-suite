import sys

from psana import *  # noqa: F403

##N.b. - this is psana2

exp = "rixc00122"
run = eval(sys.argv[1])
ds = DataSource(exp=exp, run=run, intg_det="archon", max_events=666666)  # noqa: F405

smd = ds.smalldata(filename="foo.h5")
##print(help(smd.event))

myrun = next(ds.runs())
det = myrun.Detector("archon")

nGood = 0
nBad = 0
for nevt, evt in enumerate(myrun.events()):
    ##print(dir(evt))
    ##print(help(evt))
    if det.raw.raw(evt) is None:
        if nBad < 3:
            print("event %d is None" % (nevt))
        nBad += 1
    else:
        if nGood < 3:
            print("good event")
        nGood += 1


print("good vs evil:", nGood, nBad)
