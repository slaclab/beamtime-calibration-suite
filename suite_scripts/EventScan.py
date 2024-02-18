from calibrationSuite.basicSuiteScript import *
##from fitFineScan import *

class EventScan(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        
    def plotData(self, data, pixels, eventNumbers, label):
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(eventNumbers,data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.5)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel('Event number (decimal)')
            plt.ylabel('Mean (ADU)')
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.savefig("%s/%s_r%d_c%d_%s_ROI%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
            plt.clf()
            
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(eventNumbers, data[i], label=self.ROIfileNames[i])
            plt.grid(which='major',linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which='minor', linewidth=0.5)
            plt.xlabel('EventNumber (decimal)')
            plt.ylabel('Mean (ADU)')
            ##plt.yscale('log')
            plt.legend(loc='upper right')
        plt.savefig("%s/%s_r%d_c%d_%s_All%d.png" %(self.outputDir,self.__class__.__name__, self.run, self.camera, label, i))
        plt.clf()
        # plt.show()

        for i, p in enumerate(self.singlePixels):
            ax = plt.subplot()
            ax.plot(eventNumbers, pixels[i], label=str(p))
            plt.xlabel('Event number')
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
    
if __name__ == "__main__":
    esr = EventScan()
    print("have built a", esr.className, "class")
    esr.setupPsana()
    esr.nGoodEvents = 0
    roiMeans = [[] for i in esr.ROIs]
    pixelValues = [[] for i in esr.singlePixels]
    eventNumbers = []
    evtGen = esr.myrun.events()
    for nevt,evt in enumerate(evtGen):
        if evt is None:
            continue
        frames = esr.getRawData(evt, gainBitsMasked=True)
        if frames is None:
            ##print("no frame")
            continue

        eventNumbers.append(nevt)
        for i, roi in enumerate(esr.ROIs):
            m = frames[roi==1].mean()
            roiMeans[i].append(m)

        for i, roi in enumerate(esr.singlePixels):
            pixelValues[i].append(frames[tuple(esr.singlePixels[i])])

        esr.nGoodEvents += 1
        if esr.nGoodEvents%100 == 0:
            print("n good events analyzed: %d" %(esr.nGoodEvents))

        if esr.nGoodEvents > esr.maxNevents:
            break

            
    np.save("%s/means_c%d_r%d_%s.npy" %(esr.outputDir, esr.camera, esr.run, esr.exp), np.array(roiMeans))
    np.save("%s/eventNumbers_c%d_r%d_%s.npy" %(esr.outputDir, esr.camera, esr.run, esr.exp), np.array(eventNumbers))
    esr.plotData(roiMeans, pixelValues, eventNumbers, "foo")
    
