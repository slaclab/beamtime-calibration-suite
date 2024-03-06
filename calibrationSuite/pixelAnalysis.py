import numpy as np
import logging
import matplotlib.pyplot as plt
from calibrationSuite.fitFunctions import *
from calibrationSuite.ancillaryMethods import *
from scipy.optimize import curve_fit


logger = logging.getLogger(__name__)

# add more analysis here...

# fitIndex=3
def analysis_one(clusters, nBins, sliceCoordinates, rows, cols, fitInfo, lowEnergyCut, highEnergyCut, fileInfo):
    fitInfo = np.zeros((rows, cols, 5))  ## mean, std, area, mu, sigma
    for i in range(rows):
        for j in range(cols):
            ax = plt.subplot()

            detRow, detCol = sliceToDetector(i, j, sliceCoordinates)
            currGoodClusters = goodClusters(clusters, i, j, nPixelCut=4, isSquare=1)
            if len(currGoodClusters) < 5:
                print("too few clusters in slice pixel %d, %d: %d" % (i, j, len(currGoodClusters)))
                continue

            energies = getClusterEnergies(currGoodClusters)
            photonEcut = np.bitwise_and(energies > lowEnergyCut, energies < highEnergyCut)
            nPixelClusters = (photonEcut > 0).sum()
            print("pixel %d,%d has about %d photons" % (i, j, nPixelClusters))
            logger.info("pixel %d,%d has %d photons" % (i, j, nPixelClusters))

            photonRegion = energies[photonEcut]
            mean = photonRegion.mean()
            std = photonRegion.std()
            a, mu, sigma = histogramAndFitGaussian(ax, energies, nBins)
            area = gaussianArea(a, sigma)

            ax.set_xlabel("energy (keV)")
            ax.set_title("pixel %d,%d, small cluster cuts" % (detRow, detCol))
            plt.figtext(0.7, 0.8, "%d entries (peak)" % (area))
            plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
            plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
            fileNamePlot = "%s/%s_r%d_c%d_r%d_c%d_%s_E.png" % (
                fileInfo.outputDir,
                fileInfo.className,
                fileInfo.run,
                fileInfo.camera,
                detRow,
                detCol,
                fileInfo.label,
            )
            logger.info("Writing plot: " + fileNamePlot)
            plt.savefig(fileNamePlot)
            plt.close()

            fileNameNpy = "%s/%s_r%d_c%d_r%d_c%d_%s_fitInfo.npy" % (
                fileInfo.outputDir,
                fileInfo.className,
                fileInfo.run,
                fileInfo.camera,
                detRow,
                detCol,
                fileInfo.label,
            )
            logger.info("Writing npy: " + fileNameNpy)
            np.save(fileNameNpy, fitInfo)

            fitInfo[i, j] = mean, std, area, mu, sigma
    return fitInfo


# Helpers
def histogramAndFitGaussian(ax, energies, nBins):
    y, bin_edges, _ = ax.hist(energies, nBins)
    bins = (bin_edges[:-1] + bin_edges[1:]) / 2
    ##print(y, bins)
    a, mean, std = estimateGaussianParametersFromUnbinnedArray(energies)
    try:
        popt, pcov = curve_fit(gaussian, bins, y, [a, mean, std])
        popt[1]
        popt[2]
        fittedFunc = gaussian(bins, *popt)
        ax.plot(bins, fittedFunc, color="b")
        return popt
    except Exception:
        return 0, 0, 0


def sliceToDetector(sliceRow, sliceCol, sliceCoordinates):
    return sliceRow + sliceCoordinates[0][0], sliceCol + sliceCoordinates[1][0]