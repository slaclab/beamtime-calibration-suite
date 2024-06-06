##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from psana import *
import sys
import numpy as np

exp = sys.argv[1]
run = eval(sys.argv[2])
try:
    special = sys.argv[3]
except Exception:
    special = ""

ds = DataSource(exp=exp, run=run, intg_det="epixhr")

myrun = next(ds.runs())
det = myrun.Detector("epixhr")
try:
    digIn = myrun.Detector("ePixHR_Dig_in")
    anaIn = myrun.Detector("ePixHR_Ana_in")
except Exception:
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
    except Exception:
        pass

    try:
        pedestals = det.calibconst["pedestals"][0]
        lowPed = pedestals[2]
        print("pedestal:", pedestals)
        print("pedestal mean, std")
        print(lowPed.mean(), lowPed.std())
        if "pedestal" in special:
            np.save("pedestals_%d.npy" % (run), pedestals)

    except Exception:
        print("no pedestal")

    try:
        gains = det.calibconst["pixel_gain"][0]
        print(gains.mean(axis=(1, 2, 3)))
    except Exception:
        print("no gain: pain")
    try:
        print("dig:", digIn(evt))
        print("ana:", anaIn(evt))
    except Exception:
        print("no PV")

    break
