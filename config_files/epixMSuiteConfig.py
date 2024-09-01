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
for i in [0, 2, 3]:##range(0, 3):
    singlePixelArray.append([i, 55, 10])
    singlePixelArray.append([i, 120, 10])
    singlePixelArray.append([i, 55, 200])
    singlePixelArray.append([i, 120, 200])
    singlePixelArray.append([i, 55, 300])
    singlePixelArray.append([i, 120, 300])

experimentHash = {
    "detectorType": "epixm",
    "detectorVersion":1,## new firmware
    "exp": "rixx1005922",
    "location": "RixEndstation",
    "analyzedModules": [0, 2, 3],
    "seedCut": 40,  ## pure guess
    "neighborCut": 10,  ##pure guess
    "fluxSource": "MfxDg1BmMon",
    #"fluxSource": "MfxDg2BmMon",
    "fluxChannels": [15],## or 11 if we see saturation
    #"fluxSign": 1,  ## for dg2
    "fluxSign": -1,
    "singlePixels": singlePixelArray,
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # 'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    # 'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    "ROIs": [
        "../data/cometPinhole.npy",
        "../data/smallRegionFourAsics.npy",
        "../data/smallRegionTwoAsicsForBhavna.npy",
    ],
    "regionSlice": np.s_[0:4, 0:192:, 0:384],  ## small region near Kaz rec
}
