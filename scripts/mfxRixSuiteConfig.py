import os
if os.getenv('foo') == '1':
    print("psana1")
    from psana1Base import *
else:
    print("psana2")
    from psana2Base import *



##experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation', 'fluxSource':'MFX-USR-DIO', 'fluxChannels':[11], 'fluxSign':-1}
experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation',
                  'fluxSource':'MFX-DG2-BMMON',
                  'fluxChannels':[8, 10, 14],
##                  'fluxChannels':[8, 14],
                  'fluxSign':-1,
                  'singlePixels': [
                      [0, 10, 10], [0, 100, 100], [0, 200, 200],
                      [2, 300, 300], [0, 100, 310], [2, 310, 100],
                      [2, 115, 183], [2, 103,172],
                      [4, 10, 10], [4, 100, 100], [4, 200, 200],
                      [6, 300, 300], [6, 100, 310], [6, 310, 100],
                      [6, 115, 183], [6, 103,172],
                      [8, 10, 10], [8, 100, 100], [8, 200, 200],
                      [10, 300, 300], [10, 100, 310], [10, 310, 100],
                      [10, 115, 183], [10, 103,172],
                      [12, 10, 10], [12, 100, 100], [12, 200, 200],
                      [14, 300, 300], [14, 100, 310], [14, 310, 100],
                      [14, 115, 183], [14, 103,172]
                  ],
                  'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
##                  'ROIs':['roiFromSwitched_e557_rmfxx1005021']
##                  'ROIs':['allHRasicPixels']
}
##more complex approach allowing run ranges
##fluxHash = {1:['MFX-USR-DIO', 11]}
