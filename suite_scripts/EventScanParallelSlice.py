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

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator

import calibrationSuite.loggingSetup as ls
from calibrationSuite.basicSuiteScript import BasicSuiteScript

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(
    "../logs/" + currFileName[:-3] + ".log", logging.ERROR
)  # change to logging.INFO for full logging output


class EventScanParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__("misc")  ##self)
        logging.info("Output dir: " + self.outputDir)

    def plotData(self, rois, pixels, eventNumbers, dPulseId, label):
        if "timestamp" in label:
            xlabel = "Timestamp (s)"
            ##xlabel = 'Timestamp (scaled to separation)'
        else:
            xlabel = "Event number"
        print(xlabel, label)

        for i, roi in enumerate(self.ROIs):
            ##data[i] -= data[i].mean()
            ax = plt.subplot()
            ##ax.plot(eventNumbers,data[i], label=self.ROIfileNames[i])
            ax.scatter(eventNumbers, rois[i], label=self.ROIfileNames[i])
            plt.grid(which="major", linewidth=0.5)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel(xlabel)
            plt.ylabel("Mean (ADU)")
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
            logger.info("Wrote file: " + figFileName)
            plt.savefig(figFileName)
            plt.clf()

        for i, roi in enumerate(self.ROIs):
            ax = plt.subplot()
            ##ax.plot(eventNumbers, data[i], label=self.ROIfileNames[i])
            ax.scatter(eventNumbers, rois[i], label=self.ROIfileNames[i])
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel(xlabel)
            plt.ylabel("Mean (ADU)")
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
            logger.info("Wrote file: " + figFileName)
            plt.savefig(figFileName)
            plt.clf()
        # plt.show()

        for i, p in enumerate(self.singlePixels):
            ax = plt.subplot()
            ##ax.plot(eventNumbers, pixels[i], label=str(p))
            ##ax.scatter(eventNumbers, pixels[i], marker='.', label=str(p))
            ax.plot(eventNumbers, pixels[i], ".", ms=1, label=str(p))
            ax.plot(eventNumbers[:-1][dPulseId < 7740], pixels[i][:-1][dPulseId < 7740], "r.", ms=1, label=str(p))
            ##ax.scatter(eventNumbers, pixels[i], marker='.', s=1, label=str(p))
            plt.xlabel(xlabel)
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
            logger.info("Wrote file: " + figFileName)
            plt.close()

            if True:
                ax = plt.subplot()
                ax.hist(pixels[i], 100, range=[pixels[i].min().astype("int"), pixels[i].max().astype("int")])
                plt.xlabel("Pixel ADU")
                plt.title("Event scan projection of pixel %d" % (i))
                plt.yscale("log")
                pltFileName = "%s/%s_r%d_c%d_%s_pixel%d_hist.png" % (
                    self.outputDir,
                    self.__class__.__name__,
                    self.run,
                    self.camera,
                    label,
                    i,
                )
                plt.savefig(pltFileName)
                logger.info("Wrote file: " + pltFileName)
                plt.close()

    # not working or used atm...
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

    def analyze_h5(self, dataFile, label):
        data = h5py.File(dataFile)
        print(data.keys())

        ts = data["timestamps"][()]
        print("ts: ", ts)

        pulseIds = data["pulseIds"][()]
        pixels = data["pixels"][()]
        try:
            rois = data["rois"][()]
        except Exception:
            rois = None

        # get summedBitSlice and save it to a numpy file
        try:
            bitSlice = data["summedBitSlice"][()]
            npyFileName = "%s/bitSlice_c%d_r%d_%s.npy" % (self.outputDir, self.camera, self.run, self.exp)
            logger.info("Wrote file: " + npyFileName)
            np.save(npyFileName, np.array(bitSlice))
        except Exception:
            pass

        # sort and save pulseIds to a numpy file
        pulseIds.sort()
        npyFileName = "%s/pulseIds_c%d_r%d_%s.npy" % (self.outputDir, self.camera, self.run, self.exp)
        logger.info("Wrote file: " + npyFileName)
        np.save(npyFileName, np.array(pulseIds))
        dPulseId = pulseIds[1:] - pulseIds[0:-1]

        # sort pixels and rois based on timestamps
        pixels = self.sortArrayByList(ts, pixels)
        if rois is not None:
            rois = self.sortArrayByList(ts, rois)

        ts.sort()
        ts = ts - ts[0]
        ##ts = ts/np.median(ts[1:]-ts[0:-1])
        print("ts: ", ts)
        self.plotData(np.array(rois).T, np.array(pixels).T, ts, dPulseId, "timestamps" + label)


if __name__ == "__main__":
    esp = EventScanParallel()
    print("have built a " + esp.className + "class")
    logger.info("have built a " + esp.className + "class")

    if esp.file is not None:
        esp.analyze_h5(esp.file, esp.label)
        print("done with standalone analysis of %s, exiting" % (esp.file))
        logger.info("done with standalone analysis of %s, exiting" % (esp.file))
        sys.exit(0)

    esp.setupPsana()
    if esp.psanaType == 1:  ## move to psana1Base asap
        from psana import EventId

    try:
        ##skip_283_check = "skip283" in esp.special
        skip_283_check = "fakeBeamCode" in esp.special
    except Exception:
        skip_283_check = False  ## for not running at MFX

    zeroLowGain = False
    zeroHighGain = False
    if esp.special:
        if "zeroLowGain" in esp.special:
            zeroLowGain = True
        elif "zeroHighGain" in esp.special:
            zeroHighGain = True

    size = 666
    h5FileName = "%s/%s_c%d_r%d_%s_n%d.h5" % (esp.outputDir, esp.className, esp.camera, esp.run, esp.label, size)
    if esp.psanaType == 1:
        smd = esp.ds.small_data(filename=h5FileName, gather_interval=100)
    else:
        smd = esp.ds.smalldata(filename=h5FileName)

    esp.nGoodEvents = 0
    roiMeans = [[] for i in esp.ROIs]
    pixelValues = [[] for i in esp.singlePixels]
    eventNumbers = []
    bitSliceSum = None
    try:
        evtGen = esp.myrun.events()
    except Exception:
        evtGen = esp.ds.events()

    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
        ec = esp.getEventCodes(evt)
        if not skip_283_check:
            if not esp.isBeamEvent(evt):
                ##print(ec)
                continue
        frames = esp.getRawData(evt, gainBitsMasked=True)
        if zeroLowGain or zeroHighGain:
            frames = esp.getRawData(evt, gainBitsMasked=False)
            if zeroLowGain:
                gainFilter = frames >= esp.g0cut
            else:
                gainFilter = ~(frames >= esp.g0cut)
            frames[gainFilter] = 0
            frames = frames & esp.gainBitsMask

        if frames is None:
            ##print("no frame")
            continue
        if esp.fakePedestal is not None:
            frames = frames.astype("float") - esp.fakePedestal
            if zeroLowGain or zeroHighGain:
                frames[gainFilter] = 0

            if esp.special is not None and "crazyModeForDionisio" in esp.special:
                print("crazy mode for Dionisio")
                plt.imshow(np.vstack(frames[1:3].clip(-500, 500)))
                plt.colorbar()
                plt.show()

            ##print(esp.fakePedestalFrame[tuple(esp.singlePixels[2])])
            ##print(frames[tuple(esp.singlePixels[2])])

            if esp.special is not None and "rowCommonMode" in esp.special:
                frames = esp.rowCommonModeCorrection3d(frames, 3.0)
            if esp.special is not None and "colCommonMode" in esp.special:
                frames = esp.colCommonModeCorrection3d(frames, 3.0)
            if esp.special is not None and "regionCommonMode" in esp.special:
                ##oldFrames = frames
                frames = esp.regionCommonModeCorrection(frames, esp.regionSlice, 3.0)
                ##print(frames-oldFrames)
        else:
            if esp.special is not None and "regionCommonMode" in esp.special:
                frames = np.array([esp.regionCommonModeCorrection(frames, esp.regionSlice, 666666)])

        eventNumbers.append(nevt)
        for i, roi in enumerate(esp.ROIs):
            m = frames[roi > 0].mean()
            roiMeans[i].append(m)

        for i, roi in enumerate(esp.singlePixels):
            pixelValues[i].append(frames[tuple(esp.singlePixels[i])])

        if esp.fakePedestal is None:
            slice = frames[esp.regionSlice].astype("uint16")
            sliceView = slice.view(np.uint8).reshape(slice.size, 2)
            r = np.unpackbits(sliceView, axis=1, bitorder="little")[:, ::-1]

            try:
                bitSliceSum += r
            except Exception:
                bitSliceSum = r.astype(np.uint32)

        ##parityTest = esp.getPingPongParity(frames[0][144:224, 0:80])
        ##print(frames[tuple(esp.singlePixels[0])], parityTest)

        if esp.psanaType == 1:
            t = evt.get(EventId).time()
            timestamp = t[0] + t[1] / 1000000000.0
            pulseId = 0
        else:
            timestamp = evt.datetime().timestamp()
            pulseId = esp.getPulseId(evt)
            if pulseId == 0:
                pulseId = timestamp ## better than nothing
        smdDict = {
            "timestamps": timestamp,
            "pulseIds": pulseId,
            "pixels": np.array([pixelValues[i][-1] for i in range(len(esp.singlePixels))]),
        }
        rois = np.array(None)  ## might not be defined, and smd doesn't like (0,)
        if esp.ROIs != []:
            smdDict["rois"] = np.array([roiMeans[i][-1] for i in range(len(esp.ROIs))])

        if esp.psanaType == 1:
            smd.event(**smdDict)
        else:
            smd.event(evt, **smdDict)

        esp.nGoodEvents += 1
        if esp.nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (esp.nGoodEvents))
            logger.info("n good events analyzed: %d" % (esp.nGoodEvents))

        if esp.nGoodEvents > esp.maxNevents:
            break

    print(esp.outputDir)
    npyFileName = "%s/means_c%d_r%d_%s.npy" % (esp.outputDir, esp.camera, esp.run, esp.exp)
    np.save(npyFileName, np.array(roiMeans))
    logger.info("Wrote file: " + npyFileName)

    npyFileName = "%s/eventNumbers_c%d_r%d_%s.npy" % (esp.outputDir, esp.camera, esp.run, esp.exp)
    np.save(npyFileName, np.array(eventNumbers))
    logger.info("Wrote file: " + npyFileName)
    ##esp.plotData(roiMeans, pixelValues, eventNumbers, None, "foo")

    if (esp.psanaType == 1 or smd.summary) and esp.fakePedestal is None:
        allSum = smd.sum(bitSliceSum)
        if esp.psanaType == 1:
            smd.save({"summedBitSlice": allSum})
        else:
            smd.save_summary({"summedBitSlice": allSum})
    if esp.psanaType != 1:
        smd.done()
    logger.info("Wrote file: " + h5FileName)
