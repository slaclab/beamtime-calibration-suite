##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from psana import DataSource
from psmon import publish
from cfg_utils import *

import sys

expt = sys.argv[1]
run = eval(sys.argv[2])

ds = DataSource(exp="%s" % (expt), run=run)
myrun = next(ds.runs())
det = myrun.Detector("epixhr")
det = myrun.Detector("epixm")



publish.local = True
publish.plot_opts.aspect = 1

print(ds)

tim = myrun.Detector("timing")
try:
    scan = myrun.Detector("scan")
    print(vars(scan))
except Exception:
    pass


def dump1(arr, title, nx, start):
    print(f"{title} [{nx}]")
    s = ""
    for i in range(start, start + nx):
        s += " {:04x}".format(arr[i])
        if i % 16 == 15:
            s += "\n"
    print(s)
    return start + nx


def dump2(arr):
    for i in range(arr.shape[0]):
        s = ""
        for j in range(arr.shape[1]):
            s += " {:04x}".format(arr[i][j])
            if j % 16 == 15:
                s += "\n"
        print(s)


ppid = 0
detName = "epixhr"

for nstep, step in enumerate(myrun.steps()):
    for nevt, evt in enumerate(step.events()):
        if nevt == 0:
            print(f"step {nstep}")
            dump_det_config(det, detName)
            dump_det_config(det, detName + "hw")
