##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import matplotlib.pyplot as plt
import numpy as np
import sys

dataFile = sys.argv[1]
row = eval(sys.argv[2])
col = eval(sys.argv[3])

a = np.load(dataFile)
plt.plot(np.arange(a.shape[0]), a[:, row, col], ".", ms=1)
plt.xlabel("event")
plt.ylabel("Raw")
title = "pixel %d,%d in %s" % (row, col, dataFile)
plt.title(title)
plt.savefig(title.replace(" ", "_") + ".png")
