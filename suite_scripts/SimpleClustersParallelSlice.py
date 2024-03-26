##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from calibrationSuite.basicSuiteScript import *
from calibrationSuite.cluster import Cluster, BuildClusters


class SimpleClusters(BasicSuiteScript):
    def __init__(self):
        super().__init__("lowFlux")  ##self)

    def plotData(self, clusters, label):
        ax = plt.subplot()
        energy = clusters[:, :, 0]  ##.flatten()
        foo = ax.hist(energy[energy > 0], 100)
        plt.xlabel = "energy (keV)"
        plt.title = "All pixels"
        plt.savefig("%s/%s_r%d_c%d_%s_E.png" % (self.outputDir, self.__class__.__name__, self.run, self.camera, label))
        plt.close()

        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        fitInfo = np.zeros((rows, cols, 4))  ## mean, std, mu, sigma
        for i in range(rows):
            for j in range(cols):
                pixel = np.bitwise_and((clusters[:, :, 1] == i), (clusters[:, :, 2] == j))
                small = np.bitwise_and((clusters[:, :, 3] < 4), (clusters[:, :, 4] == 1))
                smallPixel = np.bitwise_and(small, pixel)
                pixelEcut0 = np.bitwise_and(smallPixel, energy > 4)  ## adjusted due to gains not making sense
                pixelEcut = np.bitwise_and(
                    pixelEcut0, energy < 20
                )  ## would be good to get rid of these entirely when things make sense
                nPixelClusters = (pixelEcut > 0).sum()
                mean = std = mu = sigma = 0
                pixelE = energy[pixelEcut > 0]
                if nPixelClusters > 5:
                    print("pixel %d,%d has %d photons" % (i, j, nPixelClusters))
                    ax = plt.subplot()
                    y, bin_edges, _ = ax.hist(pixelE, 100)
                    bins = (bin_edges[:-1] + bin_edges[1:]) / 2
                    ##print(y, bins)
                    mean, std = fitFunctions.estimateGaussianParameters(pixelE)
                    try:
                        popt, pcov = curve_fit(fitFunctions.gaussian, bins, y, [3, mean, std])
                        mu = popt[1]
                        sigma = popt[2]
                        fitInfo[i, j] = (mean, std, popt[1], popt[2])
                        fittedFunc = fitFunctions.gaussian(bins, *popt)
                        ax.plot(bins, fittedFunc, color="b")
                    except:
                        pass
                    ax.set_xlabel("energy (keV)")
                    ax.set_title("pixel %d,%d in slice, small cluster cuts" % (i, j))
                    plt.figtext(0.7, 0.8, "%d entries" % (nPixelClusters))
                    plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
                    plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
                    plt.savefig(
                        "%s/%s_r%d_c%d_r%d_c%d_%s_E.png"
                        % (self.outputDir, self.__class__.__name__, self.run, self.camera, i, j, label)
                    )
                    plt.close()

        np.save(
            "%s/%s_r%d_c%d_r%d_c%d_%s_fitInfo.npy"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, i, j, label),
            fitInfo,
        )
        gains = fitInfo[:, :, 2]
        goodGains = gains[np.bitwise_and(gains > 0, gains < 30)]
        ax = plt.subplot()
        ax.hist(goodGains, 100)
        ax.set_xlabel("energy (keV)")
        ax.set_title("pixel single photon fitted energy")
        plt.savefig(
            "%s/%s_r%d_c%d_%s_gainDistribution.png"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, label)
        )

    def analyze_h5(self, dataFile, label):
        import h5py

        data = h5py.File(dataFile)
        simpleClusters = data["clusterData"][()]
        ##self.plotData(simpleClusters, label)
        energyHist = data["energyHistogram"][()]
        _, bins = np.histogram(energyHist, 250, [-5, 45])
        plt.hist(bins[:-1], bins, weights=energyHist)  ##, log=True)
        plt.grid(which="major", linewidth=0.5)
        plt.title = "All pixel energies in run after common mode correction"
        plt.xlabel = "energy (keV)"
        print("I hate matplotlib so much")
        plt.savefig(
            "%s/%s_r%d_c%d_%s_energyHistogram.png"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, label)
        )
        np.save(
            "%s/%s_r%d_c%d_%s_energyHistogram.npy"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, label),
            energyHist,
        )
        plt.close()
        plt.hist(bins[:-1], bins, weights=energyHist, log=True)
        plt.grid(which="major", linewidth=0.5)
        plt.title = "All pixel energies in run after common mode correction"
        plt.xlabel = "energy (keV)"
        print("I hate matplotlib so much")
        plt.savefig(
            "%s/%s_r%d_c%d_%s_energyHistogramLog.png"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, label)
        )


if __name__ == "__main__":
    sic = SimpleClusters()
    print("have built a", sic.className, "class")
    if sic.file is not None:
        sic.analyze_h5(sic.file, sic.label)
        print("done with standalone analysis of %s, exiting" % (sic.file))
        sys.exit(0)

    sic.setupPsana()
    smd = sic.ds.smalldata(filename="%s/%s_c%d_r%d_n%d.h5" % (sic.outputDir, sic.className, sic.camera, sic.run, size))

    ## 50x50 pixels, 3x3 clusters, 10% occ., 2 sensors
    maxClusters = int(50 * 50 / 3 / 3 * 0.1 * 2)
    seedCut = 4
    neighborCut = 0.5
    sic.clusterElements = ["energy", "row", "col", "nPixels", "isSquare"]
    nClusterElements = len(sic.clusterElements)

    ##sic.slices = [np.s_[0:100, 0:100], np.s_[200:300, 200:300]] ## fix this
    ##sic.slices = [np.s_[0:288, 0:384]]
    ##sic.slices = [np.s_[270:288, 59:107]]

    sic.useFlux = False

    sic.nGoodEvents = 0
    if sic.useFlux:
        evtGen = sic.matchedDetEvt()
    else:
        evtGen = sic.myrun.events()

    pedestal = None
    nComplaints = 0
    gain = None
    if sic.special is not None:  ## and 'fakePedestal' in sic.special:
        if "FH" in sic.special:
            gain = 20  ##17.## my guess
        elif "FM" in sic.special:
            gain = 6.66  # 20/3
        print("using gain correction", gain)

        ##if True:  ## turn on when db works
        try:
            if "FH" in sic.special:
                gainMode = sic.gainModes["FH"]
            if "FM" in sic.special:
                gainMode = sic.gainModes["FM"]
            print("you have decided this is gain mode %d" % (gainMode))
            pedestal = sic.det.calibconst["pedestals"][0][gainMode]
            if gain is None:
                gain = sic.det.calibconst["pedestals"][0][gainMode]
                ## something wrong with the overall logic here
        except:
            print("May not have a detector object in this data stream...")
            print("sic.det:", sic.det)
            pass

    hSum = None
    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
        if not sic.isBeamEvent(evt):
            continue

        rawFrames = sic.getRawData(evt)
        if rawFrames is None:
            continue

        frames = None
        if sic.fakePedestal is not None:
            frames = rawFrames.astype("float") - sic.fakePedestalFrame
        elif pedestal is not None:
            frames = rawFrames.astype("float") - pedestal
        if frames is not None and gain is not None:
            frames /= gain  ## this helps with the bit shift
        else:
            frame = sic.getCalibData(evt)[0]
        if frames is None:
            print("something weird and bad happened, ignore event")
            continue
        frame = frames[0]
        ## in keV now, hopefully with a sensible pedestal

        if sic.special is not None:
            if "regionCommonMode" in sic.special:
                frame = sic.regionCommonModeCorrection(frame, sic.regionSlice, 2.0)
            if "rowCommonMode" in sic.special:
                frame = sic.rowCommonModeCorrection(frame, 2.0)
            if "colCommonMode" in sic.special:
                frame = sic.colCommonModeCorrection(frame, 2.0)

        if frame is None:
            ##print("no frame")
            continue
        flux = sic.flux
        if sic.useFlux and flux is None:
            continue
        if sic.threshold is not None and flux > sic.threshold:
            if nComplaints < 10:
                print("flux is above threshold:", flux, sic.threshold, 10 - nComplaints)
            nComplaints += 1
            continue

        ## histogram frame to check pedestal
        h, _ = np.histogram(frame[sic.regionSlice], 250, [-5, 45])
        try:
            hSum += h
        except:
            hSum = np.array(h)  ##.astype(np.uint32)

        nClusters = 0
        clusterArray = np.zeros((maxClusters, nClusterElements))
        bc = BuildClusters(frame[sic.regionSlice], seedCut, neighborCut)
        fc = bc.findClusters()

        for c in fc:
            ##print(nClusters)
            if c.goodCluster and c.nPixels < 6 and nClusters < maxClusters:
                clusterArray[nClusters] = [c.eTotal, c.seedRow, c.seedCol, c.nPixels, c.isSquare()]
                nClusters += 1
            if nClusters == maxClusters:
                print("have found %d clusters, mean energy:" % (maxClusters), np.array(clusterArray)[:, 0].mean())
                ##print(frame)
                continue

        smd.event(evt, clusterData=clusterArray)

        sic.nGoodEvents += 1
        if sic.nGoodEvents % 1000 == 0:
            print("n good events analyzed: %d, clusters this event: %d" % (sic.nGoodEvents, nClusters))
            f = frame[sic.regionSlice]
            print(
                "slice median, max, guess at single photon, guess at zero photon:",
                np.median(f),
                f.max(),
                np.median(f[f > 4]),
                np.median(f[f < 2]),
            )

    ##    np.save("%s/means_c%d_r%d_%s.npy" %(sic.outputDir, sic.camera, sic.run, sic.exp), np.array(roiMeans))
    ##    np.save("%s/eventNumbers_c%d_r%d_%s.npy" %(sic.outputDir, sic.camera, sic.run, sic.exp), np.array(eventNumbers))
    ##    sic.plotData(roiMeans, pixelValues, eventNumbers, "foo")

    if smd.summary:
        sumhSum = smd.sum(hSum)
        smd.save_summary({"energyHistogram": sumhSum})
    smd.done()

    sic.dumpEventCodeStatistics()
