##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

if os.getenv("foo") == "1":
    print("psana1")
    from calibrationSuite.psana1Base import PsanaBase
else:
    print("psana2")
    from calibrationSuite.psana2Base import PsanaBase


def sortArrayByList(a, data):
    return [x for _, x in sorted(zip(a, data), key=lambda pair: pair[0])]


class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType="scan"):
        super().__init__()

        print("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        logger.info("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" % (self.psanaType))
        self.className = self.__class__.__name__

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