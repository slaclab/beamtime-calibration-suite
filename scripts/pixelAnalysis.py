import numpy as np
import matplotlib.pyplot as plt
import fitFunctions
import ancillaryMethods
from scipy.optimize import curve_fit
import logging

logger = logging.getLogger(__name__)


# fitIndex=2
def analysis_one(clusters, energy, rows, cols, fitInfo, lowEnergyCut, highEnergyCut, fileInfo):
    for i in range(rows):
        for j in range(cols):
            # Create bool array satisfying the conds
            pixel = np.bitwise_and((clusters[:, :, 1] == i), (clusters[:, :, 2] == j))
            small = np.bitwise_and((clusters[:, :, 3] < 4), (clusters[:, :, 4] == 1))
            smallPixel = np.bitwise_and(small, pixel)

            # Adjusted due to gains not making sense
            # Would be good to get rid of these entirely when things make sense
            pixelEcut0 = np.bitwise_and(smallPixel, energy > lowEnergyCut)
            pixelEcut = np.bitwise_and(pixelEcut0, energy < highEnergyCut)
            nPixelClusters = (pixelEcut > 0).sum()

            mean = std = mu = sigma = 0

            # Select energy vals that passed cut conditions
            # (selects elements from energy where corresponding element in pixelEcut is True)
            pixelE = energy[pixelEcut > 0]

            if nPixelClusters > 5:  # only do analysis if enough pixels
                print("pixel %d,%d has %d photons" % (i, j, nPixelClusters))
                logger.info("pixel %d,%d has %d photons" % (i, j, nPixelClusters))
                ax = plt.subplot()
                y, bin_edges, _ = ax.hist(pixelE, 100)
                bins = (bin_edges[:-1] + bin_edges[1:]) / 2
                # print(y, bins)
                mean, std = fitFunctions.estimateGaussianParameters(pixelE)
                try:
                    # Set maxfev arg > 800?? (fails to find optimal params for some clusters)
                    popt, pcov = curve_fit(fitFunctions.gaussian, bins, y, [3, mean, std])

                    mu = popt[1]
                    sigma = popt[2]
                    fitInfo[i, j] = (mean, std, popt[1], popt[2])
                    fitFunctions.gaussian(bins, *popt)
                    # ax.plot(bins, fittedFunc, color="b")
                except Exception as e:
                    print(f"An exception occurred: {e}")
                    logger.error(f"An exception occurred: {e}")
                    pass

                ax.set_xlabel("energy (keV)")
                ax.set_title("pixel %d,%d in slice, small cluster cuts" % (i, j))
                plt.figtext(0.7, 0.8, "%d entries" % (nPixelClusters))
                plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
                plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
                fileName = "%s/%s_r%d_c%d_r%d_c%d_%s_E.png" % (
                    fileInfo.outputDir,
                    fileInfo.className,
                    fileInfo.run,
                    fileInfo.camera,
                    i,
                    j,
                    fileInfo.label,
                )
                logger.info("Writing plot: " + fileName)
                plt.savefig(fileName)
                plt.close()
    return fitInfo


# fitIndex=3
def analysis_two(clusters, nBins, sliceCoordinates, rows, cols, fitInfo, lowEnergyCut, highEnergyCut, fileInfo):
    fitInfo = np.zeros((rows, cols, 5))  ## mean, std, area, mu, sigma
    for i in range(rows):
        for j in range(cols):
            ax = plt.subplot()

            detRow, detCol = sliceToDetector(i, j, sliceCoordinates)
            goodClusters = ancillaryMethods.goodClusters(clusters, i, j, nPixelCut=4, isSquare=1)
            if len(goodClusters) < 5:
                print("too few clusters in slice pixel %d, %d: %d" % (i, j, len(goodClusters)))
                continue

            energies = ancillaryMethods.getClusterEnergies(goodClusters)
            photonEcut = np.bitwise_and(energies > lowEnergyCut, energies < highEnergyCut)
            nPixelClusters = (photonEcut > 0).sum()
            print("pixel %d,%d has about %d photons" % (i, j, nPixelClusters))
            logger.info("pixel %d,%d has %d photons" % (i, j, nPixelClusters))

            photonRegion = energies[photonEcut]
            mean = photonRegion.mean()
            std = photonRegion.std()
            a, mu, sigma = histogramAndFitGaussian(ax, energies, nBins)
            area = fitFunctions.gaussianArea(a, sigma)

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
    a, mean, std = fitFunctions.estimateGaussianParametersFromUnbinnedArray(energies)
    try:
        popt, pcov = fitFunctions.curve_fit(fitFunctions.gaussian, bins, y, [a, mean, std])
        popt[1]
        popt[2]
        fittedFunc = fitFunctions.gaussian(bins, *popt)
        ax.plot(bins, fittedFunc, color="b")
        return popt
    except Exception:
        return 0, 0, 0


def sliceToDetector(sliceRow, sliceCol, sliceCoordinates):
    return sliceRow + sliceCoordinates[0][0], sliceCol + sliceCoordinates[1][0]
