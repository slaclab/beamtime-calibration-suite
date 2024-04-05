##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from calibrationSuite.psanaBase import PsanaBase


class RoiFromThreshold(BasicSuiteScript):
    def __init__(self):
        super().__init__()  ##self)
        print("in", sys.argv[0])
        ## temp hack

    def foo(self):
        print("foo")
        print("%d" % (self.run))


if __name__ == "__main__":
    rft = RoiFromThreshold()
    print("have built an RFT")
    rft.setupPsana()
    g0cut = 1 << 14
    aboveThresholdPixels = None
    ##    rft.maxNevents = 1000
    nGoodEvents = 0
    while True:
        evt = rft.getEvt()
        if evt is None:
            break
        rawFrames = rft.getRawData(evt, gainBitsMasked=True)
        if rawFrames is None:
            print("No contrib found")
            continue

        if not rft.detObj == "calib":
            thresholded = rawFrames >= rft.threshold
        else:
            frames = rft.det.calib(evt)
            thresholded = frames >= rft.threshold

        try:
            aboveThresholdPixels = np.bitwise_or(thresholded, aboveThresholdPixels)
        except:
            ##print("first time hopefully")
            aboveThresholdPixels = thresholded  ##copy?

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            print("aboveThreshold pixels: %d" % ((aboveThresholdPixels > 0).sum()))

        if nGoodEvents > rft.maxNevents:
            break

    label = "raw"
    if rft.detObj == "calib":
        label = "calib"
    np.save("roiFromAboveThreshold_r%d_c%d_%s.npy" % (rft.run, rft.camera, label), aboveThresholdPixels)
