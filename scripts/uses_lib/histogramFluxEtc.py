from basicSuiteScript import *

class HistogramFluxEtc(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)

    def plotData(self, flux, meanFrames, eventCodes, label):
        print("plotting data")
        plt.hist(flux, 100)
        plt.xlabel("flux")
        plt.title("Run %d flux %s" %(self.run, label))
        plt.savefig("%s/%s_r%d_%s.png" %(self.outputDir,self.className, self.run, label))
        plt.clf()
        for i in range(meanFrames.shape[0]):
            print(i)
            plt.imshow(meanFrames[i])
            plt.colorbar()
            plt.title("Run %d module %d %s" %(self.run, i, label))
            plt.savefig("%s/%s_r%d_m%d_%s.png" %(self.outputDir,self.className, self.run, i, label))
            plt.clf()

        if eventCodes is not None:
            plt.plot(eventCodes)##, len(eventCodes))
            plt.xlabel("event codes")
            plt.title("Run %d event codes %s" %(self.run, label))
            plt.savefig("%s/%s_r%d_eventCodes_%s.png" %(self.outputDir,self.className, self.run, label))

            
if __name__ == "__main__":
    hfe = HistogramFluxEtc()
    hfe.setupPsana()

    nGoodEvents = 0
    fluxes = []
    allFluxesRun = []
    meanFrames = None
    eventCodes = None
    

    evtGen = hfe.myrun.events()
    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
            ##break
        try:
            eventCodes += hfe.getEventCodes(evt)
        except:
            eventCodes = np.array(hfe.getEventCodes(evt))
        
        flux = hfe.getFlux(evt)
        if flux is None:
            ##print("no flux found")
            pass
        else:
            fluxes.append(flux)

        allFluxes = hfe.getAllFluxes(evt)
        if allFluxes is not None:
            allFluxesRun.append(allFluxes)
            
        frames = hfe.getCalibData(evt)
        if frames is None:
            continue
        try:
            meanFrames += frames
        except:
            meanFrames = frames

        nGoodEvents += 1
        if nGoodEvents%1000 == 0:
            print("n good events analyzed: %d" %(nGoodEvents))

        if nGoodEvents > hfe.maxNevents:
            print("max n events reached, hopefully break")
            break

    print("a")
    fluxes = np.array(fluxes)
    np.save("%s/fluxes_r%d_%s.npy" %(hfe.outputDir, hfe.run, hfe.exp), fluxes)
    allFluxes = np.array(allFluxesRun)
    np.save("%s/%s_allFluxes_r%d_%s.npy" %(hfe.outputDir, hfe.className, hfe.run, hfe.exp), allFluxes)
    np.save("%s/%s_eventCodes_r%d_%s.npy" %(hfe.outputDir, hfe.className, hfe.run, hfe.exp), eventCodes)
    np.save("%s/%s_meanFrames_r%d_%s.npy" %(hfe.outputDir, hfe.className, hfe.run, hfe.exp), meanFrames/nGoodEvents)

    hfe.plotData(fluxes, meanFrames/nGoodEvents, eventCodes, "")

