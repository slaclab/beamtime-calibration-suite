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
This class has setup-code and variables common for both psana bases.
(psana1Base and psana2Base must inherit from this class! ('PsanaCommon'))
"""

import importlib.util
import logging

## for parallelism
import os
import sys

import numpy as np

from calibrationSuite.argumentParser import ArgumentParser
from calibrationSuite.detectorInfo import DetectorInfo

logger = logging.getLogger(__name__)


class PsanaCommon(object):
    def __init__(self, analysisType="scan"):
        print("in psanaCommon")
        logger.info("in psanaCommon")

        self.analysisType = analysisType  ## fix below

        self.args = ArgumentParser().parse_args()
        logger.info("parsed cmdline args: " + str(self.args))

        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}

        self.ds = None
        self.det = None  ## do we need multiple dets in an array? or self.secondDet?

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283  ## per Matt
        ##self.beamCode = 281 ## don't see 283...

        # Variable-setup calls
        self.loadExperimentHashFromConfig()
        self.setupFromExperimentHash()
        self.setupFromCmdlineArgs()
        self.setupFromHashOrCmd()
        self.setupOutputDirString(analysisType)
        self.setupConfigHash()

    #### Start of setup related functions ####

    def loadExperimentHashFromConfig(self):
        """
        Loads the experiment config file (ex: beamtime-calibration-suite/config_files/epixMSuiteConfig.py)
        The config file is determined by checking the SUITE_CONFIG environment variable,
        then a command-line argument, and finally a default file 'suiteConfig.py' (in this order of precedence).
        If file cannot be found or read, exit the program.
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
            detVersion = self.experimentHash["detectorVersion"]
        except Exception:
            detVersion = 0

        try:
            self.detectorInfo = DetectorInfo(
                self.experimentHash["detectorType"],
                detSubtype=self.experimentHash["detectorSubtype"],
                detVersion=detVersion,
            )
        except Exception:
            self.detectorInfo = DetectorInfo(self.experimentHash["detectorType"], detVersion=detVersion)

        self.exp = self.experimentHash.get("exp", None)

        self.setupROIFiles()

        self.singlePixels = self.experimentHash.get("singlePixels", None)

        self.regionSlice = self.experimentHash.get("regionSlice", None)
        ## some code moved to setupFromHashOrCmd
        self.analyzedModules = self.experimentHash.get("analyzedModules", None)

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
                print("Error evaluating seedCut: " + str(e))
                logger.exception("Error evaluating seedCut: " + str(e))
                self.seedCut = None

        self.photonEnergy = self.args.photonEnergy
        self.aduPerKeV = self.args.aduPerKeV
        self.gainMode = self.args.gainMode
        
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

        print("command line det type:", self.args.detType)
        if self.args.detType == "":
            if self.args.nModules is not None:
                self.detectorInfo.setNModules(self.args.nModules)
                ##self.detType = self.detectorInfo.getCameraType()
        else:
            self.detType = self.args.detType
            jungfrau = epix10k = False
            if "epix10k" in self.detType.lower():
                epix10k = True
            elif "jungfrau" in self.detType.lower():
                jungfrau = True
            ## could allow just epix10k or jungfrau + n modules...
            if epix10k or jungfrau:
                if self.args.nModules is not None:
                    raise RuntimeError("should not specify exact detector type and n modules")
                if epix10k:
                    nModules = [
                        k
                        for k in self.detectorInfo.epix10kCameraTypes.keys()
                        if self.detectorInfo.epix10kCameraTypes[k] == self.detType
                    ]
                if jungfrau:
                    nModules = [
                        k
                        for k in self.detectorInfo.jungfrauCameraTypes.keys()
                        if self.detectorInfo.jungfrauCameraTypes[k] == self.detType
                    ]
                if nModules == []:
                    raise RuntimeError("could not determine n modules from detector type %s" % (self.detType))
                self.detectorInfo.setNModules(nModules[0])

        self.detectorInfo.setupDetector()
        ##self.detType = self.detectorInfo.getCameraType()
        self.detType = self.detectorInfo.detectorType

        ##self.analyzedModules = self.experimentHash.get("analyzedModules", None)
        ## why was this here?
        ## some code moved to setupFromHashOrCmd
        if self.args.analyzedModules is not None:
            self.analyzedModules = eval(self.args.analyzedModules)

        if self.args.regionSlice is not None:
            regionSliceArray = eval(self.args.regionSlice)
            if len(regionSliceArray) != 6:
                raise RuntimeError("expect 6 elements in region slice")
            a, b, c, d, e, f = regionSliceArray
            self.regionSlice = np.s_[a:b, c:d, e:f]

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

    def setupFromHashOrCmd(self):
        ## setup based on configuration information that can come from
        ## either experiment hash or command line
        if self.regionSlice is not None:
            ## n.b. expects 3d slice definition regardless for consistency
            if self.detectorInfo.dimension == 3:
                self.offset = 1
            self.sliceCoordinates = [
                [self.regionSlice[1].start, self.regionSlice[1].stop],
                [self.regionSlice[2].start, self.regionSlice[2].stop],
            ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1] - sc[0][0], sc[1][1] - sc[1][0]]
            ##print(self.regionSlice, sc, self.sliceEdges)
            if self.detectorInfo.dimension == 2:  ## remap to be 2d
                self.regionSlice = self.regionSlice[1:3]
                print("remapping regionSlice to be 2d")

        ## handle 1d rixs ccd data
        if self.detectorInfo.dimension == 1:
            self.regionSlice = self.regionSlice[0], self.regionSlice[2]
            print("remapping regionSlice to handle 1d case")
            logger.info("remapping regionSlice to handle 1d case")

        if self.analyzedModules is None:
            try:
                self.analyzedModules = range(self.detectorInfo.nModules)
            except Exception as e:
                print("Error evaluating range: " + str(e))
                logger.info("Error evaluating range: " + str(e))
        print("analyzing modules:", self.analyzedModules)

        if self.aduPerKeV is None:
            self.aduPerKeV = self.detectorInfo.aduPerKeV

        if self.gainMode == None:
            self.gainMode = 0 ## assume high gain or non-autoranging
            
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

    def setupConfigHash(self):
        ## info to write to h5 to help processing
        self.configHash = {
            "sliceCoordinates": self.sliceCoordinates,
            "analyzedModules": self.analyzedModules,
            "modules": self.detectorInfo.nModules,
            "rows": self.detectorInfo.nRows,
            "cols": self.detectorInfo.nCols,
        }

    #### End of setup related functions ####
