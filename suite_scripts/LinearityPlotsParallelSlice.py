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

import calibrationSuite.ancillaryMethods as ancillaryMethods
import calibrationSuite.fitFunctions as fitFunctions
import calibrationSuite.loggingSetup as ls
import h5py
import matplotlib.pyplot as plt
import numpy as np
from calibrationSuite.basicSuiteScript import BasicSuiteScript
from scipy.optimize import curve_fit

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(
    "../logs/" + currFileName[:-3] + ".log", logging.INFO
)  # change to logging.INFO for full logging output

## This builds and analyzes a dict with keys:
## 'rois' - ROI fluxes and means
## 'g0s' -per-pixel g0 fluxes and values, ragged or None-filled
## ditto with 1


class LinearityPlotsParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__("scan")  ##self)
        self.saturated = [True, False][1]
        print("using saturation fit =", self.saturated)
        logger.info("using saturation fit =" + str(self.saturated))
        self.residuals = [True, False][0]
        self.profiles = [True, False][0]
        self.seabornProfiles = [True, False][0]
        try:
            print("positive events:", "positive" in self.special)
            logger.info("positive events:" + str("positive" in self.special))

        except Exception:
            pass

    def plotAutorangingData(self, g0s, g1s, g0Fluxes, g1Fluxes, label):
        ## this is just be for single pixels
        ## index in case that's ever supported
        ## only really makes sense as calib
        for i, p in enumerate(self.singlePixels):
            if len(g0s[i]) > 0:
                plt.scatter(g0Fluxes[i], g0s[i], c="r", marker=".", s=1)
            if len(g1s[i]) > 0:
                plt.scatter(g1Fluxes[i], g1s[i], c="b", marker=".", s=1)
            plt.xlabel(self.fluxLabel)
            if "raw" in label:
                plt.ylabel("Red medium, blue low (ADU)")
            else:
                plt.ylabel("Red medium, blue low (keV)")
            if "yClip" in label:
                plt.ylim(0, 4000)
            if "xClip" in label:
                if len(g1Fluxes[i]) > 0:
                    plt.xlim(g1Fluxes[i].min() * 0.95, max(g1Fluxes[i].max(), g1Fluxes[i].max()) * 1.05)
                else:
                    plt.close()
                    return
                ##lot of hackiness here

            plt.title(label)
            figFileName = "%s/%s_p%d_r%d_c%d_%s.png" % (self.outputDir, self.className, i, self.run, self.camera, label)
            plt.savefig(figFileName)
            plt.close()

    def plotAutorangingData_profile(self, g0s, g1s, g0Fluxes, g1Fluxes, label, partialMode=None, order=1):
        ## this is just for single pixels
        ## index in case that's ever supported

        import seaborn as sns

        for i, p in enumerate(self.singlePixels):
            fig, ax = plt.subplots()
            if partialMode != 1 and len(g0s[i]) > 0:
                x = g0Fluxes[i]
                y = g0s[i]
                ##yMaxPlot = y.max()
                sns.regplot(
                    x=x, y=y, x_bins=40, marker=".", ax=ax, order=order, truncate=True
                )  ##add fit_reg=None for no plot
                ## truncate added to keep epixM plot lines from messing with y limits
            if partialMode != 0 and len(g1s[i]) > 0:
                x = g1Fluxes[i]
                y = g1s[i]
                ##try:## using truncate instead
                ##yMaxPlot = max(y.max(), yMaxPlot)
                ##except:
                    ##yMaxPlot = y.max()
                sns.regplot(
                    x=x, y=y, x_bins=40, marker=".", ax=ax, order=order, truncate=True
                )  ##add fit_reg=None for no plot
            plt.xlabel(self.fluxLabel)

            if "raw" in label:
                plt.ylabel("Red medium, blue low (ADU)")
            else:
                plt.ylabel("Red medium, blue low (keV)")
            if "yClip" in label:
                plt.ylim(0, 4000)
            if "xClip" in label:
                if len(g1Fluxes[i]) > 0:
                    plt.xlim(g1Fluxes[i].min() * 0.95, max(g1Fluxes[i].max(), g1Fluxes[i].max()) * 1.05)
                else:
                    plt.close()
                    return
                ##lot of hackiness here

            plt.title(label + "_profile")
            figFileName = "%s/%s_p%d_mod%d_row%d_col%d_r%d_c%d_%s_profile.png" % (
                self.outputDir,
                self.className,
                i,
                p[0],
                p[1],
                p[2],
                self.run,
                self.camera,
                label,
            )
            plt.savefig(figFileName)
            plt.close()

    def plotDataROIs(self, means, flux, label, raw=True):
        ## assume no autoranging
        ## raw or calib
        if raw:
            ylabel = "ADU"
        else:
            ylabel = "keV"
        for i, roi in enumerate(self.ROIs):
            plt.scatter(flux, means[i], marker=".")
            plt.xlabel(self.fluxLabel)
            plt.ylabel("detector ROI mean (%s)" % (ylabel))
            figFileName = "%s/%s_roi%d_r%d_c%d_%s.png" % (
                self.outputDir,
                self.className,
                i,
                self.run,
                self.camera,
                label,
            )
            plt.savefig(figFileName)
            plt.close()

    def analyze_h5(self, dataFile, label):
        data = h5py.File(dataFile)
        fluxes = data["fluxes"][()]
        print(fluxes)
        rois = data["rois"][()]
        pixels = data["pixels"][()]
        g0s = []
        g0Fluxes = []
        g1s = []
        g1Fluxes = []
        for s, _ in enumerate(self.singlePixels):
            g0s.append(pixels[:, s, 1][pixels[:, s, 0] == 0])
            g0Fluxes.append(fluxes[pixels[:, s, 0] == 0])
            g1s.append(pixels[:, s, 1][pixels[:, s, 0] == 1])
            g1Fluxes.append(fluxes[pixels[:, s, 0] == 1])

        if self.seabornProfiles:
            lpp.plotAutorangingData_profile(g0s, g1s, g0Fluxes, g1Fluxes, label)
            for order in [1, 2]:
                ##for order in [1]:
                lpp.plotAutorangingData_profile(
                    g0s, g1s, g0Fluxes, g1Fluxes, label + "highOrMed_poly%d" % (order), partialMode=0, order=order
                )
                lpp.plotAutorangingData_profile(
                    g0s, g1s, g0Fluxes, g1Fluxes, label + "low_poly%d" % (order), partialMode=1, order=order
                )
                lpp.plotAutorangingData(g0s, g1s, g0Fluxes, g1Fluxes, label)
                ##lpp.plotAutorangingData(g0s,g1s, g0Fluxes, g1Fluxes, label+"_yClip_xClip")
        lpp.plotDataROIs(rois.T, fluxes, "ROIs")

    def analyze_h5_slice(self, dataFile, label):
        module = 2
        nModules = 3
        data = h5py.File(dataFile)
        fluxes = data["fluxes"][()]
        pixels = data["slice"][()]
        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        if self.fitInfo is None:
            self.fitInfo = np.zeros(
                (nModules, rows, cols, 13)
            )  ##g0 slope, intercept, r2; g1 x3; max, min, g0Ped, g1Ped, g0Gain, g1Gain, offset

        for module in [1, 2]:
            for i in range(rows):
                for j in range(cols):
                    iDet, jDet = self.sliceToDetector(i, j)
                    if False:
                        self.fitInfo[module, i, j, 8] = self.g0Ped[module, iDet, jDet]
                        self.fitInfo[module, i, j, 9] = self.g1Ped[module, iDet, jDet]
                        self.fitInfo[module, i, j, 10] = self.g0Gain[module, iDet, jDet]
                        self.fitInfo[module, i, j, 11] = self.g1Gain[module, iDet, jDet]
                        self.fitInfo[module, i, j, 12] = self.offset[module, iDet, jDet]
                    g0 = pixels[:, module, i, j] < lpp.g0cut
                    g1 = np.logical_not(g0)
                    if len(g0[g0]) > 2:
                        y = np.bitwise_and(pixels[:, module, i, j][g0], lpp.gainBitsMask)
                        y_g0_max = y.max()
                        x = fluxes[g0]
                        if self.profiles:
                            x, y, err = ancillaryMethods.makeProfile(x, y, 50, myStatistic="median")
                            if x is None:  ##empty plot if single points/bin apparently
                                print("empty profile for %d, %d" % (i, j))
                                logger.info("empty profile for %d, %d" % (i, j))
                                continue
                        if x is not None:
                            fitPar, covar, fitFunc, r2 = fitFunctions.fitLinearUnSaturatedData(x, y, saturated=self.saturated)
                            if True:
                                if i%10==0 and j%10==0:
                                    print(i, j, fitPar, r2, 0)
                            ##np.save("temp_r%dc%d_x.py" %(i,j), fluxes[g0])
                            ##np.save("temp_r%dc%d_y.py" %(i,j), y)
                            ##np.save("temp_r%dc%d_func.py" %(i,j), fitFunc)
                            ##print(fitInfo.shape)
                            ##print(fitPar)
                            self.fitInfo[module, i, j, 0:2] = fitPar[0:2]  ## indices for saturated case
                            self.fitInfo[module, i, j, 2] = r2
                            self.fitInfo[module, i, j, 6] = y_g0_max
                            if i % 2 == 0 and i == j:
                                plt.figure(1)
                                plt.scatter(x, y, zorder=1, marker=".", s=1)
                                if self.saturated:
                                    plt.scatter(x, fitFunc, color="k", zorder=2, s=1)
                                else:
                                    plt.plot(x, fitFunc, color="k", zorder=2)
                                if self.profiles:
                                    plt.errorbar(x, y, err)
                                if self.residuals:
                                    plt.figure(2)
                                    plt.scatter(x, y - fitFunc, color="k", zorder=2, s=1)
                                    plt.figure(1)

                    if len(g1[g1]) > 2:
                        y = np.bitwise_and(pixels[:, module, i, j][g1], lpp.gainBitsMask)
                        y_g1_min = y.min()
                        x = fluxes[g1]
                        if self.profiles:
                            x, y, err = ancillaryMethods.makeProfile(x, y, 50)
                            if x is None:  ##empty plot if single points/bin apparently
                                print("empty profile for %d, %d" % (i, j))
                                logger.info("empty profile for %d, %d" % (i, j))
                        if x is not None:
                            fitPar, covar, fitFunc, r2 = fitFunctions.fitLinearUnSaturatedData(x, y)
                            print(i, j, fitPar, r2, 1)
                            self.fitInfo[module, i, j, 3:5] = fitPar
                            self.fitInfo[module, i, j, 5] = r2
                            self.fitInfo[module, i, j, 7] = y_g1_min
                            if i % 2 == 0 and i == j:
                                plt.scatter(x, y, zorder=3, marker=".")
                                plt.plot(x, fitFunc, color="k", zorder=4)
                                if self.profiles:
                                    plt.errorbar(x, y, err)
                                if self.residuals:
                                    plt.figure(2)
                                    plt.scatter(x, y - fitFunc, zorder=3, marker=".")
                                    plt.figure(1)

<<<<<<< HEAD
                    if i % 2 == 0 and i == j:
                        figFileName = "%s/%s_slice_m%d_r%d_c%d_r%d_c%d_%s.png" % (self.outputDir, self.className, module, i, j, self.run, self.camera, label)
=======
                if i % 2 == 0 and i == j:
                    figFileName = "%s/%s_slice_%d_%d_r%d_c%d_%s.png" % (
                        self.outputDir,
                        self.className,
                        i,
                        j,
                        self.run,
                        self.camera,
                        label,
                    )
                    plt.savefig(figFileName)
                    logger.info("Wrote file: " + figFileName)
                    plt.close()
                    if self.residuals:
                        plt.figure(2)
                        figFileName = "%s/%s_slice_%d_%d_r%d_c%d_residuals_%s.png" % (
                            self.outputDir,
                            self.className,
                            i,
                            j,
                            self.run,
                            self.camera,
                            label,
                        )
>>>>>>> 7227771506c6eb7fcf01086cf40746763a0c61c1
                        plt.savefig(figFileName)
                        logger.info("Wrote file: " + figFileName)
                        plt.close()
                        if self.residuals:
                            plt.figure(2)
                            figFileName = "%s/%s_slice_m%d_r%d_c%d_r%d_c%d_residuals_%s.png" % (self.outputDir, self.className, module, i, j, self.run, self.camera, label)
                            plt.savefig(figFileName)
                            logger.info("Wrote file: " + figFileName)
                            plt.close()

        npyFileName = "%s/%s_r%d_sliceFits_%s.npy" % (self.outputDir, self.className, self.run, label)
        np.save(npyFileName, self.fitInfo)  ## fix this to be called once
        ## not once per module
        logger.info("Wrote file: " + npyFileName)


if __name__ == "__main__":
    lpp = LinearityPlotsParallel()
    print("have built an LPP")
    logger.info("have built an LPP")
    lpp.useNswitchedAsFlux = False
    lpp.fluxLabel = "wave8 flux (ADU)" 
    if lpp.special is not None and 'useNswitchedAsFlux' in lpp.special:
        lpp.useNswitchedAsFlux = True
        lpp.fluxLabel = "number of low-gain pixels"

    noSwitchedOnly = lpp.special is not None and 'noSwitchedOnly' in lpp.special

    print("using switched pixels as flux? only events with no switch?",
          lpp.useNswitchedAsFlux, noSwitchedOnly)
    
    if lpp.file is not None:
        print("using flux label:", lpp.fluxLabel)
        lpp.fitInfo = None
        lpp.analyze_h5(lpp.file, lpp.label + "_raw")
        lpp.analyze_h5_slice(lpp.file, lpp.label + "_raw")
        print("done with standalone analysis of %s, exiting" % (lpp.file))
        logger.info("done with standalone analysis of %s, exiting" % (lpp.file))
        sys.exit(0)

    doKazFlux = False
    if doKazFlux:
        print("doing Kaz flux events")
        logger.info("doing Kaz flux events")
    else:
        print("not doing Kaz events")
        logger.info("not doing Kaz events")


    lpp.setupPsana()

    size = 666
    smd = lpp.ds.smalldata(
        filename="%s/%s_%s_c%d_r%d_n%d.h5" % (lpp.outputDir, lpp.className, lpp.label, lpp.camera, lpp.run, size)
    )

    nGoodEvents = 0
    fluxes = []  ## common for all ROIs
    roiMeans = [[] for i in lpp.ROIs]
    g0s = [[] for i in lpp.singlePixels]
    g1s = [[] for i in lpp.singlePixels]
    g0Fluxes = [[] for i in lpp.singlePixels]
    g1Fluxes = [[] for i in lpp.singlePixels]

    evtGen = lpp.myrun.events()
    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
        doFast = True  ##False ## for 2400 etc Hz
        if doFast:
            ec = lpp.getEventCodes(evt)
            beamEvent = lpp.isBeamEvent(evt)
            if ec[137]:
                lpp.flux = lpp._getFlux(evt)  ## fix this
                lpp.fluxTS = lpp.getTimestamp(evt)
                ##print("found flux", lpp.flux)
                continue
                # frames = lpp.det.calib(evt)
                ##frames = lpp.det.raw(evt)&0x3fff
            ##elif ec[281]:
            elif beamEvent:
                lpp.framesTS = lpp.getTimestamp(evt)
                rawFrames = lpp.getRawData(evt, gainBitsMasked=False)
                frames = lpp.getCalibData(evt)
            else:
                continue
        else:
            lpp.flux = lpp._getFlux(evt)  ## fix this
            lpp.frameTS = lpp.getTimestamp(evt)
            rawFrames = lpp.getRawData(evt, gainBitsMasked=False)
            frames = lpp.getCalibData(evt)

        if rawFrames is None:
            print("No contrib found")
            logger.info("No contrib found")
            continue
        ## could? should? check for calib here I guess
        if lpp.special is not None and "parity" in lpp.special:
            if lpp.getPingPongParity(rawFrames[0][144:224, 0:80]) == ("negative" in lpp.special):
                continue
            ##print(nevt)

        flux = lpp.getFlux(evt)
        if flux is None:
            print("no flux found")
            logger.info("no flux found")
            continue
        delta = lpp.framesTS - lpp.fluxTS
        if delta > 1000:
            ## probably not relevant when checking isBeamEvent
            print("frame - bld timestamp delta too large:", delta)
            logger.info("frame - bld timestamp delta too large:" + str(delta))
            continue

        if lpp.useNswitchedAsFlux:
            flux = lpp.getNswitchedPixels(rawFrames)
            ##print("nSwitched:", flux)
        elif noSwitchedOnly:
            nSwitched = lpp.getNswitchedPixels(rawFrames)
            if nSwitched > 0:
                ##print('nSwitched: %d' %(nSwitched))
                continue
            
        roiMeans = []
        for i, roi in enumerate(lpp.ROIs):
            ##m = np.multiply(roi, frames).mean()
            m = frames[roi == 1].mean()
            roiMeans.append(m)

        if doKazFlux:
            rf = rawFrames[tuple(lpp.singlePixels[0])]
            if not (flux < 20000 and rf >= lpp.g0cut and rf > 2950):
                ##not a Kaz event
                nGoodEvents += 1
                if nGoodEvents > lpp.maxNevents:
                    break
                continue

        singlePixelData = []
        for j, p in enumerate(lpp.singlePixels):
            singlePixelData.append([int(rawFrames[tuple(p)] >= lpp.g0cut), rawFrames[tuple(p)] & lpp.gainBitsMask])

        eventDict = {'fluxes':flux,
                     'rois':np.array(roiMeans),
                     'pixels':np.array(singlePixelData),
                     'slice':rawFrames[lpp.regionSlice]
        }
        
        smd.event(
            evt,
<<<<<<< HEAD
            eventDict
=======
            fluxes=flux,
            rois=np.array(roiMeans),
            pixels=np.array(singlePixelData),
            slice=rawFrames[lpp.regionSlice],
>>>>>>> 7227771506c6eb7fcf01086cf40746763a0c61c1
        )

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            logger.info("n good events analyzed: %d" % (nGoodEvents))
        ##            print("switched pixels: %d" %((switchedPixels>0).sum()))

        if nGoodEvents > lpp.maxNevents:
            break

    if False:
        fileName = "%s/%s_%s_means_r%d_c%d_%s.npy" % (
            lpp.outputDir,
            lpp.className,
            lpp.label,
            lpp.run,
            lpp.camera,
            lpp.exp,
        )
        np.save(fileName, roiMeans)
        logger.info("Wrote file: " + fileName)

        fileName = "%s/%s_%s_fluxes_r%d_c%d_%s.npy" % (
            lpp.outputDir,
            lpp.className,
            lpp.label,
            lpp.run,
            lpp.camera,
            lpp.exp,
        )
        np.save(fileName, fluxes)
        logger.info("Wrote file: " + fileName)

        fileName = "%s/%s_%s_singlePixel_g0s_r%d_c%d_%s.npy" % (
            lpp.outputDir,
            lpp.className,
            lpp.label,
            lpp.run,
            lpp.camera,
            lpp.exp,
        )
        np.save(fileName, g0s)
        logger.info("Wrote file: " + fileName)

        fileName = "%s/%s_%s_singlePixel_g1s_r%d_c%d_%s.npy" % (
            lpp.outputDir,
            lpp.className,
            lpp.label,
            lpp.run,
            lpp.camera,
            lpp.exp,
        )
        np.save(fileName, g1s)
        logger.info("Wrote file: " + fileName)
        np.save(
            "%s/%s_%s_g0Fluxes_r%d_c%d_%s.npy"
            % (lpp.outputDir, lpp.className, lpp.label, lpp.run, lpp.camera, lpp.exp),
            g0Fluxes,
        )
        logger.info("Wrote file: " + fileName)

        fileName = "%s/%s_%s_g1Fluxes_r%d_c%d_%s.npy" % (
            lpp.outputDir,
            lpp.className,
            lpp.label,
            lpp.run,
            lpp.camera,
            lpp.exp,
        )
        np.save(fileName, g1Fluxes)
        logger.info("Wrote file: " + fileName)

    """
    if False:
        print("this is broken")
        label = "rawInTimeDot"
        if doKazFlux:
            label = "raw_smarterPoints"
            label += "_kazEventsNear"
        lpp.plotAutorangingData(g0s, g1s, g0Fluxes, g1Fluxes, label)
        lpp.plotAutorangingData(g0s, g1s, g0Fluxes, g1Fluxes, label + "_yClip_xClip")
        lpp.plotDataROIs(roiMeans, fluxes, "roiTest")
    """

    smd.done()

    lpp.dumpEventCodeStatistics()
