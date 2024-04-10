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
from calibrationSuite.argumentParser import ArgumentParser
import importlib.util

##from PSCalib.NDArrIO import load_txt

## for parallelism
import os
import sys

os.environ["PS_SMD_N_EVENTS"] = "50"
os.environ["PS_SRV_NODES"] = "1"
## psana2 only

## standard
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import logging

logger = logging.getLogger(__name__)


class PsanaBase(object):
    def __init__(self, analysisType="scan"):
        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.psanaType = 2
        print("in psana2Base")
        logger.info("in psana2Base")

        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        ##self.g0cut = 1<<15 ## 2022
        self.g0cut = 1 << 14  ## 2023
        self.gainBitsMask = self.g0cut - 1

        self.allowed_timestamp_mismatch = 1000

        self.args = ArgumentParser().parse_args()
        logger.info("parsed cmdline args: " + str(self.args))

        # if the SUITE_CONFIG env var is set use that, otherwise if the cmd line arg is set use that
        # if neither are set, use the default 'suiteConfig.py' file
        defaultConfigFileName = "suiteConfig.py"
        secondaryConfigFileName = defaultConfigFileName if self.args.configFile is None else self.args.configFile
        # secondaryConfigFileName is returned if env var not set
        configFileName = os.environ.get("SUITE_CONFIG", secondaryConfigFileName)
        config = self.importConfigFile(configFileName)
        if config is None:
            print("\ncould not find or read config file: " + configFileName)
            print("please set SUITE_CONFIG env-var or use the '-cf' cmd-line arg to specify a valid config file")
            print("exiting...")
            sys.exit(1)
        self.experimentHash = config.experimentHash
        knownTypes = ['epixhr', 'epixM', 'rixsCCD']
        if self.experimentHash['detectorType'] not in knownTypes:
            print ("type %s not in known types" %(self.experimentHash['detectorType']), knownTypes)
            return -1
        ##self.setupPsana()

    def importConfigFile(self, file_path):
        if not os.path.exists(file_path):
            print(f"The file '{file_path}' does not exist")
            return None
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module

    def get_ds(self, run=None):
        if run is None:
            run = self.run
        ##tmpDir = '/sdf/data/lcls/ds/rix/rixx1005922/scratch/xtc'## temp
        return DataSource(exp=self.exp, run=run, intg_det=self.experimentHash['detectorType'], max_events=self.maxNevents)##, dir=tmpDir)

    def setupPsana(self):
        ##print("have built basic script class, exp %s run %d" %(self.exp, self.run))
        if self.runRange is None:
            self.ds = self.get_ds(self.run)
        else:
            self.run = self.runRange[0]
            self.ds = self.get_ds()

        self.myrun = next(self.ds.runs())
        try:
            self.step_value = self.myrun.Detector("step_value")
            self.step_docstring = self.myrun.Detector("step_docstring")
        except:
            self.step_value = self.step_docstring = None

        ##        self.det = Detector('%s.0:%s.%d' %(self.location, self.detType, self.camera), self.ds.env())
        ## make this less dumb to accomodate epixM etc.
        ## use a dict etc.
        self.det = self.myrun.Detector(self.experimentHash['detectorType'])
        if self.det is None:
            print("no det object for epixhr, what?  Pretend it's ok.")
            ##raise Exception
        ## could set to None and reset with first frame I guess, or does the det object know?

        self.timing = self.myrun.Detector("timing")
        self.desiredCodes = {"120Hz": 272, "4kHz": 273, "5kHz": 274}

        try:
            self.mfxDg1 = self.myrun.Detector("MfxDg1BmMon")
        except:
            self.mfxDg1 = None
            print("No flux source found")  ## if self.verbose?
            logger.exception("No flux source found")
        try:
            self.mfxDg2 = self.myrun.Detector("MfxDg2BmMon")
        except:
            self.mfxDg2 = None
        ## fix hardcoding in the fullness of time
        self.detEvts = 0
        self.flux = None

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

    ##        if self.mfxDg1 is None:

    def getFivePedestalRunInfo(self):
        ## could do load_txt but would require full path so
        if self.det is None:
            self.setupPsana()

        evt = self.getEvt(self.fivePedestalRun)
        self.fpGains = self.det.gain(evt)
        self.fpPedestals = self.det.pedestals(evt)
        self.fpStatus = self.det.status(evt)  ## does this work?
        self.fpRMS = self.det.rms(evt)  ## does this work?

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
            except:
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
            return(evt)
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

    def getAllFluxes(self, evt):
        if evt is None:
            return None
        try:
            return self.mfxDg1.raw.peakAmplitude(evt)
        except:
            return None

    def _getFlux(self, evt):
        if self.mfxDg1 is None:
            return None

        ##        f = self.mfxDg1.raw.peakAmplitude(evt)[self.fluxChannels].mean()*self.fluxSign
        try:
            f = self.mfxDg1.raw.peakAmplitude(evt)[self.fluxChannels].mean() * self.fluxSign
            ##print(f)
        except Exception as e:
            # print(e)
            return None
        try:
            if f < self.fluxCut:
                return None
        except:
            pass
        return f

    def getFlux(self, evt):
        ##return 1
        return self.flux

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == EvrData.ConfigV7:
                self.evrs.append(key.src())

    def getEventCodes(self, evt):
        return self.timing.raw.eventcodes(evt)

    def getPulseId(self, evt):
        return self.timing.raw.pulseId(evt)

    def isKicked(self, evt):
        allcodes = self.getEventCodes(evt)
        ##print(allcodes)
        return allcodes[self.desiredCodes["120Hz"]]

    def get_config(self):
        self.config = self.ds.env().configStore()

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
            ##print(payload)
            sv = eval(payload.split()[-1][:-1])
            print("step", int(self.step_value(step)), sv)
            logger.info("step" + str(int(self.step_value(step))) + str(sv))
            return sv
        return self.step_value(step)

    def getRawData(self, evt, gainBitsMasked=True):
        frames = self.det.raw.raw(evt)
        if frames is None:
            return None
        if self.special:
            if 'thirteenBits' in self.special:
                frames = (frames & 0xfffe)
                ##print("13bits")
            elif 'twelveBits' in self.special:
                frames = (frames & 0xfffc)
                ##print("12bits")
            elif 'elevenBits' in self.special:
                frames = (frames & 0xfff8)
                ##print("11bits")
            elif 'tenBits' in self.special:
                frames = (frames & 0xfff0)
                ##print("10bits")
        if gainBitsMasked:
            return frames & self.gainBitsMask
        return frames

    def getCalibData(self, evt):
        frames = self.det.raw.calib(evt)
        return frames

    def getImage(self, evt, data=None):
        return self.raw.image(evt, data)

    def getTimestamp(self, evt):
        return evt.timestamp

    def getPingPongParity(self, frameRegion):
        evensEvenRowsOddsOddRows = frameRegion[::2, ::2] + frameRegion[1::2, 1::2]
        oddsEvenRowsEvensOddRows = frameRegion[1::2, ::2] + frameRegion[::2, 1::2]
        delta = evensEvenRowsOddsOddRows.mean() - oddsEvenRowsEvensOddRows.mean()
        ##print("delta:", delta)
        return delta > 0


if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
