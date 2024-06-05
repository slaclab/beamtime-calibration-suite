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
import sys

import calibrationSuite.loggingSetup as ls
import h5py
import matplotlib.pyplot as plt
import numpy as np
from calibrationSuite.basicSuiteScript import BasicSuiteScript
from matplotlib.ticker import AutoMinorLocator

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(
    "../logs/" + currFileName[:-3] + ".log", logging.INFO
)  # change to logging.INFO for full logging output


class TimeScanParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__()  ##self)
        try:
            print("positive events:", "positive" in self.special)
            logger.info("positive events:" + (["positive" in self.special]))
        except Exception:
            pass

    def plotData(self, rois, pixels, delays, label):
        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(delays, rois[i], label=self.ROIfileNames[i])
            plt.grid(which="major", linewidth=0.5)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel("Time delay (Ticks/1000)")
            # plt.ylabel('Step Mean (keV)')
            plt.ylabel("Step Mean (ADU)")
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)

            figFileName = "%s/%s_r%d_c%d_%s_ROI%d.png" % (
                self.outputDir,
                self.__class__.__name__,
                self.run,
                self.camera,
                label,
                i,
            )
            plt.savefig(figFileName)
            logger.info("Wrote file: " + figFileName)
            plt.clf()

        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ax.plot(delays, rois[i], label=self.ROIfileNames[i])
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel("Time delay (Ticks/1000)")
            # plt.ylabel('Step Mean (keV)')
            plt.ylabel("Step Mean (ADU)")
            ##plt.yscale('log')
            plt.legend(loc="upper right")

        if self.ROIs != []:
            figFileName = "%s/%s_r%d_c%d_%s_All%d.png" % (
                self.outputDir,
                self.__class__.__name__,
                self.run,
                self.camera,
                label,
                i,
            )
            plt.savefig(figFileName)
            logger.info("Wrote file: " + figFileName)
            plt.close()
        # plt.show()

        for i, p in enumerate(self.singlePixels):
            ax = plt.subplot()
            ax.plot(delays, pixels[i], label=str(p))
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel("Delay (Ticks/1000)")
            plt.ylabel("Pixel ADU")

            figFileName = "%s/%s_r%d_c%d_%s_pixel%d.png" % (
                self.outputDir,
                self.__class__.__name__,
                self.run,
                self.camera,
                label,
                i,
            )
            plt.savefig(figFileName)
            logger.info(figFileName)
            plt.close()

    def plotSliceData(self, sliceData, delays, label):
        print("in plot slice data, asic 1 for the moment")
        for i in range(5):
            ##slicePixel = [i*2, i*2]
            ax = plt.subplot()
            ##ax.plot(delays, sliceData[:,tuple(slicePixel)], label="slicePixel%d" %(i))
            ax.plot(delays, sliceData[:, 1, i * 2, i * 2], label="slicePixel%d" % (i))
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel("Delay (Ticks)")
            plt.ylabel("Pixel ADU")

            figFileName = "%s/%s_r%d_c%d_%s_slicePixel%d.png" % (
                self.outputDir,
                self.__class__.__name__,
                self.run,
                self.camera,
                label,
                i,
            )
            plt.savefig(figFileName)
            plt.close()

    # unused and broken (estimateFineScanPars not implemented anywhere??)
    """
    def analyzeData(self, delays, data, label):
        edge = np.zeros(data.shape[0])
        for m in range(data.shape[1]):
            for r in range(data.shape[2]):
                for c in range(data.shape[3]):
                    d = data[:, m, r, c]
                    p0 = estimateFineScanPars(delays, d)
                    f = fineScanFunc
                    coeff, var = curve_fit(f, delays, d, p0=p0)
                    edge[m, r, c] = coeff[1]
        return edge
    """

    def analyze_h5(self, dataFile, norm, label):

        a = h5py.File(dataFile)[norm]
        delays = np.array([int(eval(k)) for k in a.keys()])
        print("delays:", delays)
        ##delays = delays.astype('float').astype("int")
        ##delays = delays.astype('float').astype("int")
        delays.sort()
        d = np.array([a[str(k)] for k in delays])
        delays = np.array([d for d in delays])
        delays = [d / 1000.0 for d in delays]
        ##delays /= 1000.
        print("scaled delays", delays)

        runString = "_r%d" % (self.run)
        if norm != "slice":
            print("doing %s analysis" % (norm))
            offset = len(self.ROIs)
            rois = d[:, 0:offset]
            pixels = d[:, offset:]
            self.plotData(rois.T, pixels.T, delays, norm + label + runString)
        else:
            self.plotSliceData(d, delays, norm + label + runString)


if __name__ == "__main__":
    tsp = TimeScanParallel()
    print("have built a ", tsp.className, "class")
    logger.info("have built a " + tsp.className + "class")
    fileMadeByScript = False
    if tsp.file is not None:
        print("tsp.file", tsp.file)
        fileMadeByScript = tsp.file.split("/")[-1].startswith(tsp.className)
    if fileMadeByScript:  ##and tsp.psanaType != 0: ## added type for rogue
        tsp.analyze_h5(tsp.file, "means", tsp.label)
        ##tsp.analyze_h5(tsp.file, 'ratios', tsp.label)
        tsp.analyze_h5(tsp.file, "slice", tsp.label)
        print("done with standalone analysis of %s, exiting" % (tsp.file))
        logger.info("done with standalone analysis of %s, exiting" % (tsp.file))
        sys.exit(0)

    tsp.setupPsana()
    tsp.use_281_for_old_data = False
    ##this is a hack
    if tsp.exp == "foo" and tsp.run < 500:  ## guess
        tsp.use_281_for_old_data = True
        print("using all event code 281 frames for old data")
        logger.info("using all event code 281 frames for old data")

    size = 666
    if "size" in dir():  ## check for rogue
        print("size is ", dir("size"))

    h5FileName = "%s/%s_%s_c%d_r%d_n%d.h5" % (tsp.outputDir, tsp.className, tsp.label, tsp.camera, tsp.run, size)
    smd = tsp.ds.smalldata(filename=h5FileName)

    tsp.nGoodEvents = 0
    stepMeans = {}
    stepMeans["means"] = {}
    stepMeans["ratios"] = {}
    stepMeans["slice"] = {}

    offset = len(tsp.ROIs)

    stepGen = tsp.getStepGen()
    ##for nstep, step in enumerate (tsp.ds.steps()):
    for nstep, step in enumerate(stepGen):
        ##scanValue = tsp.getScanValue(step, useStringInfo=True)
        scanValue = tsp.getScanValue(step, True)
        print(scanValue, "in tsp")
        logger.info(str(scanValue) + "in tsp")
        roiAndPixelSums = np.zeros(len(tsp.ROIs) + len(tsp.singlePixels)).astype(np.uint32)
        ratioSums = np.zeros(len(tsp.ROIs) + len(tsp.singlePixels)).astype(np.float32)

        nGoodInStep = 0
        stepSliceSum = np.zeros([tsp.detectorInfo.nModules, tsp.detectorInfo.nRows, tsp.detectorInfo.nCols])[
            tsp.regionSlice
        ].astype("float32")
        stepSliceSum = None
        for nevt, evt in enumerate(step.events()):
            if evt is None:
                continue
            ##if not tsp.isBeamEvent(evt):
            ##continue

            doFast = [True, False][0]
            fakeFlux = [True, False][0]  ## 0 for ASC lab, FEE
            if doFast:
                ec = tsp.getEventCodes(evt)

                ##tsp.isBeamEvent(evt):
                if tsp.detectorInfo.detectorType == "epixm" or tsp.isBeamEvent(evt):  ##FEE hack
                    frames = tsp.getRawData(evt)  ##, gainBitsMasked=True)
                    ##print("real beam on event", nstep, nevt)
                    ##logger.info("real beam on event" + str(nstep) + ", " + str(nevt))
                elif tsp.use_281_for_old_data and ec[281]:
                    frames = tsp.getRawData(evt)  ##, gainBitsMasked=True)
                    print("281 only...")
                elif ec[137]:
                    tsp.flux = tsp._getFlux(evt)  ## fix this
                    continue
                else:
                    print("not beam event, not frame event, not bld...")
                    logger.info("not beam event, not frame event, not bld...")
                    continue
            else:
                tsp.flux = tsp._getFlux(evt)  ## fix this
                frames = tsp.getRawData(evt)  ##, gainBitsMasked=True)

            if frames is None:
                ##print("no frame")
                continue

            if tsp.special is not None and "parity" in tsp.special:
                if tsp.getPingPongParity(frames[0][144:224, 0:80]) == ("negative" in tsp.special):
                    continue

            flux = tsp.getFlux(evt)
            if fakeFlux:
                flux = 1.0
            elif flux is None:
                print("no flux")
                continue
            elif tsp.threshold is not None and flux < tsp.threshold:
                print("flux =", flux, "<", tsp.threshold, "skip")
                continue
            nGoodInStep += 1

            try:
                stepSliceSum += frames[tsp.regionSlice]
                ##stepEvents += 1
            except Exception:
                stepSliceSum = frames[tsp.regionSlice].astype(np.float32)
                ##stepEvents = 1

            for i, roi in enumerate(tsp.ROIs):
                ##m = np.multiply(roi, frames).mean()
                m = frames[roi == 1].mean()
                roiAndPixelSums[i] += m
                ratioSums[i] += m / flux

            for j, _ in enumerate(tsp.singlePixels):
                v = frames[tuple(tsp.singlePixels[j])]
                roiAndPixelSums[offset + j] += v
                ratioSums[offset + j] += v / flux

            tsp.nGoodEvents += 1
            if tsp.nGoodEvents % 100 == 0:
                print("n good events analyzed: %d" % (tsp.nGoodEvents))
                logger.info("n good events analyzed: %d" % (tsp.nGoodEvents))
                ##print("switched pixels: %d" %((switchedPixels>0).sum()))

            if tsp.nGoodEvents > tsp.maxNevents:
                break

        if nGoodInStep == 0:
            roiAndPixelSums = None
            ratioSums = None

        step_sums = None
        ##print(roiAndPixelSums is None)
        step_sums = smd.sum(roiAndPixelSums)
        step_ratio_sums = smd.sum(ratioSums)
        step_nsum = smd.sum(nGoodInStep)
        try:
            step_slice_sum = smd.sum(stepSliceSum)
        except Exception:
            print(tsp.nGoodEvents)
            print(stepSliceSum.shape)
            ##print(stepSliceSum)
            step_slice_sum = np.zeros([tsp.detectorInfo.nModules, tsp.detectorInfo.nRows, tsp.detectorInfo.nCols])[
                tsp.regionSlice
            ].astype("float32")

        if roiAndPixelSums is not None:
            step_sums = smd.sum(roiAndPixelSums)
            step_ratio_sums = smd.sum(ratioSums)
            step_nsum = smd.sum(nGoodInStep)
        if step_sums is not None:
            stepMeans["means"][str(scanValue)] = step_sums / step_nsum
            stepMeans["ratios"][str(scanValue)] = step_ratio_sums / step_nsum
            stepMeans["slice"][str(scanValue)] = step_slice_sum / step_nsum
    if smd.summary:
        ##smd.save_summary(unNormalized=stepMeans, fluxNormalized=stepRatioMeans)
        smd.save_summary(stepMeans)
    smd.done()

    """
    if False:
        meansFileName = "%s/means_%s_c%d_r%d_%s.npy" % (tsp.outputDir, tsp.label, tsp.camera, tsp.run, tsp.exp)
        np.save(meansFileName, np.array(roiMeans))
        logger.info("Wrote file: " + meansFileName)
        fluxesFileName = "%s/fluxes_%s_r%d_%s.npy" % (tsp.outputDir, tsp.label, tsp.run, tsp.exp)
        np.save(fluxesFileNAme, np.array(fluxes))
        logger.info("Wrote file: " + fluxesFileName)
        ##np.save("%s/ratios_c%d_r%d_%s.npy" %(tsp.outputDir, tsp.camera, tsp.run, tsp.exp), np.array(ratios))
        delaysFileName = "%s/delays_%s_c%d_r%d_%s.npy" % (tsp.outputDir, tsp.label, tsp.camera, tsp.run, tsp.exp)
        np.save(delaysFileName, np.array(delays))
        logger.info("Wrote file: " + delaysFileName)
        
        tsp.plotData(ratios, delays, "normalized_signal")
        tsp.plotData(roiMeans, delays, "signal")

        tsp.dumpEventCodeStatistics()
    """
