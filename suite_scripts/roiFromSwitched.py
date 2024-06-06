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

import calibrationSuite.loggingSetup as ls
import numpy as np
from calibrationSuite.basicSuiteScript import BasicSuiteScript

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(
    "../logs/" + currFileName[:-3] + ".log", logging.ERROR
)  # change to logging.INFO for full logging output

if __name__ == "__main__":
    rfs = BasicSuiteScript("test2")
    print("have built an RFS")
    logger.info("have built an RFS")

    rfs.setupPsana()

    switchedPixels = None
    nGoodEvents = 0
    while True:
        evt = rfs.getEvt()
        if evt is None:
            break

        rawFrames = rfs.getRawData(evt, gainBitsMasked=False)
        if rawFrames is None:
            continue

        fG1 = rawFrames >= rfs.g0cut
        try:
            switchedPixels = np.bitwise_or(fG1, switchedPixels)
        except Exception:
            switchedPixels = fG1

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            logger.info("n good events analyzed: %d" % (nGoodEvents))
            print("switched pixels: %d" % ((switchedPixels > 0).sum()))
            logger.info("switched pixels: %d" % ((switchedPixels > 0).sum()))

        if nGoodEvents > rfs.maxNevents:
            break

    fileName = "%s/roiFromSwitched_r%d_c%d.npy" % (rfs.outputDir, rfs.run, rfs.camera)
    np.save(fileName, switchedPixels)
    logger.info("Wrote file: ", fileName)

    print("%d pixels were in low at least once in %d events" % ((switchedPixels > 0).sum(), nGoodEvents))
    logger.info("%d pixels were in low at least once in %d events" % ((switchedPixels > 0).sum(), nGoodEvents))
