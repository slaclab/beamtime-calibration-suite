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

# experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation', 'fluxSource':'MFX-USR-DIO', 'fluxChannels':[11], 'fluxSign':-1}
# experimentHash = {'exp':'rixc00121', 'location':'RixEndstation',
singlePixelArray = []
for i in range(16):
    singlePixelArray.append([i, 10, 10])
    singlePixelArray.append([i, 10, 100])
    singlePixelArray.append([i, 100, 10])
    singlePixelArray.append([i, 100, 100])
    singlePixelArray.append([i, 150, 150])
    singlePixelArray.append([i, 80, 20])

experimentHash = {
    ##"detectorType": "Epix10kaQuad",## this needs work
    "detectorType": "Epix10ka",
    "exp": "mfxx1013123",
    # "exp": "rixx1003721",
    "location": "MfxEndstation",
    "ignoreEventCodeCheck": True,
    ## might add camera:0 or whatever here...
    "analyzedModules": [15],
    "seedCut": 40,  ## pure guess
    "neighborCut": 10,  ##pure guess
    # "fluxSource": "MfxDg1BmMon",
    ##"fluxSource": "MfxDg2BmMon",
    ##"fluxChannels": [15],
    ##"fluxSign": 1,  ## for dg2
    # "fluxSign": -1,
    "singlePixels": singlePixelArray,
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # 'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    # 'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    # ],
    ##"regionSlice": np.s_[0:1, 0:704:, 0:768]
    "regionSlice": np.s_[15:16, 0:352:, 0:384],
}
