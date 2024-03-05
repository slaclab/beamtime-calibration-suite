import h5py
import numpy as np
import calibrationSuite.fitFunctions as fitFunctions
import calibrationSuite.ancillaryMethods as ancillaryMethods

##import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

##import sys
import argparse
from calibrationSuite.argumentParser import ArgumentParser

import logging

# for logging from current file
logger = logging.getLogger(__name__)

import calibrationSuite.loggingSetup as ls
import os

# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(currFileName[:-3] + ".log", logging.ERROR)  # change to logging.INFO for full logging output


class AnalyzeH5(object):
    def __init__(self):
        print("in init")

        args = ArgumentParser().parse_args()

        self.run = args.run
        self.files = args.files.replace(" ", "")
        print(self.files)
        self.outputDir = args.path
        logging.info("Output dir: " + self.outputDir)
        self.label = args.label
        self.camera = 0

    def getFiles(self):
        fileNames = self.files.split(",")
        self.h5Files = []
        for f in fileNames:
            print(f)
            self.h5Files.append(h5py.File(f))

    def identifyAnalysis(self):
        try:
            self.analysisType = self.h5Files[0]["analysisType"]
            self.sliceCoordinates = self.h5Files[0]["sliceCoordinates"][()]
        except:
            ## do something useful here, maybe
            self.analysisType = None
            ## but for now
            self.analysisType = "cluster"
            self.sliceCoordinates = [[270, 288], [59, 107]]
            self.sliceEdges = [288 - 270, 107 - 59]

    def sliceToDetector(self, sliceRow, sliceCol):
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

    def analyze(self):
        if self.analysisType == "cluster":
            self.clusterAnalysis()
        else:
            print("unknown analysis type %s" % (self.analysisType))
            logging.info("unknown analysis type %s" % (self.analysisType))

    def clusterAnalysis(self):
        clusters = None
        energyHist = None
        clusters = np.concatenate([h5["clusterData"][()] for h5 in self.h5Files])
        try:
            energyHist = np.concatenate(energyHist, h5["energyHistogram"][()])
        except:
            pass

        self.nBins = 100
        self.lowEnergyCut = 1  ## fix - should be 0.5 photons or something
        self.highEnergyCut = 10  ## fix - should be 1.5 photons or something
        ##tmp
        npyFileName = "%s/r%d_clusters.npy" % (self.outputDir, self.run)
        np.save(npyFileName, clusters)
        logger.info("Wrote file: " + npyFileName)

        self.analyzeSimpleClusters(clusters)

        if energyHist is None:
            return

        _, bins = np.histogram(energyHist, 250, [-5, 45])
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
        ax = plt.subplot()
        energy = clusters[:, :, 0]  ##.flatten()
        ##energy *= 2 ## temporary, due to bit shift
        ##print(energy[energy>0][666:777])
        print("mean energy above 0:" + str(energy[energy > 0].mean()))
        logger.info("mean energy above 0:" + str(energy[energy > 0].mean()))

        foo = ax.hist(energy[energy > 0], 100)
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

        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        fitInfo = np.zeros((rows, cols, 5))  ## mean, std, area, mu, sigma
        for i in range(rows):
            for j in range(cols):
                detRow, detCol = self.sliceToDetector(i, j)
                ax = plt.subplot()
                currGoodClusters = ancillaryMethods.goodClusters(clusters, i, j, nPixelCut=4, isSquare=1)
                if len(currGoodClusters) < 5:
                    print("too few clusters in slice pixel %d, %d: %d" % (i, j, len(currGoodClusters)))
                    logger.info("too few clusters in slice pixel %d, %d: %d" % (i, j, len(currGoodClusters)))
                    continue
                energies = ancillaryMethods.getClusterEnergies(currGoodClusters)
                photonEcut = np.bitwise_and(energies > self.lowEnergyCut, energies < self.highEnergyCut)
                nPixelClusters = (photonEcut > 0).sum()
                print("pixel %d,%d has about %d photons" % (i, j, nPixelClusters))
                logger.info("pixel %d,%d has about %d photons" % (i, j, nPixelClusters))
                photonRegion = energies[photonEcut]
                mean = photonRegion.mean()
                std = photonRegion.std()
                a, mu, sigma = self.histogramAndFitGaussian(ax, energies, self.nBins)
                area = fitFunctions.gaussianArea(a, sigma)
                ax.set_xlabel("energy (keV)")
                ax.set_title("pixel %d,%d, small cluster cuts" % (detRow, detCol))
                plt.figtext(0.7, 0.8, "%d entries (peak)" % (area))
                plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
                plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
                figFileName = "%s/%s_r%d_c%d_r%d_c%d_%s_E.png" % (
                    self.outputDir,
                    self.__class__.__name__,
                    self.run,
                    self.camera,
                    detRow,
                    detCol,
                    self.label,
                )
                plt.savefig(figFileName)
                logger.info("Wrote file: " + figFileName)
                plt.close()

                npyFileName = "%s/%s_r%d_c%d_r%d_c%d_%s_fitInfo.npy" % (
                    self.outputDir,
                    self.__class__.__name__,
                    self.run,
                    self.camera,
                    detRow,
                    detCol,
                    self.label,
                )
                np.save(npyFileName, fitInfo)
                logger.info("Wrote file: " + npyFileName)
                fitInfo[i, j] = mean, std, area, mu, sigma

        gains = fitInfo[:, :, 3]
        goodGains = gains[np.bitwise_and(gains > 0, gains < 15)]
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
        ##print(y, bins)
        a, mean, std = fitFunctions.estimateGaussianParametersFromUnbinnedArray(energies)
        try:
            popt, pcov = fitFunctions.curve_fit(fitFunctions.gaussian, bins, y, [a, mean, std])
            mu = popt[1]
            sigma = popt[2]
            fittedFunc = fitFunctions.gaussian(bins, *popt)
            ax.plot(bins, fittedFunc, color="b")
            return popt
        except:
            return 0, 0, 0


if __name__ == "__main__":
    ah5 = AnalyzeH5()
    ah5.getFiles()
    ah5.identifyAnalysis()
    ah5.analyze()
