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
