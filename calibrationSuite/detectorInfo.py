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
        knownTypes = ['epixhr', 'epixM', 'rixsCCD']
        if detType not in knownTypes:
            print ("type %s not in known types" %detType, knownTypes)

        self.nRows = 1
        self.nCols = 1
        self.nColsPerBank = 1
        self.detNbanks = 1
        self.nBanksCol = 1
        self.nRowsPerBank = 1
        self.dimension = 1

        if detType == 'epixhr':
            self.setup_epixhr()
        elif detTpye == 'epixM':
            self.setup_epixM()
        elif detType == 'rixsCCD':
            self.setup_rixsCCD()

    def setup_epixhr(self, version=0):
        self.nRows = 288
        self.nCols = 666
        self.nColsPerBank = 96
        self.detNbanks = int(self.nCols / self.nColsPerBank)
        self.nBanksCol = 2
        self.nRowsPerBank = int(self.nRows / self.nBanksCol)

        # self.gainMode = self.getGainMode()
        self.preferredCommonMode = 'regionCommonMode'
        self.clusterShape = [3,3]

    def setup_epixM(self, version=0):
        #wip
        self.test = 0

    def setup_rixsCCD(self, version=0):
        #self.dimension = self.getDimension()##1d or 2d
        #if self.dimension == '1d':
            #self.nRows = 0
       self.test = 0

