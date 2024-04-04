##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################


class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType="scan"):
        super().__init__()
        

    


if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    logger.info("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
    logger.info(dir(evt))
