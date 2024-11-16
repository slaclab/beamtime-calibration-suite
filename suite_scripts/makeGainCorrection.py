##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################

import numpy as np

from calibrationSuite import ancillaryMethods
from calibrationSuite.basicSuiteScript import BasicSuiteScript


class MakeGainCorrection(BasicSuiteScript):
    def __init__(self):
        super().__init__()  ##self)


if __name__ == "__main__":
    mgc = MakeGainCorrection()
    mgc.setupPsana()

    setOutliersToMedian = True
    clipSigmas = 3
    if not setOutliersToMedian:
        print("will clip on the module (not bank) level outside +/- %0.1f sigma" % (clipSigmas))
    else:
        print("will set to median on the module (not bank) level outside +/- %0.1f sigma" % (clipSigmas))

    if mgc.fakePedestal is not None:
        pedestal = mgc.fakePedestal
    else:
        evt = mgc.getEvt()
        pedestal = mgc.getPedestal(evt, mgc.gainMode)
    ## pedestal should be the same shape as a the numpy file analyzed

    data = np.load(mgc.file)
    print("found %d NaN elements in %s" % (np.isnan(data).sum(), mgc.file))

    ## handle 2d case
    if mgc.detectorInfo.dimension == 2:
        data = np.array([data])
        pedestal = np.array([pedestal])

    ## clean up by module
    ## ??? or bank ???
    for m in range(mgc.detectorInfo.nModules):
        regionMedian = np.median(data[m][np.isfinite(data[m])])
        data[m][np.isnan(data[m])] = regionMedian
        data[m][data[m] == 0] = regionMedian

        rms = data[m].std()
        lowCutDouble = regionMedian - 2 * clipSigmas * rms
        highCutDouble = regionMedian + 2 * clipSigmas * rms
        rmsClipped = (data[m]).clip(lowCutDouble, highCutDouble).std()
        ## this accounts for extra long tails so we don't clip
        ## using a distorted metric
        ## responds to bad pixels

        lowCut = regionMedian - clipSigmas * rmsClipped
        highCut = regionMedian + clipSigmas * rmsClipped
        nLow = (data[m] < lowCut).sum()
        nHigh = (data[m] > highCut).sum()
        print("will reset %d low tail and %d high tail pixels in module %d" % (nLow, nHigh, m))
        if not setOutliersToMedian:
            data[m] = data[m].clip(lowCut, highCut)
        else:
            data[m][data[m] < lowCut] = regionMedian
            data[m][data[m] > highCut] = regionMedian

        print("have clipped module %d, pre-clipped rms was %0.2f, now %0.2f" % (m, rmsClipped, data[m].std()))

    correction = measuredAduPerKeV = data / mgc.photonEnergy * mgc.aduPerKeV

    if mgc.detectorInfo.detectorType == "Epix100a":
        ## psana wants keV/adu in this one case
        correction = 1.0 / measuredAduPerKeV

    if "Epix10k" in mgc.detectorInfo.detectorType:
        if mgc.gainMode == 1:
            highGainCorr = np.load("/sdf/data/lcls/ds/det/detdaq21/results/lowFlux/ePix10k_Q2_FH_Gain.npy")
            print("rescaling FM to FH")
            correction = correction * 8.07 / data.mean()
            fullCorrection = np.array(
                [highGainCorr, correction, correction / 33, highGainCorr, correction, correction * 0, correction * 0]
            )
        else:
            print("needs more work")
            raise Exception
    elif mgc.detectorInfo.detectorType == "Epix100a":
        fullCorrection = correction
        ## may need to adjust dimension

    fileName = mgc.file.split(".npy")[0] + "_cleanedCorrection.npy"
    np.save(fileName, correction)
    fileName = "%d-end.data" % (mgc.run)
    mgc.det.save_txtnda(fileName, ndarr=fullCorrection, fmt="%.4f")

    print("n.b. for autoranging detectors this needs to be applied carefully")

    import matplotlib.pyplot as plt

    pedMean = pedestal.mean()
    pedRms = pedestal.std()
    x, y, err = ancillaryMethods.makeProfile(
        pedestal.clip(pedMean - 5 * pedRms, pedMean + 4 * pedRms).flatten(), correction.flatten(), 50
    )  ##, spread=True)##, myStatistic="median")
    plt.errorbar(x, y, err)
    plt.xlabel("pedestal")
    plt.ylabel("gain correction")
    fileName = mgc.file.split(".npy")[0] + "_correctionVsPed.png"
    plt.savefig(fileName)
