##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import logging
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np

import calibrationSuite.ancillaryMethods as ancillaryMethods
import calibrationSuite.fitFunctions as fitFunctions
import calibrationSuite.loggingSetup as ls

##import sys
from calibrationSuite.argumentParser import ArgumentParser

# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(currFileName[:-3] + ".log", logging.INFO)  # change to logging.INFO for full logging output
# for logging from current file
logger = logging.getLogger(__name__)


class AnalyzeH5(object):
    def __init__(self):
        args = ArgumentParser().parse_args()

        self.run = args.run
        self.files = args.files.replace(" ", "")
        print(self.files)
        self.outputDir = args.path
        print("output dir:", self.outputDir)
        ##logging.info("Output dir: " + self.outputDir)
        self.label = args.label
        self.camera = 0
        self.seedCut = args.seedCut
        self.photonEnergy = args.photonEnergy
        self.isTestRun = args.special is not None and "testRun" in args.special

    def getFiles(self):
        fileNames = self.files.split(",")
        self.h5Files = []
        for f in fileNames:
            print("using file: ", f)
            self.h5Files.append(h5py.File(f))

    def identifyAnalysis(self):
        for key in ["analysis", "sliceCoordinates", "modules", "rows", "cols", "analyzedModules"]:
            if key not in self.h5Files[0]:
                print("h5 file missing metadata for key: '" + key + "'\nexiting...")
                exit(1)  # eventually try get this data from cmdline args?? or maybe have default vals to try with?

        encoding = "utf-8"

        # note: [()] is h5py way to access key's data

        # handle how some different machines create h5 differently
        try:
            bstring = self.h5Files[0]["analysis"][()][0]
            self.analysis = bstring.decode(encoding)
        except Exception:
            try:
                self.analysis = self.h5Files[0]["analysis"][()].decode(encoding)
            except Exception as e:
                print(f"failed to decode metadata value for key 'analysis': {e}")
                print("exiting...")
                exit(1)

        try:
            self.detModules = self.h5Files[0]["modules"][()][0]
            self.analyzedModules = self.h5Files[0]["analyzedModules"][()][0]
            self.detRows = self.h5Files[0]["rows"][()][0]
            self.detCols = self.h5Files[0]["cols"][()][0]
            self.sliceCoordinates = self.h5Files[0]["sliceCoordinates"][()][0]
        except Exception:
            ## seems to be needed for command-line analysis
            self.detModules = self.h5Files[0]["modules"][()]
            self.analyzedModules = self.h5Files[0]["analyzedModules"][()]
            self.detRows = self.h5Files[0]["rows"][()]
            self.detCols = self.h5Files[0]["cols"][()]
            self.sliceCoordinates = self.h5Files[0]["sliceCoordinates"][()]

        print("the following metadata was read from h5:")
        print("analysis: ", self.analysis)
        print("sliceCoordinates: ", self.sliceCoordinates)
        print("detModules: ", self.detModules)
        print("detRows: ", self.detRows)
        print("detCols: ", self.detCols)
        print("analyzedModules: ", self.analyzedModules)

    def sliceToDetector(self, sliceRow, sliceCol):
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

    def getRowsColsFromSliceCoordinates(self):
        offset = 0
        if len(self.sliceCoordinates) == 3:
            offset = 1
        self.rowStart = self.sliceCoordinates[offset][0]
        self.rowStop = self.sliceCoordinates[offset][1]
        self.colStart = self.sliceCoordinates[offset + 1][0]
        self.colStop = self.sliceCoordinates[offset + 1][1]
        rows = self.rowStop - self.rowStart
        cols = self.colStop - self.colStart
        print("analyzing %d rows, %d cols" % (rows, cols))

        return rows, cols

    def analyze(self):
        if self.analysis == "cluster":
            self.clusterAnalysis()
        elif self.analysis == "linearity":
            self.linearityAnalysis()
        else:
            print("unknown analysis type %s" % (self.analysis))
            logging.info("unknown analysis type %s" % (self.analysis))

    def clusterAnalysis(self):
        clusters = None
        energyHist = None
        clusters = np.concatenate([ancillaryMethods.getEnergeticClusters(h5["clusterData"][()]) for h5 in self.h5Files])
        ## getEnergeticClusters
        ## makes [events, maxClusters, nClusterElements] -> [m, n]
        ## makes memory violation a bit less likely too

        try:
            energyHist = np.concatenate(energyHist, [h5["energyHistogram"][()] for h5 in self.h5Files])
        except Exception:
            pass

        self.nBins = 200  ## for epixM with a lot of 2 photon events...

        if self.seedCut is None:
            self.lowEnergyCut = 4  ## fix - should be 0.5 photons or something
        else:
            self.lowEnergyCut = self.seedCut * 0.8  ## 0.8 is dumb here
        self.highEnergyCut = 15  ## fix - should be 1.5 photons or something
        if self.photonEnergy is not None:
            self.highEnergyCut = self.photonEnergy*1.5
        ##tmp
        npyFileName = "%s/r%d_clusters.npy" % (self.outputDir, self.run)
        np.save(npyFileName, clusters)
        ##logger.info("Wrote file: " + npyFileName)

        self.analyzeSimpleClusters(clusters)

        if energyHist is None:
            return

        minE, maxE = -5, 45
        if self.photonEnergy is not None:
            minE = -1*self.photonEnergy/2.
            maxE = self.photonEnergy*3
        
        _, bins = np.histogram(energyHist, 250, [minE, maxE])
        plt.hist(bins[:-1], bins, weights=energyHist)  ##, log=True)
        plt.grid(which="major", linewidth=0.5)
        plt.title = "All pixel energies in run after common mode correction"
        plt.xlabel = "energy (keV)"
        print("I hate matplotlib so much")

        figFileName = "%s/%s_r%d_c%d_%s_energyHistogram.png" % (
            self.outputDir,
            self.__class__.__name__,
            self.run,
            self.camera,
            self.label,
        )
        plt.savefig(figFileName)
        logger.info("Wrote file: " + figFileName)
        npyFileName = "%s/%s_r%d_c%d_%s_energyHistogram.npy" % (
            self.outputDir,
            self.__class__.__name__,
            self.run,
            self.camera,
            self.label,
        )
        np.save(npyFileName, energyHist)
        logger.info("Wrote file: " + npyFileName)
        plt.close()

    def analyzeSimpleClusters(self, clusters):
        ## v. sic.clusterElements = ["energy", "module", "row", "col", "nPixels", "isSquare"]
        ## should make a dict for this info and use below instead of indices

        ax = plt.subplot()
        energy = clusters[:, 0]  ##.flatten()
        ##maximumModule = int(clusters[:, 1].max())
        ##analyzedModules = np.unique(clusters[:, 1]).astype("int")

        rows, cols = self.getRowsColsFromSliceCoordinates()

        ##        ##cols = self.sliceEdges[1]
        ##        ## doesn't exist in h5 yet so calculate dumbly instead
        ##        rows = int(clusters[:, 2].max()) + 1
        ##        cols = int(clusters[:, 3].max()) + 1
        print("appear to have a slice with %d rows, %d cols" % (rows, cols))
        ##        self.sliceCoordinates = [[0, rows], [0, cols]]  ## temp - get from h5
        ##        self.sliceEdges = [rows, cols]

        print("mean energy above 0:" + str(energy[energy > 0].mean()))
        logger.info("mean energy above 0:" + str(energy[energy > 0].mean()))

        # foo = ax.hist(energy[energy > 0], 100)
        plt.xlabel = "energy (keV)"
        plt.title = "All pixels"
        figFileName = "%s/%s_r%d_c%d_%s_E.png" % (
            self.outputDir,
            self.__class__.__name__,
            self.run,
            self.camera,
            self.label,
        )
        plt.savefig(figFileName)
        logger.info("Wrote file: " + figFileName)
        plt.close()

        # verbose = False
        ##maximumModule = int(clusters[:, 1].max())
        ##fitInfo = np.zeros((maximumModule + 1, rows, cols, 5))  ## mean, std, area, mu, sigma
        fitInfo = np.zeros((self.detModules, self.detRows, self.detCols, 5))  ## mean, std, area, mu, sigma
        if False: ## turn on if one believes the baseline is right
            smallSquareClusters = ancillaryMethods.getSmallSquareClusters(clusters, nPixelCut=3)
        else:
            smallSquareClusters = clusters
        for m in self.analyzedModules:
            modClusters = ancillaryMethods.getMatchedClusters(smallSquareClusters, "module", m)
            for i in range(self.rowStart, self.rowStop):
                # just do a single row when testing
                if self.isTestRun and i > 0:
                    break

                rowModClusters = ancillaryMethods.getMatchedClusters(modClusters, "row", i)

                for j in range(self.colStart, self.colStop):
                    ##detRow, detCol = self.sliceToDetector(i, j)
                    detRow, detCol = i, j  ## mostly for clarity
                    currGoodClusters = ancillaryMethods.getMatchedClusters(rowModClusters, "column", j)
                    if len(currGoodClusters) < 5:
                        if i%10==0 and j%10==0:
                            print("too few clusters in slice pixel %d, %d, %d: %d" % (m, i, j, len(currGoodClusters)))
                            logger.info("too few clusters in slice pixel %d, %d, %d: %d" % (m, i, j, len(currGoodClusters)))
                        continue
                    energies = ancillaryMethods.getClusterEnergies(currGoodClusters)
                    photonEcut = np.bitwise_and(energies > self.lowEnergyCut, energies < self.highEnergyCut)
                    nPixelClusters = (photonEcut > 0).sum()
                    print("pixel %d,%d,%d has about %d photons" % (m, i, j, nPixelClusters))
                    logger.info("pixel %d,%d,%d has about %d photons" % (m, i, j, nPixelClusters))
                    photonRegion = energies[photonEcut]
                    mean = photonRegion.mean()
                    std = photonRegion.std()
                    ax = plt.subplot()
                    a, mu, sigma = self.histogramAndFitGaussian(ax, energies, self.nBins)
                    area = fitFunctions.gaussianArea(a, sigma)
                    fitInfo[m, i, j] = mean, std, area, mu, sigma
                    if i % 13 == 1 and j % 17 == 1:
                        ## don't save a zillion plots when analyzing full array
                        ## should add singlePixelArray here
                        ax.set_xlabel("energy (keV)")
                        ax.set_title("pixel %d,%d,%d, small cluster cuts" % (m, detRow, detCol))
                        plt.figtext(0.7, 0.8, "%d entries (peak)" % (area))
                        plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
                        plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
                        figFileName = "%s/%s_r%d_c%d_m%d_r%d_c%d_%s_E.png" % (
                            self.outputDir,
                            self.__class__.__name__,
                            self.run,
                            self.camera,
                            m,
                            detRow,
                            detCol,
                            self.label,
                        )
                        plt.savefig(figFileName)
                        logger.info("Wrote file: " + figFileName)
                    plt.close()

        npyFileName = "%s/%s_r%d_c%d_%s_fitInfo.npy" % (
            self.outputDir,
            self.__class__.__name__,
            self.run,
            self.camera,
            self.label,
        )
        np.save(npyFileName, fitInfo)
        logger.info("Wrote file: " + npyFileName)

        gains = fitInfo[:, :, 3]
        maxE = 15
        if self.photonEnergy is not None:
            maxE = self.photonEnergy*2
        goodGains = gains[np.bitwise_and(gains > 0, gains < maxE)]
        ax = plt.subplot()
        ax.hist(goodGains, 100)
        ax.set_xlabel("energy (keV)")
        ax.set_title("pixel single photon fitted energy")
        figFileName = "%s/%s_r%d_c%d_%s_gainDistribution.png" % (
            self.outputDir,
            self.__class__.__name__,
            self.run,
            self.camera,
            self.label,
        )
        plt.savefig(figFileName)

    def histogramAndFitGaussian(self, ax, energies, nBins):
        y, bin_edges, _ = ax.hist(energies, nBins)
        bins = (bin_edges[:-1] + bin_edges[1:]) / 2
        a, mean, std = fitFunctions.estimateGaussianParametersFromUnbinnedArray(energies)
        try:
            popt, pcov = fitFunctions.curve_fit(fitFunctions.gaussian, bins, y, [a, mean, std])
            # mu = popt[1]
            # sigma = popt[2]
            fittedFunc = fitFunctions.gaussian(bins, *popt)
            ax.plot(bins, fittedFunc, color="b")
            return popt
        except Exception:
            return 0, 0, 0

    def linearityAnalysis(self):
        fluxes = np.concatenate([h5["fluxes"][()] for h5 in self.h5Files])
        rois = np.concatenate([h5["rois"][()] for h5 in self.h5Files])
        someSinglePixels = np.concatenate([h5["pixels"][()] for h5 in self.h5Files])
        slice = np.concatenate([h5["slice"][()] for h5 in self.h5Files])
        self.singlePixels = [[0, 66, 66], [0, 6, 6]]
        print("load temporary fake pixels")


if __name__ == "__main__":
    ah5 = AnalyzeH5()
    ah5.getFiles()
    ah5.identifyAnalysis()
    ah5.analyze()
