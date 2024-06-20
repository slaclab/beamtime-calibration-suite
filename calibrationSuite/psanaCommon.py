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
This class has setup-code and variables, along with some utility functions, common for both psana bases.
(psana1Base and psana2Base must both inherit from PsanaCommon!)
"""

import psana
import logging
import importlib.util

## for parallelism
import os
import sys
import np

from calibrationSuite.argumentParser import ArgumentParser
from calibrationSuite.detectorInfo import DetectorInfo

logger = logging.getLogger(__name__)


class PsanaCommon(object):
    def __init__(self, analysisType="scan"):
        print("in psanaCommon")
        logger.info("in psanaCommon")

        self.args = ArgumentParser().parse_args()
        logger.info("parsed cmdline args: " + str(self.args))

        # Variable-setup calls
        self.loadExperimentHashFromConfig()
        self.setupFromExperimentHash()
        self.setupFromCmdlineArgs()
        self.setupOutputDirString(analysisType)

    #### Start of setup related functions ####

    def loadExperimentHashFromConfig(self):
        """
        Loads the experiment config file (ex: beamtime-calibration-suite/config_files/epixMSuiteConfig.py)
        The config file is determined by checking the SUITE_CONFIG environment variable,
        then a command-line argument, and finally a default file 'suiteConfig.py' (in this order of precedence).
        If file cannot be found or read, exit the program.
        The function also validates the detector type against known types (with info from the config).
        """

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
            logger.error("\ncould not find or read config file: " + configFileName)
            logger.error("please set SUITE_CONFIG env-var or use the '-cf' cmd-line arg to specify a valid config file")
            logger.error("exiting...")
            sys.exit(1)
        self.experimentHash = config.experimentHash
        knownTypes = ["epixhr", "epixM", "rixsCCD"]
        if self.experimentHash["detectorType"] not in knownTypes:
            print("type %s not in known types" % (self.experimentHash["detectorType"]), knownTypes)
            print("exiting...")
            logger.error("type %s not in known types" % (self.experimentHash["detectorType"]), knownTypes)
            logger.error("exiting...")
            sys.exit(1)

    def importConfigFile(self, file_path):
        """
        Imports config file as a Python module. See loadExperimentHashFromConfig() for how the config file
        is specified by the user.
        """
        if not os.path.exists(file_path):
            print("The file " + file_path + " does not exist")
            logger.error("The file " + file_path + " does not exist")
            return None
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(config_module)
        except Exception as e:
            print("Error executing config-file code: " + str(e))
            logger.info("Error executing config-file code: " + str(e))
            return None
        return config_module

    def setupFromExperimentHash(self):
        """
        Sets up configurations and parameters based on user-specified config file.
        Initializes necessary attributes and handles exceptions on specific evaluations.
        """

        try:
            self.detectorInfo = DetectorInfo(
                self.experimentHash["detectorType"], self.experimentHash["detectorSubtype"]
            )
        except Exception:
            self.detectorInfo = DetectorInfo(self.experimentHash["detectorType"])

        self.exp = self.experimentHash.get("exp", None)

        self.setupROIFiles()

        self.singlePixels = self.experimentHash.get("singlePixels", None)

        self.regionSlice = self.experimentHash.get("regionSlice", None)
        if self.regionSlice is not None:
            ## n.b. assumes 3d slice now
            self.sliceCoordinates = [
                [self.regionSlice[1].start, self.regionSlice[1].stop],
                [self.regionSlice[2].start, self.regionSlice[2].stop],
            ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1] - sc[0][0], sc[1][1] - sc[1][0]]

        ## handle 1d rixs ccd data
        if self.detectorInfo.dimension == 2:
            self.regionSlice = self.regionSlice[0], self.regionSlice[2]
            print("remapping regionSlice to handle 1d case")
            logger.info("remapping regionSlice to handle 1d case")

        self.fluxSource = self.experimentHash.get("fluxSource", None)
        self.fluxChannels = self.experimentHash.get("fluxChannels", range(8, 16))  ## wave8
        self.fluxSign = self.experimentHash.get("fluxSign", 1)

        self.ignoreEventCodeCheck = self.experimentHash.get("ignoreEventCodeCheck", None)
        self.fakeBeamCode = True if self.ignoreEventCodeCheck is not None else False

    def setupROIFiles(self):
        """
        Sets up the ROI (Region of Interest) files.
        Loads ROI data from the file names specified in the config file.
        If any errors occur during the process, logs and prints appropriate error messages.
        """

        self.ROIfileNames = None
        try:
            self.ROIfileNames = self.experimentHash.get("ROIs", None)
            self.ROIs = []
            for f in self.ROIfileNames:
                self.ROIs.append(np.load(f))
            self.ROI = self.ROIs[0] if len(self.ROIs) >= 1 else None
        except Exception:
            if self.ROIfileNames is not None:
                print("had trouble finding" + str(self.ROIfileNames))
                logger.error("had trouble finding" + str(self.ROIfileNames))
                for currName in self.ROIfileNames:
                    print("had trouble finding" + currName)
                    logger.exception("had trouble finding" + currName)

    def setupFromCmdlineArgs(self):
        """
        Sets up configurations and parameters based on user-entered command-line arguments.
        Initializes necessary attributes and handles exceptions on specific evaluations.
        """
            
        self.special = self.args.special

        if not self.fakeBeamCode:  ## defined in ignoreEventCodeCheck
            if self.special is not None:
                self.fakeBeamCode = "fakeBeamCode" in self.special

        print(
            "ignoring event code check, faking beam code:"
            + str(self.ignoreEventCodeCheck)
            + " "
            + str(self.fakeBeamCode)
        )
        logger.info(
            "ignoring event code check, faking beam code:"
            + str(self.ignoreEventCodeCheck)
            + " "
            + str(self.fakeBeamCode)
        )

        ## for standalone analysis
        self.file = self.args.files
        self.label = "" if self.args.label is None else self.args.label

        ## analyzing xtcs
        self.run = self.args.run

        self.camera = 0 if self.args.camera is None else self.args.camera

        # this is set in the config-file, but take the cmd-line value instead if it is set
        if self.args.exp is not None:
            self.exp = self.args.exp

        self.location = self.experimentHash.get("location", None)
        if self.args.location is not None:
            self.location = self.args.location

        self.maxNevents = self.args.maxNevents
        self.skipNevents = self.args.skipNevents

        self.detObj = self.args.detObj

        self.threshold = None
        if self.args.threshold is not None:
            try:
                self.threshold = eval(self.args.threshold)
            except Exception as e:
                print("Error evaluating threshold: " + str(e))
                logger.exception("Error evaluating threshold: " + str(e))
                self.threshold = None

        self.seedCut = None
        if self.args.seedCut is not None:
            try:
                self.seedCut = eval(self.args.seedCut)
            except Exception as e:
                print("Error evaluating seedcut: " + str(e))
                logger.exception("Error evaluating seedcut: " + str(e))
                self.seedCut = None

        self.fluxCutMin = self.args.fluxCutMin
        self.fluxCutMax = self.args.fluxCutMax

        self.runRange = None
        if self.args.runRange is not None:
            try:
                self.runRange = eval(self.args.runRange)  ## in case needed
            except Exception as e:
                print("Error evaluating runRange: " + str(e))
                logger.exception("Error evaluating runRange: " + str(e))
                self.runRange = None

        self.loadPedestalGainOffsetFiles() 

        if self.args.detType == "":
            ## assume epix10k for now
            if self.args.nModules is not None:
                self.detectorInfo.setNModules(self.args.nModules)
                self.detType = self.detectorInfo.getCameraType()
        else:
            self.detType = self.args.detType

        self.analyzedModules = self.experimentHash.get("analyzedModules", None)
        if self.analyzedModules is not None:
            try:
                self.analyzedModules = range(self.detectorInfo.nModules)
            except Exception as e:
                print("Error evaluating range: " + str(e))
                logger.info("Error evaluating range: " + str(e))

        self.g0cut = self.detectorInfo.g0cut
        if self.g0cut is not None:
            self.gainBitsMask = self.g0cut - 1
        else:
            self.gainBitsMask = 0xFFFF  ## might be dumb. for non-autoranging

        self.negativeGain = self.detectorInfo.negativeGain  ## could just use the detector info in places it's defined

    def loadPedestalGainOffsetFiles(self):
        """
        Loads the pedestal, gain, and offset np files for analysis.
        The files-locations are specified with cmd-line arguments.
        """

        self.fivePedestalRun = self.args.fivePedestalRun  ## in case needed

        self.fakePedestal = None
        self.fakePedestalFile = self.args.fakePedestalFile
        if self.fakePedestalFile is not None:
            try:
                self.fakePedestal = np.load(self.fakePedestalFile)  ##cast to uint32???
            except Exception as e:
                print("Error loading fake pedistal: " + str(e))
                logger.exception("Error loading fake pedistal: " + str(e))

        self.g0PedFile = self.args.g0PedFile
        if self.g0PedFile is not None:
            ##self.g0Ped = np.load(self.g0PedFile)
            self.g0Ped = np.array([np.load(self.g0PedFile)])  ##temp hack
            print(self.g0Ped.shape)

        self.g1PedFile = self.args.g0PedFile
        if self.g1PedFile is not None:
            ##self.g1Ped = np.load(self.g1PedFile)
            self.g1Ped = np.array([np.load(self.g1PedFile)])  ##temp hack

        self.g0GainFile = self.args.g0GainFile
        if self.g0GainFile is not None:
            self.g0Gain = np.load(self.g0GainFile)

        self.g1GainFile = self.args.g1GainFile
        if self.g1GainFile is not None:
            self.g1Gain = np.load(self.g1GainFile)

        self.offsetFile = self.args.offsetFile
        if self.offsetFile is not None:
            self.offset = np.load(self.offsetFile)

    def setupOutputDirString(self, analysisType):
        """
        Sets up the output directory for saving output file (default dir-name is based on the analysis type).
        The output directory can be specified via a command-line argument, and its location must be specified relative to the
        'OUTPUT_ROOT environment variable. If the directory does not exist, it logs error and exits.
        """
            
        # output dir is where we dump .npy, .h5, and .png files
        self.outputDir = "/%s/" % (analysisType)
        if self.args.path is not None:
            self.outputDir = self.args.path
        # if set, output folders will be relative to OUTPUT_ROOT
        # if not, they will be relative to the current script file
        self.outputDir = os.getenv("OUTPUT_ROOT", ".") + self.outputDir
        # check if outputDir exists, if does not create it and tell user
        if not os.path.exists(self.outputDir):
            print("could not find output dir: " + self.outputDir)
            logger.info("could not find output dir: " + self.outputDir)
            print("please create this dir, exiting...")
            logger.info("please create this dir, exiting...")
            exit(1)
            # the following doesnt work with mpi parallelism (other thread could make dir b4 curr thread)
            # print("so creating dir: " + self.outputDir)
            # logger.info("creating dir: " + self.outputDir)
            # os.makedirs(self.outputDir)
            # give dir read, write, execute permissions
            # os.chmod(self.outputDir, 0o777)
        else:
            print("output dir: " + self.outputDir)
            logger.info("output dir: " + self.outputDir)

    #### End of setup related functions ####

    #### Start of common getter functions ####

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == psana.EvrData.ConfigV7:
                self.evrs.append(key.src())

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

    #### End of common getter functions ####

    #### Start of common setter functions ####

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

    #### End of common setter functions ####

    #### Start of common utility functions ####

    def sliceToDetector(self, sliceRow, sliceCol):  ## cp from AnalyzeH5: import?
        return sliceRow + self.sliceCoordinates[0][0], sliceCol + self.sliceCoordinates[1][0]

    def getNswitchedPixels(self, data, region=None):
        return ((data >= self.g0cut) * 1).sum()

    def dumpEventCodeStatistics(self):
        print(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )
        logger.info(
            "have counted %d run triggers, %d DAQ triggers, %d beam events"
            % (self.nRunCodeEvents, self.nDaqCodeEvents, self.nBeamCodeEvents)
        )

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
    
    #### End of common utility functions ####

    #### Start of analysis/correction functions ####

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
       
    #### End of analysis/correction functions ####
