from basicSuiteScript import *

class EventScanParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        
    def plotData(self, data, pixels, eventNumbers, label):
        if 'timestamp' in label:
            xlabel = 'Timestamp (s)'
            ##xlabel = 'Timestamp (scaled to separation)'
        else:
            xlabel = 'Event number'
        print(xlabel,label)
        
        for i, roi in enumerate(self.ROIs):
            ##data[i] -= data[i].mean()
            ax = plt.subplot()
            ##ax.plot(eventNumbers,data[i], label=self.ROIfileNames[i])
            ax.scatter(eventNumbers,data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.5)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel(xlabel)
            plt.ylabel('Mean (ADU)')
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.savefig("%s/%s_r%d_c%d_%s_ROI%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
            plt.clf()
            
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ##ax.plot(eventNumbers, data[i], label=self.ROIfileNames[i])
            ax.scatter(eventNumbers, data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel(xlabel)
            plt.ylabel('Mean (ADU)')
            ##plt.yscale('log')
            plt.legend(loc='upper right')
        plt.savefig("%s/%s_r%d_c%d_%s_All%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
        plt.clf()
        # plt.show()

        for i, p in enumerate(self.singlePixels):
            ax = plt.subplot()
            ##ax.plot(eventNumbers, pixels[i], label=str(p))
            ##ax.scatter(eventNumbers, pixels[i], marker='.', label=str(p))
            ax.plot(eventNumbers, pixels[i], '.', ms=1, label=str(p))
            ##ax.scatter(eventNumbers, pixels[i], marker='.', s=1, label=str(p))
            plt.xlabel(xlabel)
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

    def analyze_h5(self, dataFile, label):
        import h5py
        data = h5py.File(dataFile)
        ts = data['timestamps'][()]
        print(ts)
        pixels = data['pixels'][()]
        rois = data['rois'][()]
        pixels = sortArrayByList(ts, pixels)
        rois = sortArrayByList(ts, rois)
        ts.sort()
        ts = ts-ts[0]
        ##ts = ts/np.median(ts[1:]-ts[0:-1])
        print(ts)

## stopped working in psana
##        runNumbers = data['runnum'][()]
##        runNumbers.sort()
##        runString = ''
##        if runNumbers[0]!=runNumbers[-1]:
##            runString = str(runNumbers[0]) + "-" + str(runNumbers[-1])
##        self.run=runNumbers[0]
        self.plotData(np.array(rois).T, np.array(pixels).T, ts, 'timestamps' + label)
            
if __name__ == "__main__":
    esp = EventScanParallel()
    print("have built a", esp.className, "class")
    if esp.file is not None:
        esp.analyze_h5(esp.file, esp.label)
        print("done with standalone analysis of %s, exiting" %(esp.file))
        sys.exit(0)
    
    esp.setupPsana()

    smd = esp.ds.smalldata(filename='%s/%s_c%d_r%d_n%d.h5' %(esp.outputDir, esp.className, esp.camera, esp.run, size))
    
    esp.nGoodEvents = 0
    roiMeans = [[] for i in esp.ROIs]
    pixelValues = [[] for i in esp.singlePixels]
    eventNumbers = []
    evtGen = esp.myrun.events()
    for nevt,evt in enumerate(evtGen):
        if evt is None:
            continue
        frames = esp.getRawData(evt, gainBitsMasked=True)
        if frames is None:
            ##print("no frame")
            continue

        eventNumbers.append(nevt)
        for i, roi in enumerate(esp.ROIs):
            m = frames[roi==1].mean()
            roiMeans[i].append(m)

        for i, roi in enumerate(esp.singlePixels):
            pixelValues[i].append(frames[tuple(esp.singlePixels[i])])

        parityTest = esp.getPingPongParity(frames[0][144:224, 0:80])
        print(frames[tuple(esp.singlePixels[0])], parityTest)
            
        smd.event(evt,
                  timestamps=evt.datetime().timestamp(),
                  rois=np.array([roiMeans[i][-1] for i in range(len(esp.ROIs))]),
                  pixels=np.array([pixelValues[i][-1] for i in range(len(esp.singlePixels))])
                  )
                  
        esp.nGoodEvents += 1
        if esp.nGoodEvents%100 == 0:
            print("n good events analyzed: %d" %(esp.nGoodEvents))

        if esp.nGoodEvents > esp.maxNevents:
            break

            
    np.save("%s/means_c%d_r%d_%s.npy" %(esp.outputDir, esp.camera, esp.run, esp.exp), np.array(roiMeans))
    np.save("%s/eventNumbers_c%d_r%d_%s.npy" %(esp.outputDir, esp.camera, esp.run, esp.exp), np.array(eventNumbers))
    esp.plotData(roiMeans, pixelValues, eventNumbers, "foo")

    ##if smd.summary:
    ##smd.save_summary(
    smd.done()
    
