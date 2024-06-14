##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
# from psana import *
import importlib
import logging
import os
import sys

import psana

from calibrationSuite.argumentParser import ArgumentParser

logger = logging.getLogger(__name__)


class PsanaBase(object):
    def __init__(self, analysisType="scan"):
        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.psanaType = 1
        print("in psana1Base")
        logger.info("in psana1Base")
        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.g0cut = 1 << 14
        self.gainBitsMask = self.g0cut - 1

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
        knownTypes = ["epixhr", "epixM", "rixsCCD"]
        if self.experimentHash["detectorType"] not in knownTypes:
            print("type %s not in known types" % (self.experimentHash["detectorType"]), knownTypes)
            return -1

    ## self.setupPsana()

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

    def getFivePedestalRunInfo(self):
        ## could do load_txt but would require full path so
        if self.det is None:
            self.setupPsana()

        evt = self.getEvt(self.fivePedestalRun)
        self.fpGains = self.det.gain(evt)
        self.fpPedestals = self.det.pedestals(evt)
        self.fpStatus = self.det.status(evt)  ## does this work?
        self.fpRMS = self.det.rms(evt)  ## does this work?

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
            except Exception:
                pass
        except Exception:
            return None
        return f

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == psana.EvrData.ConfigV7:
                self.evrs.append(key.src())

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

    def get_config(self):
        self.config = self.ds.env().configStore()

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


"""
if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
"""
