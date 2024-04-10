##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from psana import DataSource

import logging
import os

from calibrationSuite.suiteBase import SuiteBase
import calibrationSuite.psana2 as psana2
import calibrationSuite.psana1 as psana1

psanaBaseNum = 0
if os.getenv("SUITE_PSANA_NUM") == "1":
    print("psana1")
    psanaBaseNum = 1
else:
    print("psana2")
    psanaBaseNum = 2

if psanaBaseNum == 2:
    ## psana2 only
    os.environ["PS_SMD_N_EVENTS"] = "50"
    os.environ["PS_SRV_NODES"] = "1"
else:
    pass


logger = logging.getLogger(__name__)


class PsanaBase(SuiteBase):
    def __init__(self, analysisType="scan"):
        super().__init__(analysisType)
        print("in PsanaBase")
        logger.info("in PsanaBase")

        # psana 1 + 2
        self.ds = None
        self.det = None
        self.wave8 = None
        self.evrs = None
        self.config = None
        self.controlData = None

        # psana 2
        self.myrun = None
        self.step_value = None
        self.step_docstring = None
        self.timing = None
        self.desiredCodes = None
        self.mfxDg1 = None
        self.mfxDg2 = None
        self.detEvts = None
        self.flux = None

    def setupPsana(self):
        if psanaBaseNum == 2:
            psana2.setupPsana2(self)
        else:
            psana1.setupPsana1(self)

    ######## Start of getters

    def get_ds(self, run=None):
        if run is None:
            run = self.run
        if psanaBaseNum == 2:
            return DataSource(
                exp=self.exp,
                run=run,
                intg_det=self.experimentHash["detectorType"],
                max_events=self.maxNevents,
            )
        else:
            return DataSource("exp=%s:run=%d:smd" % (self.exp, run))

    # uses get_ds, which is psana 1 vs 2 specific 
    def getEvtFromRunsTooSmartForMyOwnGood(self):
        for r in self.runRange:
            self.run = r
            self.ds = self.get_ds()
            try:
                evt = next(self.ds.events())
                yield evt
            except Exception:
                continue

    # uses get_ds, which is psana 1 vs 2 specific 
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

    # uses get_ds, which is psana 1 vs 2 specific 
    def getEvtOld(self, run=None):
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

    def isKicked(self, evt):
        if psanaBaseNum == 2:
            allcodes = self.getEventCodes(evt)
            return allcodes[self.desiredCodes["120Hz"]]
        else:
            return psana1.isKickedPsana1(self, evt)

    def getFlux(self, evt):
        if psanaBaseNum == 2:
            return self.flux
        else:
            return psana1.getFluxPsana1(self, evt)

    def getEvt(self):
        if psanaBaseNum == 2:
            return self.getEvtPsana2()
        else:
            return self.getEvtPsana1()

    def getStepGen(self):
        if psanaBaseNum == 2:
            return self.myrun.steps()
        else:
            return self.ds.steps()

    def getCalibData(self, evt):
        if psanaBaseNum == 2:
            frames = self.det.raw.calib(evt)
            return frames
        else:
            return self.det.calib(evt)

    def getRawData(self, evt, gainBitsMasked=True):
        if psanaBaseNum == 2:
            return psana2.getRawDataPsana2(self, evt, gainBitsMasked)
        else:
            return psana1.getRawDataPsana1(self, evt, gainBitsMasked)

    def getScanValue(self, step=-1, useStringInfo=False):
        # for psana1, where we don't specify a step arg
        if step == -1:  # psana1
            return self.controlData().pvControls()[0].value()

        ##print(self.step_value(step),self.step_docstring(step),useStringInfo)
        if useStringInfo:
            payload = self.step_docstring(step)
            ##print(payload)
            sv = eval(payload.split()[-1][:-1])
            print("step", int(self.step_value(step)), sv)
            logger.info("step" + str(int(self.step_value(step))) + str(sv))
            return sv
        return self.step_value(step)

    ######## End of getters


if __name__ == "__main__":
    bSS = PsanaBase()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
