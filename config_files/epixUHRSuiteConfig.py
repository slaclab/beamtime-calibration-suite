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
##for i in [0, 2, 3]:##range(0, 3):
## for 41-c00-01
m = 0
for r in range(11, 60):
    for c in range(49):
        if r%12 == 0 and c%6 == 0:
            singlePixelArray.append([m, r, c])
singlePixelArray.append([m, 12*7, 60])
singlePixelArray.append([m, 13*7, 60+12])
singlePixelArray.append([m, 14*7, 60+24])

m = 3
for r in range(8, 57):
    for c in range(10, 59):
        if r%12 == 0 and c%6 == 0:
            singlePixelArray.append([m, r, c])
singlePixelArray.append([m, 12*7, 60])
singlePixelArray.append([m, 13*7, 60+12])
singlePixelArray.append([m, 14*7, 60+24])


experimentHash = {
    "detectorType": "epixuhr",
    ##"detectorVersion": 1,  ## new firmware
    "exp": "rixx1005922",
    "location": "RixEndstation",
    "analyzedModules": [0, 3],
    "seedCut": 40,  ## pure guess
    "neighborCut": 10,  ##pure guess
    "fluxSource": "MfxDg1BmMon",
    # "fluxSource": "MfxDg2BmMon",
    "fluxChannels": [11],  ## 8 Nov
    # "fluxSign": 1,  ## for dg2
    "fluxSign": -1,
    "singlePixels": singlePixelArray,
    # 'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
    # 'ROIs':['roiFromSwitched_e557_rmfxx1005021']
    # 'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
    # "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
    "ROIs": [
        "../data/epixUHR_asic0_sensor_fullRoi.npy",
        "../data/epixUHR_asic0_sensor_pietroPixelRoi.npy",
        "../data/epixUHR_asic0_offSensor_fullRoi.npy",
        "../data/epixUHR_asic3_sensor_fullRoi.npy",
        "../data/epixUHR_asic3_sensor_pietroPixelRoi.npy",
        "../data/epixUHR_asic3_offSensor_fullRoi.npy",
    ],
    "regionSlice": np.s_[0:4, 0:168:, 0:192] ## whole thing
}
