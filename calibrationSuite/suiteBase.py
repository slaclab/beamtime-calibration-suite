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

import os
import sys
import logging
import sys
import os
import importlib.util
import numpy as np
from mpi4py import MPI

from calibrationSuite.fitFunctions import *
from calibrationSuite.ancillaryMethods import *
from calibrationSuite.argumentParser import ArgumentParser
from calibrationSuite.detectorInfo import DetectorInfo

logger = logging.getLogger(__name__)

class SuiteBase(object):
    def __init__(self, analysisType="scan"):
        
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        
        print("in commonPsanaBase")
        logger.info("in commonPsanaBase")

        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.allowed_timestamp_mismatch = 1000
        self.camera = 0
        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.g0cut = 1 << 14  ## 2023
        self.gainBitsMask = self.g0cut - 1

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283  ## per Matt
        ##self.beamCode = 281 ## don't see 283...
        self.fakeBeamCode = False
        
        self.ds = None
        self.det = None  ## do we need multiple dets in an array? or self.secondDet?

        ##self.outputDir = '/sdf/data/lcls/ds/rix/rixx1003721/results/%s/' %(analysisType)
        self.outputDir = "../%s/" % (analysisType)
        logging.info("output dir: " + self.outputDir)

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

        self.detectorInfo = DetectorInfo(self.experimentHash['detectorType'])

        self.location = self.experimentHash.get("location", None)
        self.exp = self.experimentHash.get("exp", None)
        print (self.exp) 

        self.ROIfileNames = self.experimentHash.get("ROIs", None)
        if not self.ROIfileNames:
            print("had trouble finding" + str(self.ROIfileNames))
            logger.info("had trouble finding" + str(self.ROIfileNames))
        self.ROIs = []
        for f in self.ROIfileNames:
            self.ROIs.append(np.load(f + ".npy"))
        self.ROI = None
        if len(self.ROIs[0]):
            self.ROI = self.ROIs[0]
     
        self.singlePixels = self.experimentHash.get("singlePixels", None)

        self.sliceEdges = None
        self.sliceCoordinates = None
        self.regionSlice = self.experimentHash.get("regionSlice", None)
        if self.regionSlice is not None:
            self.sliceCoordinates = [
                [self.regionSlice[0].start, self.regionSlice[0].stop],
                [self.regionSlice[1].start, self.regionSlice[1].stop],
            ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1] - sc[0][0], sc[1][1] - sc[1][0]]

        self.fluxSource = self.experimentHash.get("fluxSource", None)
        self.fluxChannels = self.experimentHash.get("fluxChannels", range(8, 16) )
        self.fluxSign = self.experimentHash.get("fluxSign", 1)
 
        self.setupValuesFromArgs()

    def setupValuesFromArgs(self):

        ## for standalone analysis
        self.file = self.args.files
        self.label = self.args.label

        ## analyzing xtcs
        if self.args.run is not None:
            self.run = self.args.run
        if self.args.camera is not None:
            self.camera = self.args.camera
        if self.args.exp is not None:
            self.exp = self.args.exp
        if self.args.location is not None:
            self.location = self.args.location
        self.maxNevents = self.args.maxNevents
        self.skipNevents = self.args.skipNevents
        self.path = self.args.path 

        # if set, output folders will be relative to OUTPUT_ROOT
        # if not, they will be relative to the current script file
        self.outputDir = os.getenv("OUTPUT_ROOT", "") + self.outputDir
        # check if outputDir exists, if does not create it and tell user
        if not os.path.exists(self.outputDir):
            print("could not find output dir: " + self.outputDir)
            logger.info("could not find output dir: " + self.outputDir)
            print("please create this dir, exiting...")
            logger.info("please create this dir, exiting...")
            exit(1)
            # the following doesnt work with mpi parallelism (other thread could make dir b4 curr thread)
            #print("so creating dir: " + self.outputDir)
            #logger.info("creating dir: " + self.outputDir)
            #os.makedirs(self.outputDir)
            # give dir read, write, execute permissions
            #os.chmod(self.outputDir, 0o777)
 
        self.detObj = self.args.detObj
        self.threshold = eval(self.args.threshold) if self.args.threshold is not None else None
        self.runRange = eval(self.args.runRange) if self.args.runRange is not None else None
        self.fluxCut = self.args.fluxCut

        self.fivePedestalRun = self.args.fivePedestalRun  ## in case needed
        self.fakePedestal = self.args.fakePedestal  ## in case needed]
        self.fakePedestalFrame = np.load(self.fakePedestal) if self.fakePedestal is not None else None  ##cast to uint32???

        self.g0PedFile = self.args.g0PedFile
        self.g0Ped = np.array([np.load(self.args.g0PedFile)]) if self.args.g0PedFile is not None else None
      
        self.g1PedFile = self.args.g1PedFile
        self.g1Ped = np.array([np.load(self.args.g1PedFile)]) if self.args.g1PedFile is not None else None

        self.g0GainFile = self.args.g0GainFile
        self.g0Gain = np.load(self.g0GainFile) if self.args.g0GainFile is not None else None

        self.g1GainFile = self.args.g1GainFile
        self.g1Gain = np.load(self.g1GainFile) if self.args.g1GainFile is not None else None

        self.offsetFile = self.args.offsetFile
        self.offset = np.load(self.offsetFile) if self.args.offsetFile is not None else None

        self.detType = None
        if self.args.detType == "":
            ## assume epix10k for now
            if self.args.nModules is not None:
                self.detectorInfo.setNModules(self.args.nModules)
                self.detType = self.detectorInfo.getCameraType()
        else:
            self.detType = self.args.detType

        self.special = self.args.special

    def importConfigFile(self, file_path):
        if not os.path.exists(file_path):
            print(f"The file '{file_path}' does not exist")
            return None
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module
    

    ######## Start of getters

    def get_config(self):
        self.config = self.ds.env().configStore() 

    def getImage(self, evt, data=None):
        return self.raw.image(evt, data)
    
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
    
    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == EvrData.ConfigV7:
                self.evrs.append(key.src())
    
    def getPingPongParity(self, frameRegion):
        evensEvenRowsOddsOddRows = frameRegion[::2, ::2] + frameRegion[1::2, 1::2]
        oddsEvenRowsEvensOddRows = frameRegion[1::2, ::2] + frameRegion[::2, 1::2]
        delta = evensEvenRowsOddsOddRows.mean() - oddsEvenRowsEvensOddRows.mean()
        ##print("delta:", delta)
        return delta > 0

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

        ##f = self.mfxDg1.raw.peakAmplitude(evt)[self.fluxChannels].mean()*self.fluxSign
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

    def getEventCodes(self, evt):
        return self.timing.raw.eventcodes(evt)

    def getPulseId(self, evt):
        return self.timing.raw.pulseId(evt)

    def getRunGen(self):
        return self.ds.runs()
    
    def getTimestamp(self, evt):
        return evt.timestamp
    
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
        
    ######## End of getters


    ######## Start of setters
    def isBeamEvent(self, evt):
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
        return False

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
    
    ######## End of setters


    ######## Start of correction functions

    def noCommonModeCorrection(self, frame):
        return frame

    def regionCommonModeCorrection(self, frame, region, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        regionCM = np.median(frame[region][frame[region] < arbitraryCut])
        return frame - regionCM

    def rowCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        ##rand = np.random.random()
        for r in range(self.detectorInfo.nRows):
            colOffset = 0
            ##for b in range(0, self.detNbanks):
            for b in range(0, 2):
                try:
                    rowCM = np.median(
                        frame[r, colOffset : colOffset + self.detColsPerBank][
                            frame[r, colOffset : colOffset + self.detColsPerBank] < arbitraryCut
                        ]
                    )
                    ##if r == 280 and rand > 0.999:
                    ##print(b, frame[r, colOffset:colOffset + self.detColsPerBank], rowCM, rowCM<arbitraryCut-1, rowCM*(rowCM<arbitraryCut-1))
                    ##frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM*(rowCM<arbitraryCut-1)
                    frame[r, colOffset : colOffset + self.detColsPerBank] -= rowCM
                    ##if r == 280 and rand > 0.999:
                    ##print(frame[r, colOffset:colOffset + self.detColsPerBank], np.median(frame[r, colOffset:colOffset + self.detColsPerBank]))
                except:
                    rowCM = -666
                    print("rowCM problem")
                    logger.error("rowCM problem")
                    print(frame[r, colOffset : colOffset + self.detColsPerBank])
                colOffset += self.detColsPerBank
        return frame

    def colCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        ##rand = np.random.random()
        for c in range(self.detCols):
            rowOffset = 0
            for b in range(0, self.detNbanksCol):
                ##for b in range(0, 2):
                try:
                    colCM = np.median(
                        frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c][
                            frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c] < arbitraryCut
                        ]
                    )
                    ##if r == 280 and rand > 0.999:
                    ##print(b, frame[r, colOffset:colOffset + self.detColsPerBank], rowCM, rowCM<arbitraryCut-1, rowCM*(rowCM<arbitraryCut-1))
                    ##frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM*(rowCM<arbitraryCut-1)
                    frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank, c] -= colCM
                    ##if r == 280 and rand > 0.999:
                    ##print(frame[r, colOffset:colOffset + self.detColsPerBank], np.median(frame[r, colOffset:colOffset + self.detColsPerBank]))
                except:
                    colCM = -666
                    print("colCM problem")
                    logger.error("colCM problem")
                    print(frame[rowOffset : rowOffset + self.detectorInfo.nRowsPerBank], c)
                rowOffset += self.detectorInfo.nRowsPerBank
        return frame

    ######## End of correction functions


    ######## Start of misc-utility functions
  
    def dumpEventCodeStatistics(self):
        print(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )
        logger.info(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )

    def sortArrayByList(self, a, data):
        return [x for _, x in sorted(zip(a, data), key=lambda pair: pair[0])]
    

    def sliceToDetector(self, sliceRow, sliceCol):## cp from AnalyzeH5: import?
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

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
        
    ######## End of misc-utility functions