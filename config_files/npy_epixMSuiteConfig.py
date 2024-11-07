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
for i in [0]:  ##range(0, 3):
    singlePixelArray.append([0, 66, 66])
    singlePixelArray.append([0, 6, 6])
    singlePixelArray.append([0, 55, 200])
    singlePixelArray.append([0, 120, 200])
    singlePixelArray.append([0, 55, 300])
    singlePixelArray.append([0, 120, 300])

experimentHash = {
    "detectorType": "epixm",
    "detectorVersion": 1,  ## new firmware
    "exp": "rixx1005922",
    "location": "RixEndstation",
    "location": "ascLab",
    "analyzedModules": [0],
    "seedCut": 40,  ## pure guess
    "neighborCut": 10,  ##pure guess
    ##"fluxSource": "MfxDg1BmMon",
    # "fluxSource": "MfxDg2BmMon",
    "fluxChannels": [15],  ## or 11 if we see saturation
    # "fluxSign": 1,  ## for dg2
    "fluxSign": -1,
    "singlePixels": singlePixelArray,
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # 'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    # 'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    "ROIs": ["../data/square9_0_epixM_roi.npy", "../data/square9_1_epixM_roi.npy"],
    "regionSlice": np.s_[0:1, 0:192:, 0:384],  ## small region near Kaz rec
}
