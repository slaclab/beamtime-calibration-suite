from psana import DataSource
import os
import numpy as np

os.environ["PS_SMD_N_EVENTS"] = "50"
os.environ["PS_SRV_NODES"] = "1"

ds = DataSource(exp="rixc00121", run=32, intg_det="epixhr")
smd = ds.smalldata(filename="ts.h5")
myrun = next(ds.runs())
epix = myrun.Detector("epixhr")
timeObj = myrun.Detector("timing")
nevt = 0
nBeam = 0
for nevt, evt in enumerate(myrun.events()):
    if evt is None:
        continue
    ec = timeObj.raw.eventcodes(evt)
    if not ec[281]:
        continue
    nBeam += 1

    frames = epix.raw.raw(evt)
    if frames is None:
        continue
    smd.event(evt, ts=evt.datetime().timestamp(), nBeam=nBeam, nevt=nevt)

##if smd.summary:
##    smd.save_summary(step_av) # this method accepts either a dictionary or kwargs
smd.done()

import matplotlib.pyplot as plt
import h5py

a = h5py.File("ts.h5")
mona_ts = a["timestamp"][()]
ts = a["ts"][()]
print(False in (ts == mona_ts))
counter = np.arange(10000)
##plt.plot(counter[:400], ts[:400])
##plt.xlabel("entry")
##plt.ylabel("timestamp")
##plt.show()


nBeam = a["nBeam"][()]
print("nBeam max:", nBeam.max())
nevt = a["nevt"][()]
print("nevt max:", nevt.max())
