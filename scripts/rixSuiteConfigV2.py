import os
if os.getenv('foo') == '1':
    print("psana1")
    from psana1Base import *
else:
    print("psana2")
    from psana2Base import *



##experimentHash = {'exp':'mfxx1005021', 'location':'MfxEndstation', 'fluxSource':'MFX-USR-DIO', 'fluxChannels':[11], 'fluxSign':-1}
#experimentHash = {'exp':'rixc00121', 'location':'RixEndstation',
experimentHash = {'exp':'rixx1003721', 'location':'RixEndstation',
                  'fluxSource':'MfxDg1BmMon',
                  'fluxChannels':[9, 10, 11, 12],
##                  'fluxChannels':[8, 14],
                  'fluxSign':1,
                  'singlePixels': [
                      [0, 150, 10], [0, 150, 100], [0, 200, 20],
                      [0, 270, 110], [0, 230, 70], [0, 210, 80],
                  ],
#                  'ROIs':['module0', 'module2', 'module4', 'module6', 'module10','module12', 'module14']
#                  'ROIs':['roiFromSwitched_e557_rmfxx1005021']
                  'ROIs':['allHRasicPixels', 'goodboxROI']#'roiAbove7k_raw_r123']
##                  'ROIs':['XavierV4']

}
##more complex approach allowing run ranges
##fluxHash = {1:['MFX-USR-DIO', 11]}
