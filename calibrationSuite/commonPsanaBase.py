import os
import sys
import logging
import importlib.util
from psana import *
from calibrationSuite.argumentParser import ArgumentParser
## standard
from mpi4py import MPI
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import sys
import h5py
from scipy.optimize import curve_fit  ## here?
from calibrationSuite.fitFunctions import *
from calibrationSuite.ancillaryMethods import *
from calibrationSuite.argumentParser import ArgumentParser
from calibrationSuite.detectorInfo import DetectorInfo
import os

logger = logging.getLogger(__name__)

class CommonPsanaBase(object):
    def __init__(self, analysisType="scan"):
        
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        
        print("in commonPsanaBase")
        logger.info("in commonPsanaBase")

        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.g0cut = 1 << 14  ## 2023
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
        knownTypes = ['epixhr', 'epixM', 'rixsCCD']
        if self.experimentHash['detectorType'] not in knownTypes:
            print ("type %s not in known types" %(self.experimentHash['detectorType']), knownTypes)
            return -1

        ##mymodule = importlib.import_module(full_module_name)

        self.camera = 0
        ##self.outputDir = '/sdf/data/lcls/ds/rix/rixx1003721/results/%s/' %(analysisType)
        self.outputDir = "../%s/" % (analysisType)
        logging.info("output dir: " + self.outputDir)
        ##self.outputDir = '/tmp'

        self.detectorInfo = DetectorInfo(self.experimentHash['detectorType'])
        
        self.className = self.__class__.__name__

        try:
            self.location = self.experimentHash["location"]
        except:
            pass
        try:
            self.exp = self.experimentHash["exp"]
        except:
            pass
        try:
            ##if True:
            self.ROIfileNames = self.experimentHash["ROIs"]
            self.ROIs = []
            for f in self.ROIfileNames:
                self.ROIs.append(np.load(f + ".npy"))
            try:  ## dumb code for compatibility or expectation
                self.ROI = self.ROIs[0]
            except:
                pass
        ##if False:
        except:
            print("had trouble finding", self.ROIfileNames)
            for currName in self.ROIfileNames:
                logger.exception("had trouble finding" + currName)
            self.ROI = None
            self.ROIs = None
        try:
            self.singlePixels = self.experimentHash["singlePixels"]
        except:
            self.singlePixels = None
        try:
            self.regionSlice = self.experimentHash["regionSlice"]
        except:
            self.regionSlice = None
        if self.regionSlice is not None:
            self.sliceCoordinates = [
                [self.regionSlice[0].start, self.regionSlice[0].stop],
                [self.regionSlice[1].start, self.regionSlice[1].stop],
            ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1] - sc[0][0], sc[1][1] - sc[1][0]]

        try:
            self.fluxSource = self.experimentHash["fluxSource"]
            try:
                self.fluxChannels = self.experimentHash["fluxChannels"]
            except:
                self.fluxChannels = range(8, 16)  ## wave8
            try:
                self.fluxSign = self.experimentHash["fluxSign"]
            except:
                self.fluxSign = 1
        except:
            self.fluxSource = None

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283  ## per Matt
        ##self.beamCode = 281 ## don't see 283...
        self.fakeBeamCode = False

        ##mymodule = importlib.import_module(full_module_name)

        ## for standalone analysis
        self.file = None
        if self.args.files is not None:
            self.file = self.args.files
        self.label = ""
        if self.args.label is not None:
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
        if self.args.maxNevents is not None:
            self.maxNevents = self.args.maxNevents
        if self.args.skipNevents is not None:
            self.skipNevents = self.args.skipNevents
        if self.args.path is not None:
            self.outputDir = self.args.path
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
        if self.args.threshold is not None:
            self.threshold = eval(self.args.threshold)
        else:
            self.threshold = None
        if self.args.fluxCut is not None:
            self.fluxCut = self.args.fluxCut
        try:
            self.runRange = eval(self.args.runRange)  ## in case needed
        except:
            self.runRange = None

        self.fivePedestalRun = self.args.fivePedestalRun  ## in case needed
        self.fakePedestal = self.args.fakePedestal  ## in case needed
        if self.fakePedestal is not None:
            self.fakePedestalFrame = np.load(self.fakePedestal)  ##cast to uint32???

        self.g0PedFile = self.args.g0PedFile
        if self.g0PedFile is not None:
            ##self.g0Ped = np.load(self.g0PedFile)
            self.g0Ped = np.array([np.load(self.g0PedFile)])##temp hack
            print(self.g0Ped.shape)
            
        self.g1PedFile = self.args.g0PedFile
        if self.g1PedFile is not None:
            ##self.g1Ped = np.load(self.g1PedFile)
            self.g1Ped = np.array([np.load(self.g1PedFile)])##temp hack

        self.g0GainFile = self.args.g0GainFile
        if self.g0GainFile is not None:
            self.g0Gain = np.load(self.g0GainFile)

        self.g1GainFile = self.args.g1GainFile
        if self.g1GainFile is not None:
            self.g1Gain = np.load(self.g1GainFile)

        self.offsetFile = self.args.offsetFile
        if self.offsetFile is not None:
            self.offset = np.load(self.offsetFile)

        if self.args.detType == "":
            ## assume epix10k for now
            if self.args.nModules is not None:
                self.detectorInfo.setNModules(self.args.nModules)
                self.detType = self.detectorInfo.getCameraType()
        else:
            self.detType = self.args.detType

        self.special = self.args.special
        ## done with configuration

        self.ds = None
        self.det = None  ## do we need multiple dets in an array? or self.secondDet?

        ##self.setupPsana()
        ##do this later or skip for -file

    def importConfigFile(self, file_path):
        if not os.path.exists(file_path):
            print(f"The file '{file_path}' does not exist")
            return None
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module
    
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

    
    def sortArrayByList(a, data):
        return [x for _, x in sorted(zip(a, data), key=lambda pair: pair[0])]
    
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

    def sliceToDetector(self, sliceRow, sliceCol):## cp from AnalyzeH5: import?
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]
    
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

    def dumpEventCodeStatistics(self):
        print(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )
        logger.info(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )