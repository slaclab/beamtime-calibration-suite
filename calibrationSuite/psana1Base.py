##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from psana import *
from calibrationSuite.commonPsanaBase import *
from PSCalib.NDArrIO import load_txt
import logging
logger = logging.getLogger(__name__)


class PsanaBase(CommonPsanaBase):
    def __init__(self, analysisType="scan"):
        super().__init__(analysisType)
        self.psanaType = 1
        print("in psana1Base")
        logger.info("in psana1Base")


    def get_ds(self, run=None):
        if run is None:
            run = self.run
        return DataSource("exp=%s:run=%d:smd" % (self.exp, run))

    def setupPsana(self):
        logger.info("have built basic script class, exp %s run %d" % (self.exp, self.run))

        if self.runRange is None:
            self.ds = self.get_ds(self.run)
        else:
            self.run = self.runRange[0]
            self.ds = self.get_ds()

        self.det = Detector("%s.0:%s.%d" % (self.location, self.detType, self.camera), self.ds.env())
        self.evrs = None
        try:
            self.wave8 = Detector(self.fluxSource, self.ds.env())
        except:
            self.wave8 = None
        self.config = None
        try:
            self.controlData = Detector("ControlData")
        except:
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

    def getEvtFromRunsTooSmartForMyOwnGood(self):
        for r in self.runRange:
            self.run = r
            self.ds = self.get_ds()
            try:
                evt = next(self.ds.events())
                yield evt
            except:
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
            except:
                print("have run out of new runs")
                logger.exception("have run out of new runs")
                return None
            ##print("get event from new run")
            evt = next(self.ds.events())
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
                if f < self.fluxCut:
                    return None
            except:
                pass
        except:
            return None
        return f

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == EvrData.ConfigV7:
                self.evrs.append(key.src())

    def isKicked(self, evt):
        try:
            evr = evt.get(EvrData.DataV4, self.evrs[0])
        except:
            self.get_evrs()
            evr = evt.get(EvrData.DataV4, self.evrs[0])

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
        except:
            pass
        return kicked

    def getScanValue(self, foo):
        return self.controlData().pvControls()[0].value()

    def getStepGen(self):
        return self.ds.steps()

    def getRawData(self, evt, gainBitsMasked=True):
        frames = self.det.raw(evt)
        if frames is None:
            return None
        if gainBitsMasked:
            return frames & 0x3FFF
        return frames

    def getCalibData(self, evt):
        return self.det.calib(evt)


if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
