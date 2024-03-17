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
import logging

# for logging from current file
logger = logging.getLogger(__name__)

import calibrationSuite.loggingSetup as ls
import os

# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging(currFileName[:-3] + ".log", logging.ERROR)  # change to logging.INFO for full logging output


class EventScanParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__("misc")  ##self)
        self.only283 = [True, False][0]  ## special beam event code
        print("only analyzing event code 283 flag set to", self.only283)

        logging.info("Output dir: " + self.outputDir)

    def plotData(self, data, pixels, eventNumbers, dPulseId, label):
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
            ax.scatter(eventNumbers, data[i], label=self.ROIfileNames[i])
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
            ax.scatter(eventNumbers, data[i], label=self.ROIfileNames[i])
            plt.grid(which="major", linewidth=0.75)
            minor_locator = AutoMinorLocator(5)
            ax.xaxis.set_minor_locator(minor_locator)
            plt.grid(which="minor", linewidth=0.5)
            plt.xlabel(xlabel)
            plt.ylabel("Mean (ADU)")
            ##plt.yscale('log')
            plt.legend(loc="upper right")

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

    def analyze_h5(self, dataFile, label):
        import h5py

        data = h5py.File(dataFile)
        print(data.keys())
        logger.info("keys: " + str(data.keys))
        ts = data["timestamps"][()]
        print(ts)
        pulseIds = data["pulseIds"][()]
        pixels = data["pixels"][()]
        rois = data["rois"][()]

        try:
            bitSlice = data["summedBitSlice"][()]
            npyFileName = "%s/bitSlice_c%d_r%d_%s.npy" % (self.outputDir, self.camera, self.run, self.exp)
            logger.info("Wrote file: " + npyFileName)
            np.save(npyFileName, np.array(bitSlice))
        except:
            pass

        pulseIds.sort()

        npyFileName = "%s/pulseIds_c%d_r%d_%s.npy" % (self.outputDir, self.camera, self.run, self.exp)
        logger.info("Wrote file: " + npyFileName)
        np.save(npyFileName, np.array(pulseIds))
        dPulseId = pulseIds[1:] - pulseIds[0:-1]

        pixels = sortArrayByList(ts, pixels)
        rois = sortArrayByList(ts, rois)
        ts.sort()
        ts = ts - ts[0]
        ##ts = ts/np.median(ts[1:]-ts[0:-1])
        print("ts: ", ts)

        self.plotData(np.array(rois).T, np.array(pixels).T, ts, dPulseId, "timestamps" + label)


if __name__ == "__main__":
    commandUsed = sys.executable + " " + " ".join(sys.argv)
    logger.info("Ran with cmd: " + commandUsed)

    esp = EventScanParallel()
    print("have built a" + esp.className + "class")
    logger.info("have built a" + esp.className + "class")
    if esp.file is not None:
        esp.analyze_h5(esp.file, esp.label)
        print("done with standalone analysis of %s, exiting" % (esp.file))
        logger.info("done with standalone analysis of %s, exiting" % (esp.file))
        sys.exit(0)

    esp.setupPsana()

    h5FileName = "%s/%s_c%d_r%d_n%d.h5" % (esp.outputDir, esp.className, esp.camera, esp.run, size)
    smd = esp.ds.smalldata(filename=h5FileName)

    esp.nGoodEvents = 0
    roiMeans = [[] for i in esp.ROIs]
    pixelValues = [[] for i in esp.singlePixels]
    eventNumbers = []
    bitSliceSum = None
    evtGen = esp.myrun.events()
    for nevt, evt in enumerate(evtGen):
        if evt is None:
            continue
        ec = esp.getEventCodes(evt)
        if esp.only283:
            if not ec[283]:
                ##print(ec)
                continue
        frames = esp.getRawData(evt, gainBitsMasked=True)
        if frames is None:
            ##print("no frame")
            continue
        if esp.fakePedestal is not None:
            frame = frames.astype("float")[0] - esp.fakePedestalFrame
            frames = np.array([frame])
            ##print(esp.fakePedestalFrame[tuple(esp.singlePixels[2])])
            ##print(frames[tuple(esp.singlePixels[2])])

            if esp.special is not None and "rowCommonMode" in esp.special:
                frames = np.array([esp.rowCommonModeCorrection(frame)])
            if esp.special is not None and "colCommonMode" in esp.special:
                frames = np.array([esp.colCommonModeCorrection(frame)])
            if esp.special is not None and "regionCommonMode" in esp.special:
                ##oldFrames = frames
                frames = np.array([esp.regionCommonModeCorrection(frame, esp.regionSlice, 666)])
                ##print(frames-oldFrames)
        else:
            frame = frames.astype('float')[0]
            frames = np.array([frame])
            if esp.special is not None and 'regionCommonMode' in esp.special:
                frames = np.array([esp.regionCommonModeCorrection(frame, esp.regionSlice, 666666)])

        eventNumbers.append(nevt)
        for i, roi in enumerate(esp.ROIs):
            m = frames[roi == 1].mean()
            roiMeans[i].append(m)

        for i, roi in enumerate(esp.singlePixels):
            pixelValues[i].append(frames[tuple(esp.singlePixels[i])])

        if esp.fakePedestal is None:
            slice = frames[0][esp.regionSlice]
            sliceView = slice.view(np.uint8).reshape(slice.size, 2)
            r = np.unpackbits(sliceView, axis=1, bitorder="little")[:, ::-1]

            try:
                bitSliceSum += r
            except:
                bitSliceSum = r.astype(np.uint32)

        ##parityTest = esp.getPingPongParity(frames[0][144:224, 0:80])
        ##print(frames[tuple(esp.singlePixels[0])], parityTest)

        smd.event(
            evt,
            timestamps=evt.datetime().timestamp(),
            pulseIds=esp.getPulseId(evt),
            rois=np.array([roiMeans[i][-1] for i in range(len(esp.ROIs))]),
            pixels=np.array([pixelValues[i][-1] for i in range(len(esp.singlePixels))]),
            ##bitSlice = r
        )

        esp.nGoodEvents += 1
        if esp.nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (esp.nGoodEvents))
            logger.info("n good events analyzed: %d" % (esp.nGoodEvents))

        if esp.nGoodEvents > esp.maxNevents:
            break

    npyFileName = "%s/means_c%d_r%d_%s.npy" % (esp.outputDir, esp.camera, esp.run, esp.exp)
    np.save(npyFileName, np.array(roiMeans))
    logger.info("Wrote file: " + npyFileName)

    npyFileName = "%s/eventNumbers_c%d_r%d_%s.npy" % (esp.outputDir, esp.camera, esp.run, esp.exp)
    np.save(npyFileName, np.array(eventNumbers))
    logger.info("Wrote file: " + npyFileName)
    ##esp.plotData(roiMeans, pixelValues, eventNumbers, None, "foo")

    if smd.summary and esp.fakePedestal is None:
        allSum = smd.sum(bitSliceSum)
        smd.save_summary({"summedBitSlice": allSum})
    smd.done()
    logger.info("Wrote file: " + h5FileName)
