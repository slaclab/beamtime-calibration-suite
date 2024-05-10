import h5py
import numpy as np
from scipy.stats import logistic

mc = False
if mc:
    hfName = '../data/fake_TID_dataset.h5'
    data = np.zeros([30, 10, 4, 192, 384])
    ## 30 steps of 10 events for an epixM

    data += np.random.normal(10000, 10, data.shape)
    nSteps = data.shape[0]
    for i in range(nSteps):
        delta = 1000 * logistic.sf((i-nSteps/2.)/2.)
        print(i, delta)
        data[i] += delta
    hf = h5py.File(hfName, 'w')
    stepVals = range(0, nSteps*10000, 10000)

else:
    hfName = '../data/test_led_TID_dataset.h5'
    hf = h5py.File(hfName, 'w')
    data = np.load("/sdf/data/lcls/ds/rix/rixx1005922/results//test/wrappedMultistepXavierFile.npy")
    nSteps = data.shape[0]
    stepVals = range(0, nSteps)

if True:

    hf.create_dataset('scriptType', data="fake")
    hf.create_dataset('frames', data=data)
    hf.create_dataset('step', data=range(nSteps))
    hf.create_dataset('step_value', data=stepVals)
    hf.close()

tidFile = h5py.File(hfName, 'r')
print(tidFile.keys())
stepArray = tidFile['step'][()]
for s in stepArray:
    print(s, tidFile['step_value'][s])
    if s>5:
        break
                  
print(str(tidFile['scriptType'][()], encoding='utf-8'))
