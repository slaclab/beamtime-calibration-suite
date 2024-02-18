from library.basicSuiteScript import *
##from fitFineScan import *

class TimeScanParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        self.doEveryPixel = False##True
        ##get rid of this
        print("doEveryPixel is", self.doEveryPixel)
        
    def plotData(self, rois, pixels, delays, label):
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(delays,rois[i], label=self.ROIfileNames[i])
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
            ax.plot(delays, rois[i], label=self.ROIfileNames[i])
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

        for i, p in enumerate(self.singlePixels):
            ax = plt.subplot()
            ax.plot(delays, pixels[i], label=str(p))
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel('Delay (Ticks)')
            plt.ylabel('Pixel ADU')
            plt.savefig("%s/%s_r%d_c%d_%s_pixel%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
            plt.clf()

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
    
    def analyze_h5(self, dataFile, norm, label):
        import h5py
        a = h5py.File(dataFile)[norm]
        delays = np.array([k for k in a.keys()])
        delays = delays.astype('int')
        delays.sort()
        d = np.array([a[str(k)] for k in delays])
        delays = np.array([d for d in delays])

        print(delays)
        offset = len(self.ROIs)
        rois = d[:,0:offset]
        pixels = d[:,offset:]
        runString = '_r%d' %(self.run)
        self.plotData(rois.T, pixels.T, delays, norm + label + runString)
            
if __name__ == "__main__":
    tsp = TimeScanParallel()
    print("have built a", tsp.className, "class")
    if tsp.file is not None:
        tsp.analyze_h5(tsp.file, 'means', tsp.label)
        tsp.analyze_h5(tsp.file, 'ratios', tsp.label)
        print("done with standalone analysis of %s, exiting" %(tsp.file))
        sys.exit()
    
    tsp.setupPsana()
    smd = tsp.ds.smalldata(filename='%s/%s_c%d_r%d_n%d.h5' %(tsp.outputDir, tsp.className, tsp.camera, tsp.run, size))

    tsp.nGoodEvents = 0
    stepMeans = {}
    stepMeans['means'] = {}
    stepMeans['ratios'] = {}
    
    offset = len(tsp.ROIs)


    stepGen = tsp.getStepGen()
##    for nstep, step in enumerate (tsp.ds.steps()):
    for nstep, step in enumerate (stepGen):
        ##scanValue = tsp.getScanValue(step, useStringInfo=True)
        scanValue = tsp.getScanValue(step, True)
        print(scanValue, "in tsp")
        roiAndPixelSums = np.zeros(len(tsp.ROIs) + len(tsp.singlePixels)).astype(np.uint32)
        ratioSums = np.zeros(len(tsp.ROIs) + len(tsp.singlePixels)).astype(np.float32)
                
        nGoodInStep = 0
        for nevt, evt in enumerate(step.events()):
            if evt is None:
                continue
            doFast = [True, False][0]
            fakeFlux = [True, False][1]
            if doFast:
                ec = tsp.getEventCodes(evt)
                if ec[137]:
                    tsp.flux = tsp._getFlux(evt) ## fix this
                    continue
                    #frames = tsp.det.calib(evt)
                    ##frames = tsp.det.raw(evt)&0x3fff
                elif ec[281]:
                    frames = tsp.getRawData(evt, gainBitsMasked=True)
                else:
                    continue
            else:
                tsp.flux = tsp._getFlux(evt) ## fix this
                frames = tsp.getRawData(evt, gainBitsMasked=True)

            
            if frames is None:
                ##print("no frame")
                continue
            flux = tsp.getFlux(evt)
            if fakeFlux:
                flux = 1.
            elif flux is None:
                print("no flux")
                continue
            elif flux < tsp.threshold:
                print("flux =", flux, "<", tsp.threshold, "skip")
                continue
            nGoodInStep += 1
            
            if False and tsp.doEveryPixel:
                try:
                    stepSum += frames.astype(float)
                    stepEvents += 1
                except:
                    stepSum = frames
                    stepEvents = 1

            for i, roi in enumerate(tsp.ROIs):
                ##m = np.multiply(roi, frames).mean()
                m = frames[roi==1].mean()
                roiAndPixelSums[i] += m
                ratioSums[i] += m/flux

            for j, _ in enumerate(tsp.singlePixels):
                v = frames[tuple(tsp.singlePixels[j])]
                roiAndPixelSums[offset+j] += v
                ratioSums[offset+j] += v/flux

            
            tsp.nGoodEvents += 1
            if tsp.nGoodEvents%100 == 0:
                print("n good events analyzed: %d" %(tsp.nGoodEvents))
                ##                  print("switched pixels: %d" %((switchedPixels>0).sum()))

            if tsp.nGoodEvents > tsp.maxNevents:
                break


        if nGoodInStep == 0:
            roiAndPixelSums = None
            ratioSums = None

        step_sums = None
        ##print(roiAndPixelSums is None)
        step_sums = smd.sum(roiAndPixelSums)
        step_ratio_sums = smd.sum(ratioSums)
        step_nsum = smd.sum(nGoodInStep)
        if False and roiAndPixelSums is not None:
            step_sums = smd.sum(roiAndPixelSums)
            step_ratio_sums = smd.sum(ratioSums)
            step_nsum = smd.sum(nGoodInStep)
        if step_sums is not None:
            stepMeans['means'][str(scanValue)] = step_sums/step_nsum
            stepMeans['ratios'][str(scanValue)] = step_ratio_sums/step_nsum

    if smd.summary:
        ##smd.save_summary(unNormalized=stepMeans, fluxNormalized=stepRatioMeans)
        smd.save_summary(stepMeans)
    smd.done()
    
    if False:
        np.save("%s/means_c%d_r%d_%s.npy" %(tsp.outputDir, tsp.camera, tsp.run, tsp.exp), np.array(roiMeans))
        np.save("%s/fluxes_r%d_%s.npy" %(tsp.outputDir, tsp.run, tsp.exp), np.array(fluxes))
        ##    np.save("%s/ratios_c%d_r%d_%s.npy" %(tsp.outputDir, tsp.camera, tsp.run, tsp.exp), np.array(ratios))
        np.save("%s/delays_c%d_r%d_%s.npy" %(tsp.outputDir, tsp.camera, tsp.run, tsp.exp), np.array(delays))
        
        tsp.plotData(ratios, delays, "normalized_signal")
        tsp.plotData(roiMeans, delays, "signal")

