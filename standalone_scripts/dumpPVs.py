from psana import *
import sys
import numpy as np

exp = sys.argv[1]
run = eval(sys.argv[2])
pvList = sys.argv[3].split(",")
allNames = pvList.join("_")

detList = [DataSource(exp=exp, run=run, intg_det=pv) for pv in pvList]
data = [[]] * len(pvList)
myrun = next(ds.runs())
while True:
    evt = next(myrun.events())
    if evt is None:
        break
    for n, ds in enumerate(dsList):
        data[n].append(det(evt))

np.save("%s_r%d_PVs_%s.npy" % (exp, run, allNames), np.array(data))
