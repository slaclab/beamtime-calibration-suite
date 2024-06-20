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
This class contains a setup function and some utility functions that work only for psana1 based analysis.
To make the library use this class execute 'export foo=psana1'.
"""

import logging
import sys

import psana
from calibrationSuite.psanaCommon import PsanaCommon

logger = logging.getLogger(__name__)


class PsanaBase(PsanaCommon):
    def __init__(self, analysisType="scan"):
        super().__init__()

        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.psanaType = 1
        print("in psana1Base")
        logger.info("in psana1Base")
        self.g0cut = 1 << 14
        self.gainBitsMask = self.g0cut - 1

    def get_ds(self, run=None):
        if run is None:
            run = self.run
        return psana.DataSource("exp=%s:run=%d:smd" % (self.exp, run))

    def setupPsana(self):
        logger.info("have built basic script class, exp %s run %d" % (self.exp, self.run))

        if self.runRange is None:
            self.ds = self.get_ds(self.run)
        else:
            self.run = self.runRange[0]
            self.ds = self.get_ds()

        self.det = psana.Detector("%s.0:%s.%d" % (self.location, self.detType, self.camera), self.ds.env())
        self.evrs = None
        try:
            self.wave8 = psana.Detector(self.fluxSource, self.ds.env())
        except Exception:
            self.wave8 = None
        self.config = None
        try:
            self.controlData = psana.Detector("ControlData")
        except Exception:
            self.controlData = None

    def getEvt(self, run=None):
        oldDs = self.ds
        if run is not None:
            self.ds = self.get_ds(run)
        try:  ## or just yield evt I think
            evt = next(self.ds.events())
        except StopIteration:
            self.ds = oldDs
            return None
        self.ds = oldDs
        return evt

    def getFlux(self, evt):
        try:
            fluxes = self.wave8.get(evt).peakA()
            if fluxes is None:
                print("No flux found")  ## if self.verbose?
                logger.error("No flux found")
                return None
            f = fluxes[self.fluxChannels].mean() * self.fluxSign
            try:
                if f < self.fluxCutMin:
                    return None
            except Exception:
                pass
            try:
                if f > self.fluxCutMax:
                    return None
            except Exception:
                pass
        except Exception:
            return None
        return f

    def isKicked(self, evt):
        try:
            evr = evt.get(psana.EvrData.DataV4, self.evrs[0])
        except Exception:
            self.get_evrs()
            evr = evt.get(psana.EvrData.DataV4, self.evrs[0])

        ##        kicked = False
        ##        try:
        ##            for ec in evr.fifoEvents():
        ##                if ec.eventCode() == 162:
        ##                    return True
        kicked = True
        try:
            for ec in evr.fifoEvents():
                if ec.eventCode() == 137:
                    kicked = False
        except Exception:
            pass
        return kicked

    def getStepGen(self):
        return self.ds.steps()

    def getScanValue(self, foo):
        return self.controlData().pvControls()[0].value()

    def getRawData(self, evt, gainBitsMasked=True):
        frames = self.det.raw(evt)
        if frames is None:
            return None
        if gainBitsMasked:
            return frames & 0x3FFF
        return frames

    def getCalibData(self, evt):
        return self.det.calib(evt)

    def getImage(self, evt, data=None):
        return self.raw.image(evt, data)