from basicSuiteScript import *
import sys
import numpy as np
import matplotlib.pyplot as plt

class PersistenceCheck(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        print("in", sys.argv[0])
        self.skipN = 0

    def plotData(self, data, label):
        print("plotStuff method")
        print(data.shape)
##        plt.graph(
        plt.scatter(data[:,1], data[:,0])
        plt.title("Run %d post-kick vs kick signal" %(self.run))
        plt.xlabel("pre-kick ROI mean (keV)")
        plt.ylabel("kicked ROI mean (keV)")
        plt.savefig("%s/%s_r%d_c%d%s.png" %(self.outputDir, self.className, self.run, self.camera, label))


if __name__ == "__main__":
    pc = PersistenceCheck()
    print("have built a PC")
    pc.setupPsana()
##    pc.setROI('roiFromSwitched_e398_rmfxx1005021.npy')

    nEvent = -1
    nGoodEvents = 0
    nKicked = 0
    unKickedMeans = []
    missingMeans = []
    data = []
    previousShotKicked = False
    previousShotMean = -666
    previousShotFlux = -666

    while True:
        evt = pc.getEvt()
        if evt is None:
            break
        nEvent += 1
        frames = pc.getCalibData(evt)
        ## could do raw - ped instead
        if frames is None:
            print("No contrib found")
            continue
        
        flux = pc.getFlux(evt)
        if flux is None:
            print("no flux found")
            continue

        if pc.ROI is None:
            pc.ROI = (frames * 0)+1
        pc.ROI = pc.ROIs[-1]
        label = ""
        if False:
            pc.ROI = np.load("roiFromAboveThreshold_r671_c1_calib.npy")
            label = "_intenseRegion"
            
        rm = np.multiply(pc.ROI, frames).mean()

        kicked = pc.isKicked(evt)

        if kicked:
            if nKicked < 10:
                print("found a nominally kicked event", nEvent, "n kicked", nKicked)
                print("current, previous fluxes:", flux, previousShotFlux)
            nKicked += 1
            missingMeans.append(rm)
            if not previousShotKicked:
                data.append([rm, previousShotMean, flux, previousShotFlux])
        else:
            unKickedMeans.append(rm)

        previousShotMean = rm
        previousShotFlux = flux
        previousShotKicked = kicked

        nGoodEvents += 1
        if nGoodEvents%100 == 0:
            print("n good events analyzed: %d, n overall %d" %(nGoodEvents, nEvent))
##            print("switched pixels: %d" %((switchedPixels>0).sum()))

        if nEvent > pc.maxNevents:
            break

        if kicked:
            if nKicked<10:
                print("skip next %d events" %(pc.skipN))
            ## this is somewhat fragile
            for i in range(pc.skipN):
                try:
                    evt = pc.getEvt()
                    if evt is None:
                        break
                    nEvent += 1
                except:
                    break

    unKickedMeans = np.array(unKickedMeans)
    missingMeans = np.array(missingMeans)
    if missingMeans.size > 0:
        np.save("signalMeans_r%d.npy" %(pc.run), unKickedMeans)
        np.save("kickedMeans_r%d.npy" %(pc.run), missingMeans)


    data = np.array(data)
    np.save("%s/persistenceData_%s_r%d_c%d%s.npy" %(pc.outputDir, pc.exp, pc.run, pc.camera, label), data)
    pc.plotData(data, label)
