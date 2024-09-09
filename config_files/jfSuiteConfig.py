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
for i in [3]:  ##range(0, 8):
    singlePixelArray.append([i, 10, 10])
    singlePixelArray.append([i, 10, 100])
    singlePixelArray.append([i, 100, 10])
    singlePixelArray.append([i, 100, 100])
    singlePixelArray.append([i, 150, 150])
    singlePixelArray.append([i, 80, 20])

singlePixelArray.append([2, 178, 367])

experimentHash = {
    "detectorType": "Jungfrau",
    "exp": "cxic00121",
    "location": "CxiDs1",
    "ignoreEventCodeCheck": True,
    "analyzedModules": [0],  ##range(0:8),
    "seedCut": 100,  ## pure guess
    "neighborCut": 20,  ##pure guess
    # "fluxSource": "MfxDg1BmMon",
    ##"fluxSource": "MfxDg2BmMon",
    ##"fluxChannels": [15],
    ##"fluxSign": 1,  ## for dg2
    # "fluxSign": -1,
    "singlePixels": singlePixelArray,
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    # ],
    ##"regionSlice": np.s_[0:8, 0:512:, 0:1024]  ## whole camera
    ##"regionSlice": np.s_[0:1, 0:512:, 0:1024]
    "regionSlice": np.s_[0:1, 0:129:, 0:129],
}
