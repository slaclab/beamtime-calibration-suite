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

import numpy as np

import calibrationSuite.loggingSetup as ls
from calibrationSuite.basicSuiteScript import BasicSuiteScript

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(
    "../logs/" + currFileName[:-3] + ".log", logging.INFO
)  # change to logging.INFO for full logging output


if __name__ == "__main__":
    spc = BasicSuiteScript(analysisType="lowFlux")
    scriptType = "SimplePhotonCounter"  # for naming output files
    spc.setupPsana()

    nGoodEvents = 0
    thresholded = None
    energyHistogramBins = 1000
    energyHistogram = np.zeros(energyHistogramBins)
    energyHistogramRange = [-100, 900]  ## should get this from somewhere
    gain = None
    if spc.fakePedestal is not None:
        if spc.detectorInfo is not None:
            gain = spc.detectorInfo.aduPerKeV
        else:
            if "FH" in spc.special:
                gain = 20  ##17.## my guess
            elif "FM" in spc.special:
                gain = 6.66  # 20/3
            else:
                raise Exception
        print("using gain correction", gain)

    if spc.threshold is not None:
        spc.photonCut = spc.threshold
    else:
        spc.photonCut = 6.0
        print("using photon cut", spc.photonCut)

    while True:
        evt = spc.getEvt()
        if evt is None:
            break
        if not spc.isBeamEvent(evt):
            ##print('foo')
            continue

        if spc.fakePedestal is not None:
            rawFrames = spc.getRawData(evt)
            if rawFrames is None:
                continue
            frames = rawFrames.astype("float") - spc.fakePedestal
            frames /= gain  ## psana may not have the right default
        else:
            frames = spc.getCalibData(evt)

        if frames is None:
            ##print("No contrib found")
            continue
        try:
            thresholded += (frames > spc.photonCut) * 1.0
        except Exception:
            thresholded = (frames > spc.photonCut) * 1.0

        if False and gain is not None:
            for e in frames.flatten():
                energyHistogram[((e - energyHistogramRange[0]) / energyHistogramBins).clip(0, energyHistogramBins)] += 1

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            logging.info("n good events analyzed: %d" % (nGoodEvents))

        if nGoodEvents > spc.maxNevents:
            break
    if spc.special is not None and "slice" in spc.special:
        thresholded = thresholded[spc.regionSlice]

    npyFileName = "%s/%s_%s_r%d_c%d_%s.npy" % (spc.outputDir, scriptType, spc.label, spc.run, spc.camera, spc.exp)
    np.save(npyFileName, thresholded / nGoodEvents)
    logger.info("Wrote file: " + npyFileName)
    print(
        "likelihood of a photon or photons per pixel using cut %0.2f is %0.3f"
        % (spc.photonCut, (thresholded / nGoodEvents).mean())
    )
    logger.info(
        "likelihood of a photon or photons per pixel using cut %0.2f is %0.3f"
        % (spc.photonCut, (thresholded / nGoodEvents).mean())
    )
    print("total photons in detector using cut %0.2f is %0.3f" % (spc.photonCut, (thresholded).sum()))
    logger.info("total photons in detector using cut %0.2f is %0.3f" % (spc.photonCut, (thresholded).sum()))

    if True:  ##False:
        spectrumFileName = "%s/%s_%s_r%d_c%d_%s_spectrum.npy" % (
            spc.outputDir,
            scriptType,
            spc.label,
            spc.run,
            spc.camera,
            spc.exp,
        )
        np.save(spectrumFileName, energyHistogram)

        imageFileName = spectrumFileName.replace("spectrum", "image")
        tImage = spc.getImage(evt, thresholded)
        np.save(imageFileName, tImage)
        import matplotlib.pyplot as plt

        p90 = np.percentile(tImage, 90)
        print("clipping image at 90% of max")
        plt.imshow(tImage.clip(0, p90))
        plt.colorbar()
        plt.savefig(imageFileName.replace("npy", "png"))

    spc.dumpEventCodeStatistics()
