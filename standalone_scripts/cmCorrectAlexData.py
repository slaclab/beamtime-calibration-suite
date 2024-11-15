import numpy as np
import sys
import matplotlib.pyplot as plt

nCols = 384
nRows = 192
nBanksRow = 4
nRowsPerBank = int(nRows/nBanksRow)


def colCommonModeCorrection(frame, arbitraryCut=1000):
    for c in range(nCols):
        rowOffset = 0
        for b in range(0, nBanksRow):
            if True:
                colCM = np.median(
                    frame[rowOffset : rowOffset + nRowsPerBank, c][
                        frame[rowOffset : rowOffset + nRowsPerBank, c] < arbitraryCut
                    ]
                )
                if not np.isnan(colCM):  ## if no pixels < cut we get nan
                    frame[rowOffset : rowOffset + nRowsPerBank, c] -= colCM.astype('int')
            ##except Exception:
            if False:
                print("colCM problem")
                print(frame[rowOffset : rowOffset + nRowsPerBank], c)
            rowOffset += nRowsPerBank
    return frame



f = sys.argv[1]
label = f.split('/')[-1]
label = label.split('.')[0]
rawData = np.load(f)
data = np.zeros(rawData.shape)

try:
    signalPixel = eval(sys.argv[2])
    darkPixel = eval(sys.argv[3])
except:
    print("defaulting to standard pixels")
    signalPixel = (66, 66)
    darkPixel = (6, 6)

nSkipForChargeInjectionOffset = 200
nInjections = 1024
gainCut = 1<<15
gainBitsMask = gainCut -1

dataHighSignalPixel = data[signalPixel[0],signalPixel[1],:]<gainCut
dataHighDarkPixel = data[darkPixel[0],darkPixel[1],:]<gainCut
x = np.arange(nSkipForChargeInjectionOffset, nInjections)

rawData &= gainBitsMask

pedestal = rawData[:,:,nSkipForChargeInjectionOffset]
for i in range(rawData.shape[2]):
    data[:,:, i] = rawData[:,:, i] - pedestal
print(data[:,:, 666].mean())

data = data[:,:,nSkipForChargeInjectionOffset:]
dataHighSignalPixel = dataHighSignalPixel[nSkipForChargeInjectionOffset:]
dataHighDarkPixel = dataHighDarkPixel[nSkipForChargeInjectionOffset:]

doCM = [True,False][1]

plt.scatter(x[dataHighSignalPixel], data[signalPixel[0],signalPixel[1],:][dataHighSignalPixel],color='slateblue')
plt.scatter(x[~ dataHighSignalPixel], data[signalPixel[0],signalPixel[1],:][~ dataHighSignalPixel], color='darkblue')

## real photons are quantized, allowing cut to make sense even for signal pixels
if doCM:
    label += " column common mode correction"
    for i in range(data.shape[2]):
        data[:,:,i] = colCommonModeCorrection(data[:,:,i], 32000)
else:
    label += " no common mode correction"

plt.scatter(x[dataHighDarkPixel], data[darkPixel[0],darkPixel[1],:][dataHighDarkPixel], color='orange')
plt.scatter(x[~ dataHighDarkPixel], data[darkPixel[0],darkPixel[1],:][~ dataHighDarkPixel], color='goldenrod')
plt.title("Alex data, %s" %(label))
plt.xlabel("injection")
title = "test pixels %d,%d, %d,%d in file %s" %(signalPixel[0], signalPixel[1], darkPixel[0], darkPixel[1], label)
plt.savefig(title.replace(' ', '_'))
plt.clf()
            

##plt.hist(data.flatten().clip(0,40000), 100)
plt.hist(data[data<gainCut].flatten(), 100)
plt.hist((data[data>=gainCut].flatten()), 100, alpha=0.5)
plt.title("Alex data, %s" %(label))
plt.xlabel("ADU")
title = "all pixels in file %s" %(label)
##plt.savefig(title.replace(' ', '_'))
