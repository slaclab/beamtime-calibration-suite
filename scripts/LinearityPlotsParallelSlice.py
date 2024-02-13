from basicSuiteScript import *

## This builds and analyzes a dict with keys:
## 'rois' - ROI fluxes and means
## 'g0s' -per-pixel g0 fluxes and values, ragged or None-filled
## ditto with 1

class LinearityPlotsParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__("scan")##self)
        self.saturated = [True, False][0]
        print("using saturation fit =", self.saturated)
        try:
            print('positive events:', 'positive' in self.special)
        except:
            pass
        
    def plotAutorangingData(self, g0s, g1s, g0Fluxes, g1Fluxes, label):
        ## this is just be for single pixels
        ## index in case that's ever supported
        ## only really makes sense as calib
        for i, p in enumerate(self.singlePixels):
            if len(g0s[i])>0:
                plt.scatter(g0Fluxes[i], g0s[i], c='r', marker='.', s=1)
            if len(g1s[i])>0:
                plt.scatter(g1Fluxes[i], g1s[i], c='b', marker='.', s=1)
            plt.xlabel('wave8 flux (ADU)')
            if 'raw' in label:
                plt.ylabel('Red medium, blue low (ADU)')
            else:
                plt.ylabel('Red medium, blue low (keV)')
            if 'yClip' in label:
                plt.ylim(0, 4000)
            if 'xClip' in label:
                if len(g1Fluxes[i])>0:
                    plt.xlim(g1Fluxes[i].min()*0.95, max(g1Fluxes[i].max(), g1Fluxes[i].max())*1.05)
                else:
                    plt.close()
                    return
                ##lot of hackiness here
                
            plt.title(label)
            plt.savefig("%s/%s_p%d_r%d_c%d_%s.png" %(self.outputDir, self.className, i, self.run, self.camera, label))
            plt.close()

    def plotAutorangingData_profile(self, g0s, g1s, g0Fluxes, g1Fluxes, label, partialMode=None, order=1):
        ## this is just for single pixels
        ## index in case that's ever supported
        ## only really makes sense as catlib
        import seaborn as sns
        for i, p in enumerate(self.singlePixels):
            fig, ax = plt.subplots()
            if partialMode != 1 and len(g0s[i])>0:
                x = g0Fluxes[i]
                y = g0s[i]
                sns.regplot(x=x, y=y, x_bins=40, marker='.', ax=ax, order=order)##add fit_reg=None for no plot
            if partialMode != 0 and len(g1s[i])>0:
                x = g1Fluxes[i]
                y = g1s[i]
                sns.regplot(x=x, y=y, x_bins=40, marker='.', ax=ax, order=order)##add fit_reg=None for no plot
            plt.xlabel('wave8 flux (ADU)')
            if 'raw' in label:
                plt.ylabel('Red medium, blue low (ADU)')
            else:
                plt.ylabel('Red medium, blue low (keV)')
            if 'yClip' in label:
                plt.ylim(0, 4000)
            if 'xClip' in label:
                if len(g1Fluxes[i])>0:
                    plt.xlim(g1Fluxes[i].min()*0.95, max(g1Fluxes[i].max(), g1Fluxes[i].max())*1.05)
                else:
                    plt.close()
                    return
                ##lot of hackiness here
                
            plt.title(label+"_profile")
            plt.savefig("%s/%s_p%d_r%d_c%d_%s_profile.png" %(self.outputDir, self.className, i, self.run, self.camera, label))
            plt.close()

    def plotDataROIs(self, means, flux, label, raw=True):
        ## assume no autoranging
        ## raw or calib
        if raw:
            ylabel = 'ADU'
        else:
            ylabel = 'keV'
        for i, roi in enumerate(self.ROIs):
            plt.scatter(flux, means[i], marker='.')
            plt.xlabel('wave8 flux (ADU)')
            plt.ylabel('detector ROI mean (%s)' %(ylabel))
            plt.savefig("%s/%s_roi%d_r%d_c%d_%s.png" %(self.outputDir, self.className, i, self.run, self.camera, label))
            plt.close()

    def fitData(self, x, y, saturated=False):##, gainMode, label):
        if saturated:
            ##f = fitFunctions.saturatedLinear
            ##p0 = [1, 0, x.mean(), y.max()]
            f = fitFunctions.linear
            p0 = [0, y.mean()]
            popt, pcov = curve_fit(f, x, y, p0=p0)
            f = fitFunctions.saturatedLinearB
            p0 = [popt[0], popt[1], y.max()]
        else:
            f = fitFunctions.linear
            p0 = [0, y.mean()]
        popt, pcov = curve_fit(f, x, y, p0=p0)
        y_fit = f(x, *popt)
        r2 = fitFunctions.calculateFitR2(y, y_fit)
        
        ##condition = np.linalg.cond(pcov)
        return popt, pcov, y_fit, r2
        
    def analyze_h5(self, dataFile, label):
        import h5py
        data = h5py.File(dataFile)
        fluxes = data['fluxes'][()]
        print(fluxes)
        rois = data['rois'][()]
        pixels = data['pixels'][()]
        g0s = []
        g0Fluxes = []
        g1s = []
        g1Fluxes = []
        for s,_ in enumerate(self.singlePixels):
            g0s.append(pixels[:,s,1][pixels[:,s,0]==0])
            g0Fluxes.append(fluxes[pixels[:,s,0]==0])
            g1s.append(pixels[:,s,1][pixels[:,s,0]==1])
            g1Fluxes.append(fluxes[pixels[:,s,0]==1])

        lpp.plotAutorangingData_profile(g0s,g1s, g0Fluxes, g1Fluxes, label)
        for order in [1,2]:
        ##for order in [1]:
            lpp.plotAutorangingData_profile(g0s,g1s, g0Fluxes, g1Fluxes, label+'highOrMed_poly%d' %(order), partialMode=0, order=order)
            lpp.plotAutorangingData_profile(g0s,g1s, g0Fluxes, g1Fluxes, label+'low_poly%d' %(order), partialMode=1, order=order)
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label)
        ##lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label+"_yClip_xClip")
        lpp.plotDataROIs(rois.T, fluxes, "ROIs")

    def analyze_h5_slice(self, dataFile, label):
        data = h5py.File(dataFile)
        fluxes = data['fluxes'][()]
        pixels = data['slice'][()]
        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        fitInfo = np.zeros((rows, cols, 8)) ##g0 slope, intercept, r2; g1 x3; max, min
        for i in range(rows):
            for j in range(cols):
                g0 = pixels[:,i,j]<lpp.g0cut
                g1 = np.logical_not(g0)
                if len(g0[g0])>2:
                    y = np.bitwise_and(pixels[:,i,j][g0], lpp.gainBitsMask)
                    ##fitPar, covar, fitFunc = self.fitData(fluxes[g0], y)
                    fitPar, covar, fitFunc, r2 = self.fitData(fluxes[g0], y, saturated=self.saturated)
                    print(i,j, fitPar, r2, 0)
                    ##np.save("temp_r%dc%d_x.py" %(i,j), fluxes[g0])
                    ##np.save("temp_r%dc%d_y.py" %(i,j), y)
                    ##np.save("temp_r%dc%d_func.py" %(i,j), fitFunc)
                    fitInfo[i,j,0:2] = fitPar[0:2] ## indices for saturated case
                    fitInfo[i,j, 2] = r2
                    fitInfo[i,j, 6] = y.max()
                    if i%2==0 and i == j:
                        plt.scatter(fluxes[g0], y, zorder=1, marker='.', s=1)
                        if self.saturated:
                            plt.scatter(fluxes[g0], fitFunc, color='k', zorder=2, s=1)
                        else:
                            plt.plot(fluxes[g0], fitFunc, color='k', zorder=2)
                if len(g1[g1])>2:
                    y = np.bitwise_and(pixels[:,i,j][g1], lpp.gainBitsMask)
                    y_g1_min = y.min()
                    fitPar, covar, fitFunc, r2 = self.fitData(fluxes[g1], y)
                    print(i,j, fitPar, r2, 1)
                    fitInfo[i,j,3:5] = fitPar
                    fitInfo[i,j, 5] = r2
                    fitInfo[i,j, 7] = y.min()
                    if i%2==0 and i == j:
                        plt.scatter(fluxes[g1], y, zorder=3, marker='.')
                        plt.plot(fluxes[g1], fitFunc, color='k', zorder=4)

                if i%2==0 and i==j:
                    plt.savefig("%s/%s_slice_%d_%d_r%d_c%d_%s.png" %(self.outputDir, self.className, i, j, self.run, self.camera, label))
                    plt.close()
                    
        np.save("%s/%s_r%d_sliceFits_%s.npy" %(self.outputDir, self.className, self.run, label), fitInfo)
        
                    
if __name__ == "__main__":
    lpp = LinearityPlotsParallel()
    print("have built an LPP")
    if lpp.file is not None:
        lpp.analyze_h5(lpp.file, lpp.label+'_raw')
        lpp.analyze_h5_slice(lpp.file, lpp.label+'_raw')
        print("done with standalone analysis of %s, exiting" %(lpp.file))
        sys.exit(0)
    
    doKazFlux = False
    if doKazFlux:
        print("doing Kaz flux events")
    else:
        print("not doing Kaz events")
        
    lpp.setupPsana()
    smd = lpp.ds.smalldata(filename='%s/%s_c%d_r%d_n%d.h5' %(lpp.outputDir, lpp.className, lpp.camera, lpp.run, size))


    nGoodEvents = 0
    fluxes = [] ## common for all ROIs
    roiMeans = [[] for i in lpp.ROIs]
    g0s = [[] for i in lpp.singlePixels]
    g1s = [[] for i in lpp.singlePixels]
    g0Fluxes = [[] for i in lpp.singlePixels]
    g1Fluxes = [[] for i in lpp.singlePixels]
    
    evtGen = lpp.myrun.events()
    for nevt, evt in enumerate(evtGen):
        doFast = True##False ## for 2400 etc Hz
        if doFast:
            ec = lpp.getEventCodes(evt)
            if ec[137]:
                lpp.flux = lpp._getFlux(evt) ## fix this
                lpp.fluxTS = lpp.getTimestamp(evt)
                ##print("found flux", lpp.flux)
                continue
                #frames = lpp.det.calib(evt)
                ##frames = lpp.det.raw(evt)&0x3fff
            elif ec[281]:
                lpp.framesTS = lpp.getTimestamp(evt)
                rawFrames = lpp.getRawData(evt, gainBitsMasked=False)
                frames = lpp.getCalibData(evt)
            else:
                continue
        else:
            lpp.flux = lpp._getFlux(evt) ## fix this
            rawFrames = lpp.getRawData(evt, gainBitsMasked=False)
            frames = lpp.getCalibData(evt)

        if rawFrames is None:
            print("No contrib found")
            continue
        ## could? should? check for calib here I guess
        if lpp.special is not None and 'parity' in lpp.special:
            if lpp.getPingPongParity(rawFrames[0][144:224, 0:80]) == ('negative' in lpp.special):
                continue
            ##print(nevt)
        
        flux = lpp.getFlux(evt)
        if flux is None:
            print("no flux found")
            continue
        delta = lpp.framesTS-lpp.fluxTS
        if delta > 1000:
            print("frame - bld timestamp delta too large:", delta)
            continue

        roiMeans = []
        for i, roi in enumerate(lpp.ROIs):
            ##m = np.multiply(roi, frames).mean()
            m = frames[roi==1].mean()
            roiMeans.append(m)

        if doKazFlux:
            rf = rawFrames[tuple(lpp.singlePixels[0])]
            if not (flux<20000 and rf >= lpp.g0cut and rf > 2950):
                ##not a Kaz event
                nGoodEvents += 1
                if nGoodEvents > lpp.maxNevents:
                    break
                continue

        singlePixelData = []    
        for j, p in enumerate(lpp.singlePixels):
            singlePixelData.append([int(rawFrames[tuple(p)] >= lpp.g0cut),
                                    rawFrames[tuple(p)]&lpp.gainBitsMask])


        smd.event(evt,
                  fluxes=flux,
                  rois=np.array(roiMeans),
                  pixels=np.array(singlePixelData),
                  slice=rawFrames[0][lpp.regionSlice]
                  )

        nGoodEvents += 1
        if nGoodEvents%100 == 0:
            print("n good events analyzed: %d" %(nGoodEvents))
##            print("switched pixels: %d" %((switchedPixels>0).sum()))

        if nGoodEvents > lpp.maxNevents:
            break

    
    if False:
        np.save("%s/%s_means_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), roiMeans)
        np.save("%s/%s_fluxes_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), fluxes)
        np.save("%s/%s_singlePixel_g0s_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), g0s)
        np.save("%s/%s_singlePixel_g1s_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), g1s)
        np.save("%s/%s_g0Fluxes_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), g0Fluxes)
        np.save("%s/%s_g1Fluxes_r%d_c%d_%s.npy" %(lpp.outputDir, lpp.className, lpp.run, lpp.camera, lpp.exp), g1Fluxes)

    if False:
        label = "rawInTimeDot"
        if doKazFlux:
            label = "raw_smarterPoints"
            label += "_kazEventsNear"
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label)
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label+"_yClip_xClip")
        lpp.plotDataROIs(roiMeans, fluxes, "roiTest")

    smd.done()

