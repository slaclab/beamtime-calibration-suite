from psana import *
import sys
import numpy as np

exp = sys.argv[1]
run = eval(sys.argv[2])
try:
    special = sys.argv[3]
except:
    special = ""

ds = DataSource(exp=exp, run=run, intg_det="epixhr")

myrun = next(ds.runs())
det = myrun.Detector("epixhr")
try:
    digIn = myrun.Detector("ePixHR_Dig_in")
    anaIn = myrun.Detector("ePixHR_Ana_in")
except:
    digIn = anaIn = None

while True:
    evt = next(myrun.events())
    if evt is None:
        continue
    raw = det.raw.raw(evt)
    if raw is None:
        continue
    cal = det.raw.calib(evt)
    status = det.raw._status()
    print("raw:", raw)
    print("cal:", cal)
    print("status:", status)
    print("Max, min cal:", cal.max(), cal.min())
    try:
        print("Max, min status:", status.max(), status.min())
    except:
        pass

    try:
        pedestals = det.calibconst["pedestals"][0]
        lowPed = pedestals[2]
        print("pedestal:", pedestals)
        print("pedestal mean, std")
        print(lowPed.mean(), lowPed.std())
        if "pedestal" in special:
            np.save("pedestals_%d.npy" % (run), pedestals)

    except:
        print("no pedestal")

    try:
        gains = det.calibconst["pixel_gain"][0]
        print(gains.mean(axis=(1, 2, 3)))
    except:
        print("no gain: pain")
    try:
        print("dig:", digIn(evt))
        print("ana:", anaIn(evt))
    except:
        print("no PV")

    break
