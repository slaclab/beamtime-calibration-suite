##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from calibrationSuite.basicSuiteScript import *

import calibrationSuite.loggingSetup as ls
# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging("../logs/" + currFileName[:-3] + ".log", logging.INFO)  # change to logging.INFO for full logging output

class SimplePhotonCounter(BasicSuiteScript):
    def __init__(self):
        super().__init__(analysisType="lowFlux")


if __name__ == "__main__":
    spc = SimplePhotonCounter()
    spc.setupPsana()

    nGoodEvents = 0
    thresholded = None
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
            print('foo')
            continue

        if spc.fakePedestal is not None:
            frames = rawFrames.astype("float") - spc.fakePedestal
            frames /= gain ## psana may not have the right default
        else:
            frames = spc.getCalibData(evt)

        if frames is None:
            ##print("No contrib found")
            continue
        try:
            thresholded += (frames > spc.photonCut) * 1.0
        except:
            thresholded = (frames > spc.photonCut) * 1.0

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            logging.info("n good events analyzed: %d" % (nGoodEvents))

        if nGoodEvents > spc.maxNevents:
            break
    if spc.special is not None and "slice" in spc.special:
        thresholded = thresholded[0][spc.regionSlice]

    npyFileName = "%s/%s_%s_r%d_c%d_%s.npy" % (spc.outputDir, spc.className, spc.label, spc.run, spc.camera, spc.exp)
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

    spc.dumpEventCodeStatistics()
