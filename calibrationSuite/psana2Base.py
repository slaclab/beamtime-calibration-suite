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
This class contains a setup function and some utility functions that work only for psana2 based analysis.
To make the library use this class execute 'export foo=psana2'.
"""

import logging
import os
import sys

import psana

## standard
from mpi4py import MPI

from calibrationSuite.psanaCommon import PsanaCommon

##from PSCalib.NDArrIO import load_txt


os.environ["PS_SMD_N_EVENTS"] = "50"
os.environ["PS_SRV_NODES"] = "1"
## psana2 only


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


class PsanaBase(PsanaCommon):
    def __init__(self, analysisType="scan"):
        super().__init__()

        commandUsed = sys.executable + " " + " ".join(sys.argv)
        self.logger.info("Ran with cmd: " + commandUsed)

        self.psanaType = 2
        self.logger.info("in psana2Base")

        self.allowed_timestamp_mismatch = 1000

    def setupPsana(self):
        ## fix hardcoding in the fullness of time
        self.detEvts = 0
        self.flux = None
        self.config = None
        self.evrs = None

        if self.runRange is None:
            self.ds = self.get_ds(self.run)
        else:
            self.run = self.runRange[0]
            self.ds = self.get_ds()

        self.myrun = next(self.ds.runs())
        try:
            self.step_value = self.myrun.Detector("step_value")
            self.step_docstring = self.myrun.Detector("step_docstring")
        except Exception:
            self.step_value = self.step_docstring = None

        ## self.det = Detector('%s.0:%s.%d' %(self.location, self.detType, self.camera), self.ds.env())
        ## make this less dumb to accomodate epixM etc.
        ## use a dict etc.
        self.det = self.myrun.Detector(self.experimentHash["detectorType"])
        if self.det is None:
            logger.error("no det object for epixhr, what?  Pretend it's ok.")
            ##raise Exception
        ## could set to None and reset with first frame I guess, or does the det object know?

        self.timing = self.myrun.Detector("timing")
        self.desiredCodes = {"120Hz": 272, "4kHz": 273, "5kHz": 274}

        try:
            self.mfxDg1 = self.myrun.Detector("MfxDg1BmMon")
        except Exception:
            self.mfxDg1 = None
            self.logger.exception("No flux source found")

        try:
            self.mfxDg2 = self.myrun.Detector("MfxDg2BmMon")
        except Exception:
            self.mfxDg2 = None

        try:
            self.wave8 = psana.Detector(self.fluxSource, self.ds.env())
        except Exception:
            self.wave8 = None

        try:
            self.controlData = psana.Detector("ControlData")
        except Exception:
            self.controlData = None

    def get_ds(self, run=None):
        if run is None:
            run = self.run
        ##tmpDir = '/sdf/data/lcls/ds/rix/rixx1005922/scratch/xtc'
        ds = psana.DataSource(
            exp=self.exp, run=run, intg_det=self.experimentHash["detectorType"], max_events=self.maxNevents
        )  ##, dir=tmpDir)
        return ds

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

    def getNextEvtFromGen(self, gen):
        ## this is needed to get flux information out of phase with detector
        ## information in mixed lcls1/2 mode
        for nevt, evt in enumerate(gen):
            try:
                self.flux = self._getFlux(evt)
            except Exception:
                pass
            if self.det.raw.raw(evt) is None:
                continue
            self.detEvts += 1
            ## should check for beam code here to be smarter
            return self.detEvts, evt

    def matchedDetEvt(self):
        self.fluxTS = 0
        for nevt, evt in enumerate(self.myrun.events()):
            ec = self.getEventCodes(evt)
            if ec[137]:
                self.flux = self._getFlux(evt)  ## fix this
                self.fluxTS = self.getTimestamp(evt)
                continue
            elif ec[281]:
                self.framesTS = self.getTimestamp(evt)
                if self.framesTS - self.fluxTS > self.allowed_timestamp_mismatch:
                    continue
                yield evt
            else:
                continue

    def getAllFluxes(self, evt):
        if evt is None:
            return None
        try:
            return self.mfxDg1.raw.peakAmplitude(evt)
        except Exception:
            return None

    def _getFlux(self, evt):
        if self.mfxDg1 is None:
            return None

        ##f = self.mfxDg1.raw.peakAmplitude(evt)[self.fluxChannels].mean()*self.fluxSign
        try:
            f = self.mfxDg1.raw.peakAmplitude(evt)[self.fluxChannels].mean() * self.fluxSign
            ##print(f)
        except Exception:
            # print(e)
            return None
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
        return f

    def getFlux(self, evt):
        ##return 1
        return self.flux

    def getEventCodes(self, evt):
        return self.timing.raw.eventcodes(evt)

    def getPulseId(self, evt):
        return self.timing.raw.pulseId(evt)

    def isKicked(self, evt):
        allcodes = self.getEventCodes(evt)
        ##print(allcodes)
        return allcodes[self.desiredCodes["120Hz"]]

    def getStepGen(self):
        return self.myrun.steps()

    def getRunGen(self):
        return self.ds.runs()

    def getEvt(self):
        try:
            evt = next(self.myrun.events())
            ## dumb to do the below everywhere, should best not call this method
            ##try:
            ##    self.flux = self._getFlux(evt)
            ##except:
            ##    pass

        except StopIteration:
            return None
        return evt

    def getScanValue(self, step, useStringInfo=False):
        ##print(self.step_value(step),self.step_docstring(step),useStringInfo)
        if useStringInfo:
            payload = self.step_docstring(step)
            print(payload)
            sv = eval(payload.split()[-1][:-1])
            ##print('sv', sv)
            self.logger.info("step" + str(int(self.step_value(step))) + str(sv))
            return int(float(sv))
        return self.step_value(step)

    def plainGetRawData(self, evt):
        return self.det.raw.raw(evt)

    def getCalibData(self, evt):
        frames = self.det.raw.calib(evt)
        return frames

    def getImage(self, evt, data=None):
        return self.det.raw.image(evt, data)

    def getTimestamp(self, evt):
        return evt.timestamp

    def getPingPongParity(self, frameRegion):
        evensEvenRowsOddsOddRows = frameRegion[::2, ::2] + frameRegion[1::2, 1::2]
        oddsEvenRowsEvensOddRows = frameRegion[1::2, ::2] + frameRegion[::2, 1::2]
        delta = evensEvenRowsOddsOddRows.mean() - oddsEvenRowsEvensOddRows.mean()
        ##print("delta:", delta)
        return delta > 0
