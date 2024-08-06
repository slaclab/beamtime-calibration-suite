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

from calibrationSuite.basicSuiteScript import BasicSuiteScript
from calibrationSuite.Stats import Stats

if __name__ == "__main__":
    bss = BasicSuiteScript("dark")

    print("have built a " + bss.className + " class")
    bss.logger.info("have built a " + bss.className + " class")

    bss.setupPsana()
    if bss.special is not None and "skip283" in bss.special:
        skip283 = True
    else:
        skip283 = False

    stepGen = bss.getStepGen()

    # used for testing to stop analysis early (full run is too slow)
    isTestRun = bss.special is not None and "testRun" in bss.special
    outer_count = 0
    outer_max = 1
    inner_count = 0
    inner_max = 50

    for nstep, step in enumerate(stepGen):
        # for testing
        outer_count += 1

        statsArray = [None for i in bss.singlePixels]

        for nevt, evt in enumerate(step.events()):
            if evt is None:
                continue

            # for testing
            inner_count += 1
            if isTestRun and inner_count > inner_max:
                break

            frames = None
            if nevt < bss.skipNevents:
                print(nevt, bss.skipNevents)
                continue

            ec = bss.getEventCodes(evt)
            beamEvent = bss.isBeamEvent(evt)
            if not beamEvent and not skip283:
                continue

            if bss.special is not None and "CommonMode" in bss.special:
                commonModeCut = 2.0  ## keV, calib

                if bss.detObj and bss.detObj == "raw":
                    frames = bss.getRawData(evt).astype("float")
                    commonModeCut = bss.gainBitsMask
                else:
                    frames = bss.getCalibData(evt)

                if frames is None:
                    continue

                if "noCommonMode" in bss.special:
                    frames = bss.noCommonModeCorrection(frames)
                elif "rowCommonMode" in bss.special:
                    if bss.fakePedestal is None:
                        print("row common mode needs reasonable pedestal")
                        raise Exception
                    frames = frames - bss.fakePedestal
                    frames = bss.rowCommonModeCorrection3d(frames, 2.0)
                elif "colCommonMode" in bss.special:
                    if bss.fakePedestal is None:
                        print("col common mode needs reasonable pedestal")
                        raise Exception
                    frames = frames - bss.fakePedestal
                    frames = bss.colCommonModeCorrection3d(frames, 2.0)
                elif "regionCommonMode" in bss.special:
                    frames = bss.regionCommonModeCorrection(frames, bss.regionSlice, commonModeCut)

            else:
                frames = bss.getRawData(evt, gainBitsMasked=True)
                if frames is not None and bss.special is not None and "parity" in bss.special:
                    if bss.getPingPongParity(frames[0][144:224, 0:80]) == ("negative" in bss.special):
                        continue
                ##print(frames)

            if frames is None:
                print("None frames on beam event, should not happen")
                bss.logger.info("None frames on beam event")
                continue

            for i, p in enumerate(bss.singlePixels):
                try:
                    statsArray[i].accumulate(np.double(frames), frames[tuple(p)])
                except Exception:
                    statsArray[i] = Stats(frames.shape)
                    statsArray[i].accumulate(np.double(frames), frames[tuple(p)])

        stats = statsArray[2]  ## only matters for cross-correlation
        try:
            noise = stats.rms()
        except Exception:
            ## probably have no good events
            bss.dumpEventCodeStatistics()
            raise Exception("no stats object, probably no good events")

        means = stats.mean()
        if bss.special is not None and "slice" in bss.special:
            noise = noise[bss.regionSlice]
            print("mean, median noise: " + str(noise.mean()) + " " + str(np.median(noise)))
            bss.logger.info("mean, median noise: " + str(noise.mean()) + " " + str(np.median(noise)))
            means = means[bss.regionSlice]

        if bss.fakePedestal is not None:
            bss.label += "_fakePdestal"

        meanRmsFileName = "%s/CalcNoiseAndMean_%s_rms_r%d_step%s.npy" % (bss.outputDir, bss.label, bss.run, nstep)
        np.save(meanRmsFileName, noise)
        meanFileName = "%s/CalcNoiseAndMean_mean_%s_r%d_step%s.npy" % (bss.outputDir, bss.label, bss.run, nstep)
        np.save(meanFileName, means)
        bss.logger.info("Wrote file: " + meanRmsFileName)
        bss.logger.info("Wrote file: " + meanFileName)

        for i, p in enumerate(bss.singlePixels):
            try:
                meanCorrelationFileName = (
                    "%s/CalcNoiseAndMean_correlation_pixel_%d_%d_%s_r%d_step%s.npy"
                    % (bss.outputDir, p[1], p[2], bss.label, bss.run, nstep),
                )
                np.save(
                    meanCorrelationFileName,
                    statsArray[i].corr(statsArray[i].mean()[p[1], p[2]], statsArray[i].rms()[p[1], p[2]])[
                        bss.regionSlice
                    ],
                )
                logging.info("Wrote file: " + meanCorrelationFileName)

            except Exception:
                ## probably rms = 0.
                continue

        # for testing
        if isTestRun and outer_count >= outer_max:
            break

    bss.dumpEventCodeStatistics()
