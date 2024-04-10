##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
class DetectorInfo:
    def __init__(self, detType):

        # declare these here in case any setup_X functions don't
        # and -1 so caller knows things are not setup (non-0 to avoid error on divide)

        self.detectorType = detType
        ## this information is per module
        self.nRows = -1
        self.nCols = -1
        self.nColsPerBank = -1
        self.nBanksRow = -1
        self.nBanksCol = -1
        self.nRowsPerBank = -1
        self.nColsPerBank = -1
        self.dimension = 3 ## suite attempts not to know
        self.nModules = -1
        self.aduPerKeV = None
        
        knownTypes = ['epixhr', 'epixm', 'archon']
        if detType not in knownTypes:
            raise Exception("type %s not in known types" % (detType, knownTypes))

        self.ePix10kCameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.chosenCameraType = None

        if detType == 'epixhr':
            self.setup_epixhr()
        elif detType == 'epixm':
            self.setup_epixM()
        elif detType == 'archon':
            self.setup_rixsCCD()

    def setNModules(self, n):
        self.choosenCameraType = self.ePix10kCameraTypes[n]

    def getCameraType(self):
        return self.choosenCameraType

    def setup_epixhr(self, version=0):
        self.nRows = 288
        self.nCols = 284
        self.nColsPerBank = 96
        self.detNbanks = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 2
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)

        #need to still implement getGainMode()
        #self.gainMode = self.getGainMode()
        self.preferredCommonMode = 'regionCommonMode'
        self.clusterShape = [3,3]
        self.seedCut = 4 ## maybe the minimum sensible
        self.neighborCut = 0.5 ## probably too low given the noise

    def setup_epixM(self, version=0):
        self.nModules = 4
        ## per module (aka asic)
        self.nRows = 192
        self.nBanksRow = 4
        self.nRowsPerBank = self.nRows/self.nBanksRow
        self.nCols = 384
        self.nBanksCol = 6
        self.nColsPerBank = self.nCols/self.nBanksCol
        self.preferredCommonMode = 'rowCommonMode'## guess
        self.clusterShape = [3,3]
        self.gainMode = None ## may want to know about default, softHigh, softLow
        self.aduPerKeV = 666
        self.seedCut = 4 ## hopefully can be lowered
        self.neighborCut = 0.5 ## ditto
        
    def setup_rixsCCD(self, mode='1d', version=0):
        self.nTestPixelsPerBank = 36
        self.nBanks = 16
        self.nCols = 4800 - self.nBanks*self.nTestPixelsPerBank
        self.preferredCommonMode = 'rixsCCDTestPixelSubtraction'
        if mode == '1d':
            self.nRows = 1
            self.clusterShape = [1,5] ## might be [1,3]
        else:
            self.nRows = 1200
            self.clusterShape = [3,5] ## maybe
            
