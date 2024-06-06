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

import numpy

logger = logging.getLogger(__name__)


class Stats(object):
    def __init__(self, shape):
        self._n = 0
        self._x = numpy.zeros(shape)  ##, dtype=double)
        self._xx = numpy.zeros(shape)  ##, dtype=double)
        self._xy = numpy.zeros(shape)  ##, dtype=double)

    def mean(self):
        if self._n == 0:
            return None
        return self._x / self._n

    def rms(self):
        if self._n == 0:
            return None
        return (self._xx / self._n - (self._x / self._n) ** 2).clip(0) ** 0.5

    def corr(self, yMean, ySigma):
        ## return (self._xy -self._x*yMean)/self._n
        rms = self.rms()
        if rms.any() is None:
            return None

        rmsPosDef = rms.clip(0.000001, rms.max())

        if (self._n * ySigma * rmsPosDef).any() == 0:
            return None
        return numpy.double((self._xy - self._x * yMean) / (self._n * ySigma * rmsPosDef))

    def accumulate(self, x, y=0):
        self._n += 1
        self._x += x
        self._xx += x * x
        self._xy += x * y


if __name__ == "__main__":
    a = numpy.zeros([10])
    s = Stats(a.shape)
    for i in range(10000):
        d = numpy.sin((numpy.array(list(range(10))) + i) / 3.14159)
        s.accumulate(d, d[7])

    print("mean: " + str(s.mean()))
    print("rms: " + str(s.rms()))
    print("s.corr(s.mean()[7], s.rms()[7]): " + str(s.corr(s.mean()[7], s.rms()[7])))
    logger.info("mean: " + str(s.mean()))
    logger.info("rms: " + str(s.rms()))
    logger.info("s.corr(s.mean()[7], s.rms()[7]): " + str(s.corr(s.mean()[7], s.rms()[7])))
