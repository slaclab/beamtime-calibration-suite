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

singlePixelArray = []
for i in range(1, 3):
    singlePixelArray.append([i, 10, 10])
    singlePixelArray.append([i, 10, 100])
    singlePixelArray.append([i, 100, 10])
    singlePixelArray.append([i, 100, 100])
    singlePixelArray.append([i, 150, 150])
    singlePixelArray.append([i, 80, 20])

singlePixelArray.append([2, 178, 367])

experimentHash = {
    "detectorType": "epixm",
    "exp": "rixx1005922",
    "location": "RixEndstation",
    "analyzedModules": [1, 2],
    "seedCut": 40,
    "neighborCut": 10,
    "fluxSource": "MfxDg2BmMon",
    "fluxChannels": [15],
    "fluxSign": 1,
    "singlePixels": singlePixelArray,
    "ROIs": [
        "../data/cometPinhole.npy",
        "../data/smallRegionFourAsics.npy",
        "../data/smallRegionTwoAsicsForBhavna.npy",
    ],
    "regionSlice": np.s_[0:4, 0:192:, 0:384],  ## small region near Kaz rec
}
