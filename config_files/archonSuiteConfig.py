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

##experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation', 'fluxSource':'MFX-USR-DIO', 'fluxChannels':[11], 'fluxSign':-1}
# experimentHash = {'exp':'rixc00121', 'location':'RixEndstation',
experimentHash = {
    "detectorType": "archon",
    "detectorSubtype": "2d",
    ##"detectorSubtype": "1d",
    "exp": "rixx1017523",
    "location": "RixEndstation",
    "seedCut": 30,  ##from old scripts
    # "fluxSource": "MfxDg1BmMon",
    # 'fluxChannels':[9, 10, 11, 12],
    # "fluxChannels": [15],
    # 'fluxChannels':[8, 14],
    # "fluxSign": -1,
    "singlePixels": [
        [0, 10],
        [0, 100],
        [0, 1000],
        [0, 2000]
    ],
    "ignoreEventCodeCheck": True,
    "analyzedModules": [0],
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # 'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    # 'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    ##"regionSlice": np.s_[0:1, 0:1, 0:4800],  ##[1d]
    "regionSlice": np.s_[0:1, 0:600, 0:4800],  ##[2d with ROI....]
}
# more complex approach allowing run ranges
# fluxHash = {1:['MFX-USR-DIO', 11]}
if experimentHash['detectorSubtype'] == "2d":
    experimentHash['singlePixels'] += [[100, 100],
                                       [200, 200],
                                       [300, 300],
                                       [400, 400],
                                       [500, 500]]
