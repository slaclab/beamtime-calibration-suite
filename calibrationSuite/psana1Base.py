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
