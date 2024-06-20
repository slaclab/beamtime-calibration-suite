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

logger = logging.getLogger(__name__)

if os.getenv("foo") == "1":
    print("psana1")
    from calibrationSuite.psana1Base import PsanaBase
else:
    print("psana2")
    from calibrationSuite.psana2Base import PsanaBase


def sortArrayByList(a, data):
    return [x for _, x in sorted(zip(a, data), key=lambda pair: pair[0])]


class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType="scan"):
        super().__init__()

        print("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        logger.info("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        self.className = self.__class__.__name__

        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}

        self.ds = None
        self.det = None  ## do we need multiple dets in an array? or self.secondDet?

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283  ## per Matt
        ##self.beamCode = 281 ## don't see 283...

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

    def sliceToDetector(self, sliceRow, sliceCol):  ## cp from AnalyzeH5: import?
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

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

    def colCommonModeCorrection3d(self, frames, arbitraryCut=1000):
        for module in self.analyzedModules:
            frames[module] = self.colCommonModeCorrection(frames[module], arbitraryCut)
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
                    frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank] -= rowCM
                except Exception:
                    rowCM = -666
                    print("rowCM problem")
                    logger.error("rowCM problem")
                    print(frame[r, colOffset : colOffset + self.detectorInfo.nColsPerBank])
                colOffset += self.detectorInfo.nColsPerBank
        return frame

    def colCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        ##rand = np.random.random()
        for c in range(self.detectorInfo.nCols):
            rowOffset = 0
            for b in range(0, self.detectorInfo.nBanksRow):
                try:
                    colCM = np.median(
                        frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c][
                            frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c] < arbitraryCut
                        ]
                    )
                    frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c] -= colCM
                except Exception:
                    colCM = -666
                    print("colCM problem")
                    logger.error("colCM problem")
                    print(frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank], c)
                rowOffset += self.detectorInfo.nRowsPerBank
        return frame

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

    def dumpEventCodeStatistics(self):
        print(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )
        logger.info(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )

    def getRawData(self, evt, gainBitsMasked=True, negativeGain=False):
        frames = self.plainGetRawData(evt)
        if frames is None:
            return None
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

    def getNswitchedPixels(self, data, region=None):
        return ((data >= self.g0cut) * 1).sum()
