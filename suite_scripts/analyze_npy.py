import matplotlib.pyplot as plt
import numpy as np
from calibrationSuite.fitFunctions import *
from calibrationSuite.ancillaryMethods import *
import sys


class AnalyzeLinearity(object):
    def __init__(self, data, label):
        self.data = data
        self.label = label
        self.dataIndices = {
            "g0slope": 0,
            "g0intercept": 1,
            "g0r2": 2,
            "g1slope": 3,
            "g1intercept": 4,
            "g1r2": 5,
            "g0max": 6,
            "g1min": 7,
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

    def analyzeLinearity(self):
        self.plotLinearity("g0slope", "g1slope")
        self.plotLinearity("g0r2", "g1r2")
        self.plotLinearity("g0max", "g1min")
        self.plotRatio("g1slope", "g0slope", clipRange=[0, 0.05])

    def plotLinearity(self, stat0, stat1):
        ##return
        g0Range = self.dataRanges[stat0]
        g1Range = self.dataRanges[stat1]
        g0Index = self.dataIndices[stat0]
        g1Index = self.dataIndices[stat1]

        fig, ax = plt.subplots(2, 2)
        d = self.data[:, :, g0Index]
        print(stat0, "median:", np.median(d))
        im = ax[0, 0].imshow(d.clip(*tuple(g0Range)))
        fig.colorbar(im)
        ax[0, 0].set_title(stat0)
        ax[0, 1].hist(d.clip(*tuple(g0Range)), 100)
        ax[0, 1].set_title(stat0)
        d = self.data[:, :, g1Index]
        print(stat1, "median:", np.median(d))
        im = ax[1, 0].imshow(d.clip(*tuple(g1Range)))
        fig.colorbar(im)
        ax[1, 0].set_title(stat1)
        ax[1, 1].hist(d.clip(*tuple(g1Range)), 100)
        ax[1, 1].set_title(stat1)
        ##plt.show()
        plt.savefig("%s_%s_%s_maps_and_histos.png" % (self.label, stat0, stat1))
        plt.close()

    def plotRatio(self, statA, statB, clipRange=None):
        ##g0Range = self.dataRanges[stat0]
        ##g1Range = self.dataRanges[stat1]
        indexA = self.dataIndices[statA]
        indexB = self.dataIndices[statB]
        fig, ax = plt.subplots(2, 1)
        d = self.data[:, :, indexA] / self.data[:, :, indexB]
        print(statA, statB, "ratio median:", np.median(d))
        d = d.clip(*tuple(clipRange))
        ##im = ax[0,0].imshow(d.clip(*tuple(g0Range)))
        im = ax[0].imshow(d)
        fig.colorbar(im)
        ax[0].set_title("%s/%s" % (statA, statB))
        ax[1].hist(d, 100)
        ax[1].set_title("%s/%s" % (statA, statB))
        plt.savefig("%s_%s_%s_ratio_map_and_histo.png" % (self.label, statA, statB))
        plt.close()


f = sys.argv[1]
data = np.load(f)
label = f.split(".npy")[0]
if "Linearity" in f:
    print(f)
    a = AnalyzeLinearity(data, label)
    a.analyzeLinearity()
