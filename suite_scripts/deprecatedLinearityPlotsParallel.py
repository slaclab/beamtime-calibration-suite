from calibrationSuite.basicSuiteScript import *

## This builds and analyzes a dict with keys:
## 'rois' - ROI fluxes and means
## 'g0s' -per-pixel g0 fluxes and values, ragged or None-filled
## ditto with 1

class LinearityPlotsParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__("scan")##self)

    def plotAutorangingData(self, g0s, g1s, g0Fluxes, g1Fluxes, label):
        ## this is just be for single pixels
        ## index in case that's ever supported
        ## only really makes sense as calib
        for i, p in enumerate(self.singlePixels):
            if len(g0s[i])>0:
                plt.scatter(g0Fluxes[i], g0s[i], c='r', marker='.')
            if len(g1s[i])>0:
                plt.scatter(g1Fluxes[i], g1s[i], c='b', marker='.')
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
                    plt.clf()
                    return
                ##lot of hackiness here
                
            plt.title(label)
            plt.savefig("%s/%s_p%d_r%d_c%d_%s.png" %(self.outputDir, self.className, i, self.run, self.camera, label))
            plt.close()

    def plotAutorangingData_profile(self, g0s, g1s, g0Fluxes, g1Fluxes, label, partialMode=None):
        ## this is just for single pixels
        ## index in case that's ever supported
        ## only really makes sense as catlib
        import seaborn as sns
        for i, p in enumerate(self.singlePixels):
            fig, ax = plt.subplots()
            if partialMode != 1 and len(g0s[i])>0:
                x = g0Fluxes[i]
                y = g0s[i]
                sns.regplot(x=x, y=y, x_bins=40, marker='.', ax=ax)##add fit_reg=None for no plot
            if partialMode != 0 and len(g1s[i])>0:
                x = g1Fluxes[i]
                y = g1s[i]
                sns.regplot(x=x, y=y, x_bins=40, marker='.', ax=ax)##add fit_reg=None for no plot
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
                    plt.clf()
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
            plt.scatter(flux, means[i])
            plt.xlabel('wave8 flux (ADU)')
            plt.ylabel('detector ROI mean (%s)' %(ylabel))
            plt.savefig("%s/%s_roi%d_r%d_c%d_%s.png" %(self.outputDir, self.className, i, self.run, self.camera, label))
            plt.clf()

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
        lpp.plotAutorangingData_profile(g0s,g1s, g0Fluxes, g1Fluxes, label+'highOrMed', partialMode=0)
        lpp.plotAutorangingData_profile(g0s,g1s, g0Fluxes, g1Fluxes, label+'low', partialMode=1)
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label)
        ##lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label+"_yClip_xClip")
        lpp.plotDataROIs(rois.T, fluxes, "ROIs")

if __name__ == "__main__":
    lpp = LinearityPlotsParallel()
    print("have built an LPP")
    if lpp.file is not None:
        lpp.analyze_h5(lpp.file, lpp.label)
        print("done with standalone analysis of %s, exiting" %(lpp.file))
        sys.exit(0)
    
    doKazFlux = False
    if doKazFlux:
        print("doing Kaz flux events")
    else:
        print("not doing Kaz events")
        
    lpp.setupPsana()
    smd = lpp.ds.smalldata(filename='%s/%s_c%d_r%d_n%d.h5' %(lpp.outputDir, lpp.className, lpp.camera, lpp.run, size))


    
    ##    efs.setROI('roiFromSwitched_e398_rmfxx1005021.npy')
    if lpp.run>= 550 and lpp.run < 590: ## pinhole study range
        lpp.singlePixels = [[0, 115, 183], [0, 103,172],
                            [0, 116, 160], [0, 117, 160],
                            [0, 293, 232], [0, 300, 240]
        ]
        if doKazFlux:
            for i in range(-5, 5):
                for j in range(-5, 5):
                    if i==j==0:
                        continue
                    lpp.singlePixels.append([0,115+i, 183+j])

    if False and lpp.run>650:
        if lpp.camera == 1:
            lpp.singlePixels = [[0, 20, 130], [0, 45,133],
                                [0, 95, 136], [0, 110, 139],
                                [0, 125, 140], [0, 144, 145]
            ]
            
    nGoodEvents = 0
    fluxes = [] ## common for all ROIs
    roiMeans = [[] for i in lpp.ROIs]
    g0s = [[] for i in lpp.singlePixels]
    g1s = [[] for i in lpp.singlePixels]
    g0Fluxes = [[] for i in lpp.singlePixels]
    g1Fluxes = [[] for i in lpp.singlePixels]
    
##    while True:
##        if lpp.runRange is None:
##            evt = lpp.getEvt()
##        else:
##            evt = lpp.getEvtFromRuns()
##            evt = lpp.getEvtFromRuns()
##        if evt is None:
##            break

## something weird about break in psana2 parallel
## worry about multiple runs another day
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

        ##rawFrames = lpp.det.raw(evt)
        ##frames = lpp.det.calib(evt)
##        rawFrames = lpp.getRawData(evt, gainBitsMasked=True)
##        frames = lpp.getCalibData(evt)
        if rawFrames is None:
            print("No contrib found")
            continue
        ## check for calib here I guess
        
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
                  pixels=np.array(singlePixelData)
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

        label = "rawInTimeDot"
        if doKazFlux:
            label = "raw_smarterPoints"
            label += "_kazEventsNear"
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label)
        lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label+"_yClip_xClip")
        lpp.plotDataROIs(roiMeans, fluxes, "roiTest")

    smd.done()

