import sys
from psana import DataSource
import numpy as np

run = eval(sys.argv[1])
ds = DataSource(exp='rixx45619',run=run)
myrun = next(ds.runs())
det = myrun.Detector('epixhr')
timing = myrun.Detector('timing')

print('pedestal means, 7 modes:',det.calibconst['pedestals'][0].mean(axis=(1,2,3)))
print('pedestal maxes, 7 modes:',det.calibconst['pedestals'][0].max(axis=(1,2,3)))

fl = []
n = 0
n20 = []


desiredCode = {'120Hz':272, '4kHz':273, '5kHz':274}

lastEventWas120Hz = False
nFoo = 0
n120s = 0
for evt in myrun.events():
    allcodes = timing.raw.eventcodes(evt)
    if lastEventWas120Hz:
        ## do something
        pass
    if not allcodes[desiredCode['120Hz']]:
##        print("found", allcodes, "not", desiredCode)
##        print("no 120Hz")
        mean = det.raw.raw(evt).mean()
        print("mean for event %d after 120Hz %0.3f" %(nFoo, mean))

        np.save("not120_%d.npy" %(nFoo), det.raw.raw(evt))
        if lastEventWas120Hz:
            print("mean for event after 120Hz %0.3f" %(mean))
            np.save("lastEventWas120Hz_%d.npy" %(n120s-1), det.raw.raw(evt))
        nFoo += 1
        lastEventWas120Hz = False
        continue
    else:
        print("found 120Hz after %d, %0.3f" %(nFoo, mean))
        mean = det.raw.raw(evt).mean()
        np.save("thisEventWas120Hz_%d.npy" %(n120s), det.raw.raw(evt))
        print("mean now %0.3f" %(mean))
        nFoo = 0
        n120s += 1
        lastEventWas120Hz = True
##136 means NEH got the beam

    rawFrames = det.raw.raw(evt)
    frames = det.raw.calib(evt)
    n20.append((frames>20).sum())
    fl.append(frames)
    n += 1
    if n%1000 == 0:
        print(n)
fl = np.array(fl)
print(n)
n20 = np.array(n20)
print(n20.mean())
