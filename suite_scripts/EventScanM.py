##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from TimeScanM import *


class EventScan(TimeScanM):
    def __init__(self):
        super().__init__()

    def getScanValue(self, foo, bar):
        return self.nGoodEvents


if __name__ == "__main__":
    a = EventScan()
    super(EventScan, a).main()
