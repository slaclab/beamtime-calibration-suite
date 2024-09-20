##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

import calibrationSuite.fitFunctions as fitFunctions
from calibrationSuite.basicSuiteScript import BasicSuiteScript
from calibrationSuite.cluster import BuildClusters


class SimpleClusters(BasicSuiteScript):
    def __init__(self):
        super().__init__("lowFlux")  ##self)

    def plotData(self, clusters, label):
        ax = plt.subplot()
        energy = clusters[:, :, 0]  ##.flatten()
        ## foo = ax.hist(energy[energy > 0], 100)
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
                pixelEcut0 = np.bitwise_and(
                    smallPixel, energy > sic.seedCut * 0.8
                )  ## adjusted due to gains not making sense
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
                    except Exception:
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
        ## simpleClusters = data["clusterData"][()]
        ## self.plotData(simpleClusters, label)
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
    sic.configHash["analysis"] = "cluster"
    
    print("analyzed modules:", sic.analyzedModules) ## move this to psana setup
    size = 666
    filename="%s/%s_%s_c%d_r%d_n%d.h5" % (sic.outputDir, sic.className, sic.label, sic.camera, sic.run, size)
    if sic.psanaType==1:
        smd = sic.ds.small_data(filename=filename, gather_interval=100)
    else:
        smd = sic.get_smalldata(filename=filename)

    ## 50x50 pixels, 3x3 clusters, 10% occ., 2 sensors
    maxClusters = 10000  ##int(50 * 50 / 3 / 3 * 0.1 * 2)
    if sic.seedCut is not None:
        seedCut = sic.seedCut
    else:
        try:
            seedCut = sic.detectorInfo.seedCut
        except Exception:
            seedCut = 4
    try:
        neighborCut = sic.detectorInfo.neighborCut
    except Exception:
        neighborCut = 0.5

    print("using seed, neighbor cuts", seedCut, neighborCut)

    sic.clusterElements = ["energy", "module", "row", "col", "nPixels", "isSquare"]
    nClusterElements = len(sic.clusterElements)

    ## sic.slices = [np.s_[0:100, 0:100], np.s_[200:300, 200:300]] ## fix this
    ## sic.slices = [np.s_[0:288, 0:384]]
    ## sic.slices = [np.s_[270:288, 59:107]]

    sic.useFlux = False

    sic.nGoodEvents = 0
    if sic.useFlux:
        evtGen = sic.matchedDetEvt()
    else:
        try:
            evtGen = sic.myrun.events()
        except:
            ##if sic.psanaType == 1: ## fix in base class asap
            evtGen = sic.ds.events()
        
    pedestal = None
    nComplaints = 0
    try:
        gain = sic.aduPerKeV
    except Exception:
        gain = None
    if sic.special is not None:  ## and 'fakePedestal' in sic.special:
        if "FH" in sic.special:
            gain = 20  ##17.## my guess
        elif "FM" in sic.special:
            gain = 6.66  # 20/3
        print("using gain correction", gain)

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
        except Exception:
            print("May not have a detector object in this data stream...")
            print("sic.det:", sic.det)
            pass

    zeroLowGain = False
    if sic.special and "zeroLowGain" in sic.special:
        zeroLowGain = True
        
    useSlice = False
    if sic.special is not None and "slice" in sic.special:
        useSlice = True
    
    hSum = None
    ##sic.commonModeVals = []

    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
        if not sic.fakeBeamCode and not sic.isBeamEvent(evt):
            continue

        if zeroLowGain:
            rawFrames = sic.getRawData(evt, gainBitsMasked=False)
        else:
            rawFrames = sic.getRawData(evt)

        if rawFrames is None:
            continue
        if zeroLowGain:
            g1 = rawFrames >= sic.g0cut

        frames = None
        if sic.fakePedestal is not None:
            frames = rawFrames.astype("float") - sic.fakePedestal
            if zeroLowGain:
                frames[g1] = 0
        elif pedestal is not None:
            frames = rawFrames.astype("float") - pedestal
            if zeroLowGain:
                frames[g1] = 0
        ##else:
        ##print("something is probably wrong, need a pedestal to cluster")
        ##sys.exit(0)

        ##print("frames and gain:", frames, gain)
        if frames is not None and gain is not None:
            if sic.special is not None and "addFakePhotons" in sic.special:
                frames, nAdded = sic.addFakePhotons(frames, 0.01, 666 * 10, 10)
                print("added %d fake photons" % (nAdded))
            frames /= gain  ## this helps with the bit shift
        else:
            frames = sic.getCalibData(evt)
        if frames is None:
            print("something weird and bad happened, ignore event %d" %(nevt))
            continue

        if sic.special is not None:
            if "regionCommonMode" in sic.special:
                frames = sic.regionCommonModeCorrection(frames, sic.regionSlice, 2.0)
            if "rowCommonMode" in sic.special:
                frames = sic.rowCommonModeCorrection3d(frames, 3.0)
            if "colCommonMode" in sic.special:
                frames = sic.colCommonModeCorrection3d(frames, 3.0) ## don't hard code this - fix...

        if frames is None:
            print("common mode killed frames???")
            raise Exception

        ## temp fix for 2d case (epix100, rixsCCD)
        if sic.detectorInfo.dimension == 2:
            frames = np.array([frames])
            
        try: ## added for psana1 - should fix in base class
            flux = sic.flux
        except:
            flux = None
        if sic.useFlux and flux is None:
            continue
        if sic.threshold is not None and flux > sic.threshold:
            if nComplaints < 10:
                print("flux is above threshold:", flux, sic.threshold, 10 - nComplaints)
            nComplaints += 1
            continue

        ## histogram frame to check pedestal
        h, _ = np.histogram(frames[sic.regionSlice], 250, [-5, 45])
        try:
            hSum += h
        except Exception:
            hSum = np.array(h)  ##.astype(np.uint32)

        nClusters = 0
        clusterArray = np.zeros((maxClusters, nClusterElements))
        for module in sic.analyzedModules:
            if nClusters == maxClusters:
                continue
            if useSlice:
                if sic.detectorInfo.dimension == 2: ## figure out how to kill if
                    bc = BuildClusters(frames[module][sic.regionSlice], seedCut, neighborCut)
                elif sic.detectorInfo.dimension == 3:
                    bc = BuildClusters(frames[sic.regionSlice][module], seedCut, neighborCut)
            else:
                bc = BuildClusters(frames[module], seedCut, neighborCut)

            fc = bc.findClusters()
            if False:
                print(
                    "found %d prospective clusters" % (len(fc)), bc.frame.max(), frames[sic.regionSlice][module].max()
                )

            for c in fc:
                ##print(c.goodCluster, c.nPixels, c.eTotal)
                if c.goodCluster and c.nPixels < 6 and nClusters < maxClusters:
                    sr = c.seedRow
                    sc = c.seedCol
                    if useSlice:
                        sr, sc = sic.sliceToDetector(sr, sc)
                    clusterArray[nClusters] = [c.eTotal, module, sr, sc, c.nPixels, c.isSquare()]
                    nClusters += 1
                if nClusters == maxClusters:
                    print("have found %d clusters, mean energy:" % (maxClusters), np.array(clusterArray)[:, 0].mean())
                    ## had continue here
                    break

        if nevt%1000 == 0:
            print("event %d, found %d clusters" %(nevt, nClusters))
            
        if sic.psanaType==1:
            smd.event(clusterData=clusterArray)
        else:
            smd.event(evt, clusterData=clusterArray)

        sic.nGoodEvents += 1
        if sic.nGoodEvents == sic.maxNevents:
            print("have reached max n events %d, quitting" %(sic.maxNevents))
            break
            
        if sic.nGoodEvents % 1000 == 0:
            print("n good events analyzed: %d, clusters this event: %d" % (sic.nGoodEvents, nClusters))
            
            if sic.detectorInfo.dimension == 3:
                f = frames[sic.regionSlice]
            elif sic.detectorInfo.dimension == 2:
                f = frames[sic.analyzedModules[0]]
            print(
                "slice or module median, max, guess at single photon, guess at zero photon:",
                np.median(f),
                f.max(),
                np.median(f[f > 4]),
                np.median(f[f < 2]),
            )

    ## np.save("%s/means_c%d_r%d_%s.npy" %(sic.outputDir, sic.camera, sic.run, sic.exp), np.array(roiMeans))
    ## np.save("%s/eventNumbers_c%d_r%d_%s.npy" %(sic.outputDir, sic.camera, sic.run, sic.exp), np.array(eventNumbers))
    ## sic.plotData(roiMeans, pixelValues, eventNumbers, "foo")

    if sic.psanaType==1 or smd.summary:
        ## guess at desired psana1 behavior - no smd.summary there
        ## maybe check smd.rank == 0?
        sumhSum = smd.sum(hSum)
        if sic.psanaType==1:
            smd.save({"energyHistogram": sumhSum})
            smd.save(sic.configHash)
        else:
            smd.save_summary({"energyHistogram": sumhSum})
            smd.save_summary(sic.configHash)

    if sic.psanaType != 1:
        ## need to figure out how to hide the smalldata differences
        ## unless we have to make new classes to wrap it
        smd.done()

    sic.dumpEventCodeStatistics()
