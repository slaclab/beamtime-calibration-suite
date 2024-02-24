import argparse
import numpy as np
import importlib.util
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import sys
import h5py
from scipy.optimize import curve_fit ## here?
from calibrationSuite.fitFunctions import *
from calibrationSuite.ancillaryMethods import *
from calibrationSuite.argumentParser import ArgumentParser

import os
if os.getenv('foo') == '1':
    print("psana1")
    from calibrationSuite.psana1Base import *
else:
    print("psana2")
    from calibrationSuite.psana2Base import *


def sortArrayByList(a, data):
    return [x for _,x in sorted(zip(a, data), key=lambda pair:pair[0])]


class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType='scan'):
        super().__init__()
        ##print("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" %(self.psanaType))

        args = ArgumentParser().parse_args()

        ##mymodule = importlib.import_module(full_module_name)

        # if the SUITE_CONFIG env var is set use that, otherwise if the cmd line arg is set use that.
        # if neither are set, use the default 'suiteConfig.py' file.
        defaultConfigFileName = "suiteConfig.py"
        secondaryConfigFileName = defaultConfigFileName if args.configFile is None else args.configFile
        # secondaryConfigFileName is returned if env var not set
        configFileName = os.environ.get('SUITE_CONFIG', secondaryConfigFileName)
        config = self.importConfigFile(configFileName)
        if config is None:
            print("\ncould not find or read config file: " + configFileName)
            print("please set SUITE_CONFIG env-var or use the '-cf' cmd-line arg to specify a valid config file")
            print("exiting...")
            sys.exit(1)
        experimentHash = config.experimentHash

        logger.info("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" %(self.psanaType))
 
        self.gainModes = {"FH":0, "FM":1, "FL":2, "AHL-H":3, "AML-M":4, "AHL-L":5, "AML-L":6}
        self.ePix10k_cameraTypes = {1:"Epix10ka", 4:"Epix10kaQuad", 16:"Epix10ka2M"}
        self.camera = 0
        ##self.outputDir = '/sdf/data/lcls/ds/rix/rixx1003721/results/%s/' %(analysisType)
        self.outputDir = '../%s/' %(analysisType)
        ##self.outputDir = '/tmp'
        
        self.className = self.__class__.__name__

        try:
            self.location = experimentHash['location']
        except Exception:
            pass
        try:
            self.exp = experimentHash['exp']
        except Exception:
            pass
        try:
        ##if True:
            self.ROIfileNames = experimentHash['ROIs']
            self.ROIs = []
            for f in self.ROIfileNames:
                self.ROIs.append(np.load(f+'.npy'))
            try:  ## dumb code for compatibility or expectation
                self.ROI = self.ROIs[0]
            except Exception:
                pass
        ##if False:
        except Exception:
            print("had trouble finding", self.ROIfileNames)
            for currName in self.ROIfileNames:
                logger.exception("had trouble finding" + currName)        
            self.ROI = None
            self.ROIs = None
        try:
            self.singlePixels = experimentHash['singlePixels']
        except Exception:
            self.singlePixels = None
        try:
            self.regionSlice = experimentHash['regionSlice']
        except Exception:
            self.regionSlice = None
        if self.regionSlice is not None:
            self.sliceCoordinates = [[self.regionSlice[0].start,
                                      self.regionSlice[0].stop],
                                     [self.regionSlice[1].start,
                                      self.regionSlice[1].stop],
                                     ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1]-sc[0][0], sc[1][1]-sc[1][0]]
            
        try:
            self.fluxSource = experimentHash['fluxSource']
            try:
                self.fluxChannels = experimentHash['fluxChannels']
            except Exception:
                self.fluxChannels = range(8,16) ## wave8
            try:
                self.fluxSign = experimentHash['fluxSign']
            except Exception:
                self.fluxSign = 1
        except Exception:
            self.fluxSource = None

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283 ## per Matt
        ##self.beamCode = 281 ## don't see 283...
        self.fakeBeamCode = False
        
        
        ##mymodule = importlib.import_module(full_module_name)

        ## for standalone analysis
        self.file = None
        if args.files is not None:
            self.file = args.files
        self.label = ""
        if args.label is not None:
            self.label = args.label

        ## analyzing xtc
        if args.run is not None:
            self.run = args.run
        if args.camera is not None:
            self.camera = args.camera
        if args.exp is not None:
            self.exp = args.exp
        if args.location is not None:
            self.location = args.location
        if args.maxNevents is not None:
            self.maxNevents = args.maxNevents
        if args.skipNevents is not None:
            self.skipNevents = args.skipNevents
        if args.path is not None:
            self.outputDir = args.path
        self.detObj = args.detObj
        if args.threshold is not None:
            self.threshold = eval(args.threshold)
        else:
            self.threshold = None
        if args.fluxCut is not None:
            self.fluxCut = args.fluxCut
        try:
            self.runRange = eval(args.runRange) ## in case needed
        except Exception:
            self.runRange = None
            
        self.fivePedestalRun = args.fivePedestalRun ## in case needed
        self.fakePedestal = args.fakePedestal ## in case needed
        if self.fakePedestal is not None:
            self.fakePedestalFrame = np.load(self.fakePedestal) ##cast to uint32???
            
        if args.detType == '':
            ## assume epix10k for now
            if args.nModules is not None:
                self.detType = self.ePix10k_cameraTypes[args.nModules]
        else:
            self.detType = args.detType

        self.special = args.special
## done with configuration

        self.ds = None
        self.det = None ## do we need multiple dets in an array? or self.secondDet?

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


    def noCommonModeCorrection(self, frame):
        return frame
    
    def regionCommonModeCorrection(self, frame, region, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        regionCM = np.median(frame[region][frame[region]<arbitraryCut])
        return frame - regionCM
    
    def rowCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon

        ##rand = np.random.random()
        for r in range(self.detRows):
            colOffset = 0
            ##for b in range(0, self.detNbanks):
            for b in range(0, 2):
                try:
                    rowCM = np.median(frame[r, colOffset:colOffset + self.detColsPerBank][frame[r, colOffset:colOffset + self.detColsPerBank]<arbitraryCut])
                    ##if r == 280 and rand > 0.999:
                        ##print(b, frame[r, colOffset:colOffset + self.detColsPerBank], rowCM, rowCM<arbitraryCut-1, rowCM*(rowCM<arbitraryCut-1))
                    ##frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM*(rowCM<arbitraryCut-1)
                    frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM
                    ##if r == 280 and rand > 0.999:
                        ##print(frame[r, colOffset:colOffset + self.detColsPerBank], np.median(frame[r, colOffset:colOffset + self.detColsPerBank]))
                except Exception:
                    rowCM = -666
                    print("rowCM problem")
                    logger.exception("rowCM problem")
                    print(frame[r, colOffset:colOffset + self.detColsPerBank])
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
                    colCM = np.median(frame[rowOffset:rowOffset + self.detRowsPerBank, c][frame[rowOffset:rowOffset + self.detRowsPerBank, c]<arbitraryCut])
                    ##if r == 280 and rand > 0.999:
                        ##print(b, frame[r, colOffset:colOffset + self.detColsPerBank], rowCM, rowCM<arbitraryCut-1, rowCM*(rowCM<arbitraryCut-1))
                    ##frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM*(rowCM<arbitraryCut-1)
                    frame[rowOffset:rowOffset + self.detRowsPerBank, c] -= colCM
                    ##if r == 280 and rand > 0.999:
                        ##print(frame[r, colOffset:colOffset + self.detColsPerBank], np.median(frame[r, colOffset:colOffset + self.detColsPerBank]))
                except Exception:
                    colCM = -666
                    print("colCM problem")
                    logger.exception("colCM problem")
                    print(frame[rowOffset:rowOffset + self.detRowsPerBank], c)
                rowOffset += self.detRowsPerBank
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
        print("have counted %d run triggers, %d DAQ triggers, %d beam events"
              %(self.nRunCodeEvents,
                self.nDaqCodeEvents,
                self.nBeamCodeEvents)
              )
        logger.info("have counted %d run triggers, %d DAQ triggers, %d beam events"
              %(self.nRunCodeEvents,
                self.nDaqCodeEvents,
                self.nBeamCodeEvents)
              )
        

if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    logger.info("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
    logger.info(dir(evt))

