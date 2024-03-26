##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import numpy as np
import copy

a = np.load("roiFromSwitched_e550_rmfxx1005021.npy")
b = copy.copy(a) * 0
b[0, 150:250, 150:250] = 1
c = np.bitwise_and(a, b)
np.save("maskedRoiFromSwitched_e550_rmfxx1005021.npy", c)
