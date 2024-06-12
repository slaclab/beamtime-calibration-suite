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

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binned_statistic

logger = logging.getLogger(__name__)


def makeProfile(x, y, bins, range=None, spread=False, myStatistic="mean"):
    ## NaN for empty bins are suppressed
    ## using mean root(N) for non-empty bins to calculate 0 var weights
    ##
    ## spread=True to return standard deviation instead of standard error

    meansObj = binned_statistic(x, [y, y**2], bins=bins, range=range, statistic=myStatistic)
    means, means2 = meansObj.statistic
    countsObj = binned_statistic(x, y, bins=bins, range=range, statistic="count")
    stdObj = binned_statistic(x, y, bins=bins, range=range, statistic="std")
    bin_N = countsObj.statistic
    usefulBins = np.bitwise_and(bin_N > 0, ~np.isnan(means))
    if bin_N.sum() == 0:
        ##no data
        print("no data in profile")
        logger.error("no data in profile")
        return None, None, None

    ##yErr = np.sqrt(means2 - means**2)
    yErr = stdObj.statistic
    if not spread:
        root_N = np.sqrt(bin_N)
        root_N[root_N == 0] = root_N[usefulBins].mean()
        yErr = yErr / root_N
        ##yErr = yErr.clip(0, 6666666.)

    bin_edges = meansObj.bin_edges
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    return bin_centers[usefulBins], means[usefulBins], yErr[usefulBins]


def plotProfile(x, y, yErr):
    plt.errorbar(x=x, y=y, yerr=yErr, linestyle="none", marker=".")


def selectedClusters(clusters, row, col, lowEnerygCut, highEnergyCut, nPixelCut=4, isSquare=1):
    pass


def getEnergeticClusters(clusters):
    ## expects [events, maxClusters, nClusterElements]
    ## returns [nEnergeticClusters, nClusterElements]
    return clusters[clusters[:, :, 0] > 0]


def getSmallSquareClusters(clusters, nPixelCut=4):
    smallClusters = getSmallClusters(clusters, nPixelCut=4)
    return getSquareClusters(smallClusters)


def getSmallClusters(clusters, nPixelCut=4):
    return clusters[clusters[:, 4] < nPixelCut]


def getSquareClusters(clusters):
    return clusters[clusters[:, 5] == 1]


def getMatchedClusters(clusters, dimension, n):
    if dimension == "column":
        return clusters[(clusters[:, 3] == n)]
    if dimension == "row":
        return clusters[(clusters[:, 2] == n)]
    if dimension == "module":
        return clusters[(clusters[:, 1] == n)]
    return None


##def getMatchedClusters(clusters, m, row, col):
##    matched = np.bitwise_and.reduce([(clusters[:,1]==m), (clusters[:,2]==row), clusters[:,3]==col])
##    return clusters[matched]


def goodClusters(clusters, module, row, col, nPixelCut=4, isSquare=None):
    ## this is too slow
    mCut = clusters[:, :, 1] == module
    pixelRowCol = np.bitwise_and((clusters[:, :, 2] == row), (clusters[:, :, 3] == col))
    if isSquare is None:
        small = clusters[:, :, 4] < nPixelCut
    else:
        small = np.bitwise_and((clusters[:, :, 4] < nPixelCut), (clusters[:, :, 5] == isSquare))
    c = clusters[np.bitwise_and.reduce([mCut, small, pixelRowCol])]
    ##print(c.shape)
    ##print(c)
    return c


def getClusterEnergies(clusters):
    ##print(clusters)
    return clusters[:, 0]

class Histogram_1d(object):
    def __init__(self, data=[], nBins=None, xRange=None):
        self.nBins = nBins
        self.xRange = xRange
        self.hist, edges = np.histogram(data, bins=self.nBins, range=self.xRange)
        self.bins = (edges[:-1] + edges[1:]) / 2.

    def fill(self, value):
        hist, _ = np.histogram([value], bins=self.nBins, range=self.xRange)
        self.hist += hist



