##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import matplotlib.pyplot as plt
import numpy as np
import sys
import re
import logging
import os
import calibrationSuite.loggingSetup as ls
# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging("../logs/" + currFileName[:-3] + ".log", logging.INFO)  # change to logging.INFO for full logging output


runInfoDict = {'591':'AML 2500', '638':'AML 120'}


class LinearityInfo(object):  ## describes the .npy array
    def __init__(self):
        self.dataIndices = {
            "g0slope": 0,
            "g0intercept": 1,
            "g0r2": 2,
            "g1slope": 3,
            "g1intercept": 4,
            "g1r2": 5,
            "g0max": 6,
            "g1min": 7,
            "min": 8,
            "max": 9,
            "g0Ped": 10,
            "g1Ped": 11,
            "g0Gain": 12,
            "offset": 13
        }
        self.dataRanges = {  ##"g0slope":[0,1000],
            "g0slope": [0, 5],
            "g0intercept": [0, 10000],
            "g0r2": [0.9, 1.0],
            "g1slope": [0, 0.1],
            "g1intercept": [0, 10000],
            "g1r2": [0.9, 1.0],
            "g0max": [10000, 16384],
            "g1min": [0, 16384],
        }


class AnalyzeOneScan(object):
    def __init__(self, scanObj, statsArray, data, module, label, ratio=False):
        self.data = data[module]
        self.label = label
        self.ratio = ratio
        self.statsArray = statsArray

        self.dataIndices = scanObj.dataIndices
        self.dataRanges = scanObj.dataRanges

    def analyze(self):
        if self.ratio:
            for array in self.statsArray:
                self.plotRatio(*tuple(array))
        else:
            for array in self.statsArray:
                if len(array) == 2:
                    self.analyzePairs(array)
                else:
                    self.plotStat(*tuple(array))

    def analyzePairs(self, statsArray):
        self.plotPair(*tuple(statsArray))

    ##    def analyzeRatio(self)
    ##        self.plotRatio("g1slope", "g0slope", clipRange=[0, 0.05])

    def plotStat(self, stat0):
        ##return
        g0Range = self.dataRanges[stat0]
        g0Index = self.dataIndices[stat0]

        fig, ax = plt.subplots(2, 1)
        d = self.data[:, :, g0Index]
        print(stat0, "median:", np.median(d))
        im = ax[0].imshow(d.clip(*tuple(g0Range)))
        fig.colorbar(im)
        ax[0].set_title(stat0)
        ax[1].hist(d.clip(*tuple(g0Range)), 100)
        ax[1].set_title(stat0)

        figFileName = "%s_%s_map_and_histo.png" % (self.label, stat0, stat1)
        plt.savefig(figFileName)
        plt.close()

    def plotPair(self, stat0, stat1):
        ##return
        g0Range = self.dataRanges[stat0]
        g1Range = self.dataRanges[stat1]
        g0Index = self.dataIndices[stat0]
        g1Index = self.dataIndices[stat1]

        fig, ax = plt.subplots(2, 2)
        d = self.data[:, :, g0Index]
        print(stat0, "median:", np.median(d))
        logger.info(str(stat0) + " median: " + str(np.median(d)))

        im = ax[0, 0].imshow(d.clip(*tuple(g0Range)))
        fig.colorbar(im)
        ax[0, 0].set_title(stat0)
        ax[0, 1].hist(d.clip(*tuple(g0Range)), 100)
        ax[0, 1].set_title(stat0)
        d = self.data[:, :, g1Index]
        print(stat1, "median:", np.median(d))
        logger.info(str(stat1) + " median: " + str(np.median(d)))

        im = ax[1, 0].imshow(d.clip(*tuple(g1Range)))
        fig.colorbar(im)
        ax[1, 0].set_title(stat1)
        ax[1, 1].hist(d.clip(*tuple(g1Range)), 100)
        ax[1, 1].set_title(stat1)
        ##plt.show()

        figFileName = "%s_%s_%s_maps_and_histos.png" % (self.label, stat0, stat1)
        plt.savefig(figFileName)
        logger.info("Wrote file: " + figFileName)
        plt.close()

    def plotRatio(self, statA, statB, clipRange=None):
        ##g0Range = self.dataRanges[stat0]
        ##g1Range = self.dataRanges[stat1]
        indexA = self.dataIndices[statA]
        indexB = self.dataIndices[statB]
        fig, ax = plt.subplots(2, 1)
        d = self.data[:, :, indexA] / self.data[:, :, indexB]
        
        print(statA, statB, "ratio median:", np.median(d))
        logger.info(str(statA) + " " + str(statB) + " ratio median: " + " " + str(np.median(d)))

        if clipRange is not None:
            d = d.clip(*tuple(clipRange)) #???
        ##im = ax[0,0].imshow(d.clip(*tuple(g0Range)))
        im = ax[0].imshow(d)
        fig.colorbar(im)
        ax[0].set_title("%s/%s" % (statA, statB))
        ax[1].hist(d, 100)
        ax[1].set_title("%s/%s" % (statA, statB))

        figFileName = "%s_%s_%s_ratio_map_and_histo.png" % (self.label, statA, statB)
        plt.savefig(figFileName)
        logger.info("Wrote file: " + figFileName)
        plt.close()


class CompareMultipleScans(object):
    def __init__(self, scanObj, statsArray, dataArray, runList, label):
        self.statsArray = statsArray
        self.dataArray = dataArray
        self.runList = runList
        self.label = label
        print("label: %s" % (label))
        logger.info("label: %s" % (label))
        self.dataIndices = scanObj.dataIndices
        self.dataRanges = scanObj.dataRanges
        print(self.dataIndices)
        logger.info(self.dataIndices)

    def overlayHistograms(self, statList, nBins=50):
        if len(statList) > 1:
            fig, ax = plt.subplots(len(statList), 1)
        else:
            fig, ax = plt.subplots(len(statList), 1)
            ax = [ax]  ## must be a smarter way to generalize here

        for i, stat in enumerate(statList):
            index = self.dataIndices[stat]
            print(label)
            print(index, stat)
            print(self.runList)
            for j in range(len(self.runList)):
                run = self.runList[j]
                runInfo = ""
                if run in runInfoDict.keys():
                    runInfo = runInfoDict[run]
                ax[i].hist(
                    self.dataArray[j][:, :, index].clip(*tuple(self.dataRanges[stat])).flatten(),
                    nBins,
                    label="r%s %s %s" % (run, stat, runInfo),
                    alpha=0.5,
                )

            ax[i].legend(loc="best")
            print("foo")
        ##plt.show()
        stats = "_".join(statList)
        print(stats)
        logger.info(stats)
        figFileName ="%s_%s_overlay.png" % (self.label, stats)
        plt.savefig(figFileName)
        logger.info("Wrote file: " + figFileName)
        plt.close()

    def analyze(self):
        print("analyze dataArray")
        logger.info("analyze dataArray")
        for array in self.statsArray:
            self.overlayHistograms(array)


if __name__ == "__main__":
    f = sys.argv[1]
    module = eval(sys.argv[2])
    statsArray = None
    plainStatsArray = None
    ratioStatsArray = None

    try:
        statsArray = [sys.argv[3].split(",")]
    except:
        pass

    label = f.split(".npy")[0]
    if "," in f:
        print("compare files...", label, statsArray)
        dataArray = [np.load(g) for g in f.split(",")]
        dataArray = np.array(dataArray)
        ##        runList = [eval(re.search(r'_r(\d+)_', a).group(1)) for a in f.split(',')]
        runList = [re.search(r"_r(\d+)_", a).group(1) for a in f.split(",")]
        label = label.replace("r%s" % (runList[0]), "r" + "_r".join(runList))
        if "Linearity" in f.split(",")[0]:
            scanObj = LinearityInfo()
            if statsArray is None:
                statsArray = [["g1min", "g1intercept"]]
        elif "Foo" in f.split(",")[0]:  ##fake example
            scanObj = FooInfo()
            if statsArray is not None:
                statsArray = [["g1min", "g1intercept"]]

        a = CompareMultipleScans(scanObj, statsArray, dataArray, runList, label)
        a.analyze()

    else:
        data = np.load(f)
        label = f.split(".npy")[0]
        if "Linearity" in f:
            print(f)
            scanObj = LinearityInfo()
            if statsArray is None:
                plainStatsArray = [["g0slope", "g1slope"], ["g0r2", "g1r2"], ["g0max", "g1min"]]
                ratioStatsArray = [["g1slope", "g0slope"]]
            else:
                plainStatsArray = statsArray

        if plainStatsArray is not None:
            a = AnalyzeOneScan(scanObj, plainStatsArray, data, module, label)
            a.analyze()

        if ratioStatsArray is not None:
            a = AnalyzeOneScan(scanObj, ratioStatsArray, data, module, label, ratio=True)
            a.analyze()
