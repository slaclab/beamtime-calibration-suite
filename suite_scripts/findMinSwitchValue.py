from calibrationSuite.basicSuiteScript import *

class FindMinSwitchValue(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)

    def plotData(self, data, img, label):
        plt.hist(data.flatten(), 100)
        plt.xlabel('Min switched value (ADU in low)')
##        plt.ylabel('Step Mean (keV)')
        plt.savefig("%s_r%d_%s.png" %(self.__class__.__name__, self.run, label))
        plt.clf()



if __name__ == "__main__":
    fmsv = FindMinSwitchValue()
    fmsv.setupPsana()
##    fmsv.setROI('roiFromSwitched_e398_rmfxx1005021.npy')
    nGoodEvents = 0
    minRaw = None

    while True:
        evt = fmsv.getEvt()
        if evt is None:
            break
        
        rawFrames = fmsv.getRawData(evt, gainBitsMasked=False)
        if rawFrames is None:
            print("No ePix10k contrib found")
            continue

        fG1 = rawFrames>=fmsv.g0cut
        try:
            b = np.bitwise_and(fG1,rawFrames<minRaw)
        except:
            minRaw = rawFrames*0 + 0xffff
            b = np.bitwise_and(fG1,rawFrames<minRaw)
            
        minRaw[b] = rawFrames[b]
   
        nGoodEvents += 1
        if nGoodEvents%100 == 0:
            print("n good events analyzed: %d" %(nGoodEvents))

        if nGoodEvents > fmsv.maxNevents:
            break

    minRaw = minRaw.astype('int')&fmsv.gainBitsMask

    np.save("minRaw_e%d_r%s.npy" %(fmsv.run, fmsv.exp), minRaw)
    fmsv.plotData(minRaw, fmsv.getImage(evt, minRaw), "foo")

