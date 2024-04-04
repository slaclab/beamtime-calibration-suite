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

    def getRawData(self, evt, gainBitsMasked=True, negativeGain=False):
        frames = self.plainGetRawData(evt)
        if frames is None:
            return None
        if False and self.special:## turned off for a tiny bit of speed
            if 'thirteenBits' in self.special:
                frames = (frames & 0xfffe)
                ##print("13bits")
            elif 'twelveBits' in self.special:
                frames = (frames & 0xfffc)
                ##print("12bits")
            elif 'elevenBits' in self.special:
                frames = (frames & 0xfff8)
                ##print("11bits")
            elif 'tenBits' in self.special:
                frames = (frames & 0xfff0)
                ##print("10bits")
        if self.negativeGain or negativeGain:
            zeroPixels = frames==0
            maskedData = frames & self.gainBitsMask
            gainData = frames - maskedData
            frames = gainData + self.gainBitsMask - maskedData
            frames[zeroPixels] = 0
        if gainBitsMasked:
            return frames & self.gainBitsMask
        return frames

    def addFakePhotons(self, frames, occupancy, E, width):
        shape = frames.shape
        occ = np.random.random(shape)
        fakes = np.random.normal(E, width, shape)
        fakes[occ>occupancy] = 0
        return frames + fakes, (fakes>0).sum()
    
if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    logger.info("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))
    logger.info(dir(evt))
