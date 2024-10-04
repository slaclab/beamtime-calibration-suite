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
    def __init__(self, detType, detSubtype="1d", detVersion=0):
        # declare all detector-specific info vars here in case any setup_X functions don't,
        # and use -1 so caller knows things are not setup (non-0 to avoid error on divide.
        self.nModules = -1
        self.detSubtype = detSubtype

        self.nRows = -1
        self.nCols = -1
        self.nColsPerBank = -1
        self.nBanks = -1
        self.nBanksRow = -1
        self.nBanksCol = -1
        self.nRowsPerBank = -1

        self.aduPerKeV = None
        self.negativeGain = False

        self.preferredCommonMode = None
        self.clusterShape = None

        self.g0cut = None
        self.seedCut = None
        self.neighborCut = None
        # end of detector-specific vars

        self.detectorType = detType
        self.detectorSubtype = detSubtype
        self.detectorVersion = detVersion
        self.cameraType = None
        self.dimension = 3  ## suite attempts not to know
        self.autoRanging = True

        knownTypes = [
            "epixhr",
            "epixm",
            "epix100",
            "Epix100a",
            "jungfrau",
            "Jungfrau",  ## cxic00121 has no alias in run 88
            "epix10k",
            "Epix10ka",
            "archon",
        ]
        if detType not in knownTypes:
            raise Exception("type %s not in known types %s" % (detType, str(knownTypes)))

        self.epix10kCameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.jungfrauCameraTypes = {1: "Jungfrau0.5", 2: "Jungfrau1M", 8: "Jungfrau4M"}

    def setupDetector(self):  ## needs nModules to be set
        if self.detectorType == "epixhr":
            self.setup_epixhr()
        elif self.detectorType == "epixm":
            self.setup_epixM()
        elif self.detectorType in ["epix100", "Epix100a"]:
            self.setup_epix100()
        elif self.detectorType == "archon":
            self.setup_rixsCCD()
        elif "jungfrau" in self.detectorType.lower():
            self.setup_jungfrau()
        elif "epix10k" in self.detectorType.lower():
            self.setup_epix10k()

    def setNModules(self, n):
        self.nModules = n

    def getCameraType(self):
        return self.cameraType

    def setup_epixhr(self):
        self.cameraType = "epixhr"
        self.g0cut = 1 << 14
        self.nRows = 288
        self.nCols = 284
        self.nColsPerBank = 96
        self.nBanksRow = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 2
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)
        # need to still implement getGainMode()
        # self.gainMode = self.getGainMode()
        self.preferredCommonMode = "regionCommonMode"
        self.clusterShape = [3, 3]
        self.seedCut = 4  ## maybe the minimum sensible
        self.neighborCut = 0.5  ## probably too low given the noise

    def setup_epixM(self):
        self.cameraType = "epixM"
        self.g0cut = 1 << 15
        self.nModules = 4
        ## per module (aka asic)
        self.nRows = 192
        self.nBanksRow = 4
        self.nRowsPerBank = int(self.nRows / self.nBanksRow)
        self.nCols = 384
        self.nBanksCol = 6
        self.nColsPerBank = int(self.nCols / self.nBanksCol)
        self.preferredCommonMode = "rowCommonMode"  ## guess
        self.clusterShape = [3, 3]
        self.gainMode = None  ## may want to know about default, softHigh, softLow
        if self.detectorVersion < 1:
            self.negativeGain = True
            print("N.b: using negative gain for version %d" % (self.detectorVersion))
        self.aduPerKeV = 666
        self.seedCut = 2
        self.neighborCut = 0.25  ## ditto

    def setup_epix100(self):
        self.cameraType = "Epix100a"
        self.autoRanging = False
        self.g0cut = 1 << 15
        self.dimension = 2
        self.nModules = 1
        self.nRows = 704
        self.nCols = 768
        self.nColsPerBank = 96
        self.nBanksRow = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 4
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)
        # need to still implement getGainMode()
        # self.gainMode = self.getGainMode()
        self.preferredCommonMode = "regionCommonMode"
        self.aduPerKeV = 18.0  ## approximate
        self.clusterShape = [3, 3]
        self.seedCut = 3
        self.neighborCut = 0.5

    def setup_jungfrau(self):
        self.cameraType = self.jungfrauCameraTypes[self.nModules]
        self.g0cut = 1 << 14
        self.g1cut = 2 << 14
        self.g2cut = 3 << 14
        self.nRows = 512
        self.nCols = 1024
        self.nColsPerBank = 256
        self.nBanksRow = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 1
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)
        # need to still implement getGainMode()
        # self.gainMode = self.getGainMode()
        self.preferredCommonMode = "regionCommonMode"
        self.clusterShape = [3, 3]
        self.aduPerKeV = 41  ## g0 only of course...
        self.seedCut = 3
        self.neighborCut = 0.5

    def setup_epix10k(self):
        self.cameraType = self.epix10kCameraTypes[self.nModules]
        self.g0cut = 1 << 14
        self.nRows = 352
        self.nCols = 384
        self.nColsPerBank = 96
        self.nBanksRow = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 2
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)
        # need to still implement getGainMode()
        # self.gainMode = self.getGainMode()
        self.preferredCommonMode = "colCommonMode"
        self.clusterShape = [3, 3]
        self.aduPerKeV = 16  ## high gain; 5.5 for medium
        self.seedCut = 3
        self.neighborCut = 0.5

    def setup_rixsCCD(self):
        print("rixsCCD mode:", self.detectorSubtype)
        self.cameraType = "rixsCCD"  ##+ mode ## psana should support mode
        self.autoRanging = False
        self.nTestPixelsPerBank = 36
        self.nBanks = 16
        self.nCols = 4800 - self.nBanks * self.nTestPixelsPerBank
        self.preferredCommonMode = "rixsCCDTestPixelSubtraction"
        if self.detectorSubtype == "1d":
            self.nRows = 1
            self.clusterShape = [1, 5]  ## might be [1,3]
            self.dimension = 2
        else:
            self.nRows = 1200
            self.clusterShape = [3, 5]  ## maybe
        self.g0cut = 1 << 16
