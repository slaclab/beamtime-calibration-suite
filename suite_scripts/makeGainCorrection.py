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

    if mgc.fakePedestal is not None:
        pedestal = mgc.fakePedestal
    else:
        evt = mgc.getEvt()
        pedestal = mgc.getPedestal(evt, gainmode=0)
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
        rms = data[m].std()
        data[m] = data[m].clip(regionMedian - 3 * rms, regionMedian + 3 * rms)
        print("have clipped module %d, rms was %0.2f, now %0.2f" % (m, rms, data[m].std()))

    correction = measuredAduPerKeV = data / mgc.photonEnergy * mgc.detectorInfo.aduPerKeV
    if mgc.detectorInfo.detectorType == "Epix100a":
        ## psana wants keV/adu in this one case
        correction = 1.0 / measuredAduPerKeV

    fileName = mgc.file.split(".npy")[0] + "_cleanedCorrection.npy"
    np.save(fileName, correction)

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
