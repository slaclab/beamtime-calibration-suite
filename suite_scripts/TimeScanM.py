from calibrationSuite.basicSuiteScript import *
##from fitFineScan import *

class TimeScanM(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        self.doEveryPixel = True
        print("doEveryPixel is", self.doEveryPixel)

    def foo(self):
        print("foo")
        
    def plotData(self, data, delays, label):
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(delays,data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.5)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel('Time delay (Ticks)')
           # plt.ylabel('Step Mean (keV)')
            plt.ylabel('Step Mean (ADU)')
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.savefig("%s/%s_r%d_c%d_%s_ROI%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
            plt.clf()
            
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(delays, data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel('Time delay (Ticks)')
            # plt.ylabel('Step Mean (keV)')
            plt.ylabel('Step Mean (ADU)')
            ##plt.yscale('log')
            plt.legend(loc='upper right')
        plt.savefig("%s/%s_r%d_c%d_%s_All%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
        plt.clf()
       # plt.show()
       
    def analyzeData(self, delays, data, label):
        edge = np.zeros(data.shape[0])
        for m in range(data.shape[1]):
            for r in range(data.shape[2]):
                for c in range(data.shape[3]):
                    d = data[:, m, r, c]
                    p0 = estimateFineScanPars(delays, d)
                    f = fineScanFunc
                    coeff, var = curve_fit(f, delays, d, p0=p0)
                    edge[m, r, c] = coeff[1]
        return edge

    def main(self):
        print("have built a", self.className, "class")
        self.setupPsana()
        ##    tsr.setROI('roiFromSwitched_e398_rmfxx1005021.npy')
        self.nGoodEvents = 0
        roiMeans = [[] for i in self.ROIs]
        ratios = [[] for i in self.ROIs]
        pixelMeans = [[] for i in self.ROIs]
        pixelRatios = [[] for i in self.ROIs]
        if self.doEveryPixel:
            stepMeanFrames = []
            stepSum = []
            stepEvents = 0
        fluxes = []
        delays = []
    

        stepGen = self.getStepGen()
        ##    for nstep, step in enumerate (self.ds.steps()):
        for nstep, step in enumerate (stepGen):
            ##scanValue = self.getScanValue(step, useStringInfo=True)
            scanValue = self.getScanValue(step, True)
            print(scanValue, "in self")
            ##    pvList = self.controlData().pvControls()
            if self.doEveryPixel:
                if stepEvents != 0:
                    stepMeanFrames.append(stepSum/stepEvents)
                    stepSum = None
                    stepEvents = 0 ## next step might be empty
                
            meanArray = [[] for i in self.ROIs]
            fluxArray = []
            ##                print (f'Step: {nstep}, name/value: {pv.name()}/{pv.value()}')
            nGoodInStep = 0
            for nevt, evt in enumerate(step.events()):
                if evt is None:
                    continue
                doFast = True
                fakeFlux = True
                if doFast:
                    ec = self.getEventCodes(evt)
                    if ec[137]:
                        self.flux = self._getFlux(evt) ## fix this
                        continue
                    #frames = self.det.calib(evt)
                    ##frames = self.det.raw(evt)&0x3fff
                    elif ec[281]:
                        frames = self.getRawData(evt, gainBitsMasked=True)
                    else:
                        continue
                else:
                    self.flux = self._getFlux(evt) ## fix this
                    frames = self.getRawData(evt, gainBitsMasked=True)

            
                if frames is None:
                    ##print("no frame")
                    continue
                flux = self.getFlux(evt)
                if fakeFlux:
                    flux = 1.
                if flux is None:
                    print("no flux")
                    continue
                if flux == 0.:
                    print("flux = 0...: skip")
                    continue
                fluxArray.append(flux)
                nGoodInStep += 1
            
                if self.doEveryPixel:
                    try:
                        stepSum += frames.astype(float)
                        stepEvents += 1
                    except:
                        stepSum = frames
                        stepEvents = 1

                for i, roi in enumerate(self.ROIs):
                    ##m = np.multiply(roi, frames).mean()
                    m = frames[roi==1].mean()
                    meanArray[i].append(m)
        
                self.nGoodEvents += 1
                if self.nGoodEvents%100 == 0:
                    print("n good events analyzed: %d" %(self.nGoodEvents))
                    ##                  print("switched pixels: %d" %((switchedPixels>0).sum()))

                if self.nGoodEvents > self.maxNevents:
                    break


            if nGoodInStep>0:
                ##delays.append(pvList[0].value())
                delays.append(scanValue)
                means = np.array(meanArray)
                flux = np.array(fluxArray)
        
                for i, roi in enumerate(self.ROIs):
                    roiMeans[i].append(means[i].mean())
                    ratios[i].append(means[i].mean()/flux.mean())

                fluxes.append(flux.mean())
            else:
                print(nstep, nGoodInStep)
            
        delays = np.array(delays)
        if self.doEveryPixel:
            if stepEvents != 0:
                stepMeanFrames.append(stepSum/stepEvents)
            stepMeanFrames = np.array(sortArrayByList(delays, stepMeanFrames))
            np.save("%s/%s_allMeanFrames_c%d_r%d.npy" %(self.outputDir, self.className, self.camera, self.run), stepMeanFrames)
            ##self.analyzeData(np.array(sorted(delays)), stepMeanFrames, 'test')

        roiMeans = sortArrayByList(delays, roiMeans)
        fluxes = sortArrayByList(delays, fluxes)
        ratios = sortArrayByList(delays, ratios)
        delays = sorted(delays)


    
        np.save("%s/means_c%d_r%d_%s.npy" %(self.outputDir, self.camera, self.run, self.exp), np.array(roiMeans))
        np.save("%s/fluxes_r%d_%s.npy" %(self.outputDir, self.run, self.exp), np.array(fluxes))
        ##    np.save("%s/ratios_c%d_r%d_%s.npy" %(self.outputDir, self.camera, self.run, self.exp), np.array(ratios))
        np.save("%s/delays_c%d_r%d_%s.npy" %(self.outputDir, self.camera, self.run, self.exp), np.array(delays))
        self.plotData(ratios, delays, "normalized_signal")
        self.plotData(roiMeans, delays, "signal")
    
if __name__ == "__main__":
    main()
    
