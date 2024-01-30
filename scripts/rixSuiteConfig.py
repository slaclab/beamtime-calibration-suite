import os

# this probably in file where it's actually used
if os.getenv("foo") == "1":
    print("psana1")
    from psana1Base import *  # noqa: F403
else:
    print("psana2")
    from psana2Base import *  # noqa: F403

import numpy as np

##experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation',\\
## 'fluxSource':'MFX-USR-DIO', 'fluxChannels':[11], 'fluxSign':-1}
##experimentHash = {'exp':'rixc00121', 'location':'RixEndstation',
experimentHash = {
    "exp": "rixx1003721",
    "location": "RixEndstation",
    "fluxSource": "MfxDg1BmMon",
    ##                  'fluxChannels':[9, 10, 11, 12],
    "fluxChannels": [11],
    ##                  'fluxChannels':[8, 14],
    "fluxSign": -1,
    "singlePixels": [
        [0, 150, 10],
        [0, 150, 100],
        [0, 275, 100],
        [0, 272, 66],
        [0, 280, 70],
        [0, 282, 90],
        [0, 270, 90],
        [0, 271, 90],
        [0, 272, 90],
        [0, 273, 90],
    ],
    #                  'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    #                  'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    ##                  'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    "ROIs": ["XavierV4_2", "OffXavierV4_2"],
    "regionSlice": np.s_[270:288, 59:107],
}
##more complex approach allowing run ranges
##fluxHash = {1:['MFX-USR-DIO', 11]}
