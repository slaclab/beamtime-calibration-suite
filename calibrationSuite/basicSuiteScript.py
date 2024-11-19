##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
"""
This class acts as an entry-point into the psana-based utility of the library.
(should be used in high-level scripts as follows: 'from calibrationSuite.basicSuiteScript import BasicSuiteScript')
It contains utility functions, analysis functions, and some getters and setters, that can be used with both 'psana1Base' and 'psana2Base'.
"""

import logging
import os

import numpy as np
import psana

logger = logging.getLogger(__name__)

if os.getenv("foo") == "0":
    print("non-psana")
    from calibrationSuite.nonPsanaBase import PsanaBase
elif os.getenv("foo") == "1":
    print("psana1")
    from calibrationSuite.psana1Base import PsanaBase
else:
    print("psana2")
    from calibrationSuite.psana2Base import PsanaBase


class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType="scan"):
        super().__init__(analysisType)

        print("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        logger.info("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        self.className = self.__class__.__name__

    #### Start of common getter functions ####

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == psana.EvrData.ConfigV7:
                self.evrs.append(key.src())

    def get_config(self):
        self.config = self.ds.env().configStore()

    def getFivePedestalRunInfo(self):
        ## could do load_txt but would require full path so
        if self.det is None:
            self.setupPsana()

        evt = self.getEvt(self.fivePedestalRun)
        self.fpGains = self.det.gain(evt)
        self.fpPedestals = self.det.pedestals(evt)
        self.fpStatus = self.det.status(evt)  ## does this work?
        self.fpRMS = self.det.rms(evt)  ## does this work?

    def getEvtFromRunsTooSmartForMyOwnGood(self):
        for r in self.runRange:
            self.run = r
            self.ds = self.get_ds()
            try:
                evt = next(self.ds.events())
                yield evt
            except Exception:
                continue

    def getEvtFromRuns(self):
        try:  ## can't get yield to work
            evt = next(self.ds.events())
            return evt
        except StopIteration:
            i = self.runRange.index(self.run)
            try:
                self.run = self.runRange[i + 1]
                print("switching to run %d" % (self.run))
                logger.info("switching to run %d" % (self.run))
                self.ds = self.get_ds(self.run)
            except Exception:
                print("have run out of new runs")
                logger.exception("have run out of new runs")
                return None
            ##print("get event from new run")
            evt = next(self.ds.events())
            return evt

    def getRawData(self, evt, gainBitsMasked=True, negativeGain=False):
        frames = self.plainGetRawData(evt)
        if frames is None:
            return None

        nZero = 0
        if not "skipZeroCheck" in dir(self):
            nZero = frames.size - np.count_nonzero(frames)
        try:
            dz = self.nZero - nZero
            if dz != 0:
            ##if abs(dz) > 10: ## add a flag for just epixM...
                print("found %d new zero pixels, expected %d, setting frame to None, size was %d" % (dz, self.nZero, frames.size))
                return None
        except Exception:
            self.nZero = nZero
            print("Starting with %d zero pixels, will maybe require exactly that many for this run, size is %d" % (nZero, frames.size))

            try:
                self.dumpEpixMHeaderInfo(evt)
            except Exception:
                pass

        if False and self.special:  ## turned off for a tiny bit of speed
            if "thirteenBits" in self.special:
                frames = frames & 0xFFFE
                ##print("13bits")
            elif "twelveBits" in self.special:
                frames = frames & 0xFFFC
                ##print("12bits")
            elif "elevenBits" in self.special:
                frames = frames & 0xFFF8
                ##print("11bits")
            elif "tenBits" in self.special:
                frames = frames & 0xFFF0
                ##print("10bits")

        if self.negativeGain or negativeGain:
            zeroPixels = frames == 0
            maskedData = frames & self.gainBitsMask
            gainData = frames - maskedData
            frames = gainData + self.gainBitsMask - maskedData
            frames[zeroPixels] = 0

        if gainBitsMasked:
            return frames & self.gainBitsMask
        return frames

    def addFakePhotons(self, frames, occupancy, E, width):
        shape = frames.shape
        occ = np.random.random(shape)
        fakes = np.random.normal(E, width, shape)
        fakes[occ > occupancy] = 0
        return frames + fakes, (fakes > 0).sum()

    #### End of common getter functions ####

    #### Start of common setter functions ####

    def setROI(self, roiFile=None, roi=None):
        """Call with both file name and roi to save roi to file and use,
        just name to load,
        just roi to set for current job"""
        if roiFile is not None:
            if roi is None:
                self.ROIfile = roiFile
                self.ROI = np.load(roiFile)
                return
            else:
                np.save(roiFile, roi)
        self.ROI = roi

    #### End of common setter functions ####

    #### Start of common utility functions ####

    def sortArrayByList(self, a, data):
        return [x for _, x in sorted(zip(a, data), key=lambda pair: pair[0])]

    def sliceToDetector(self, sliceRow, sliceCol):  ## cp from AnalyzeH5: import?
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

    def getNswitchedPixels(self, data, region=None):
        return ((data >= self.g0cut) * 1).sum()

    def getSwitchedPixels(self, data, region=None):
        return data >= self.g0cut

    def dumpEventCodeStatistics(self):
        print(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )
        logger.info(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )

    def isBeamEvent(self, evt):
        if self.ignoreEventCodeCheck:
            return True
        ec = self.getEventCodes(evt)
        ##print(ec[280], ec[281], ec[282], ec[283], ec[284], ec[285] )
        if ec[self.runCode]:
            self.nRunCodeEvents += 1
        if ec[self.daqCode]:
            self.nDaqCodeEvents += 1
            if self.fakeBeamCode:
                return True
        if ec[self.beamCode]:
            self.nBeamCodeEvents += 1
            return True
        ## for FEE, ASC, ...
        return self.fakeBeamCode  ##False

    #### End of common utility functions ####

    #### Start of analysis/correction functions ####

    def noCommonModeCorrection(self, frames):
        return frames

    def regionCommonModeCorrection(self, frame, region, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        regionCM = np.median(frame[region][frame[region] < arbitraryCut])
        return frame - regionCM

    def rowCommonModeCorrection3d(self, frames, arbitraryCut=1000):
        for module in self.analyzedModules:
            frames[module] = self.rowCommonModeCorrection(frames[module], arbitraryCut)
        return frames

    def colCommonModeCorrection3d(self, frames, cut=1000, switchedPixels = None
):
        if switchedPixels is None:
            switchedPixels = self.getSwitchedPixels(frames)
            
        for module in self.analyzedModules:
            sp = None
            if switchedPixels is not None: ## dumb as written
                sp  = switchedPixels[module]
            frames[module] = self.colCommonModeCorrection(frames[module], cut, sp)
        return frames

    def rowCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d object
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        for r in range(self.detectorInfo.nRows):
            colOffset = 0
            for b in range(0, self.detectorInfo.nBanksCol):
                ##for b in range(0, 2):
                try:
                    rowCM = np.median(
                        frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank][
                            frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank] < arbitraryCut
                        ]
                    )
                    if not np.isnan(rowCM):  ## no pixels found under cut
                        frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank] -= rowCM
                except Exception:
                    print("rowCM problem")
                    logger.error("rowCM problem")
                    print(frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank])
                colOffset += self.detectorInfo.nColsPerBank
        return frame

    def colCommonModeCorrection(self, frame, cut=1000, switchedPixels=None):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        ##rand = np.random.random()

        for c in range(self.detectorInfo.nCols):
            rowOffset = 0
            for b in range(0, self.detectorInfo.nBanksRow):
                try:
                    testPixels = np.s_[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c]
                    relevantPixels = frame[testPixels] < cut
                    if switchedPixels is not None:
                        ##print(testPixels, relevantPixels)
                        relevantPixels = np.bitwise_and(relevantPixels, ~switchedPixels[testPixels])
                    colCM = np.median(frame[testPixels][relevantPixels])
                    if not np.isnan(colCM):  ## if no pixels < cut we get nan
                        if False:
                            if c < 100:
                                self.commonModeVals.append(colCM)
                        if colCM > cut:
                            raise Exception("overcorrection: colCM, cut:", colCM, cut)
                        frame[testPixels] -= colCM
                except Exception:
                    print("colCM problem")
                    logger.error("colCM problem")
                    print(frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank], c)
                rowOffset += self.detectorInfo.nRowsPerBank
        return frame

    #### End of analysis/correction functions ####
