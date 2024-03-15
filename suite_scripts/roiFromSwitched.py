from calibrationSuite.basicSuiteScript import *


class RoiFromSwitched(BasicSuiteScript):
    def __init__(self):
        super().__init__()  ##self)


if __name__ == "__main__":
    rfs = RoiFromSwitched()
    print("have built an RFS")
    rfs.setupPsana()
    switchedPixels = None
    nGoodEvents = 0
    while True:
        evt = rfs.getEvt()
        if evt is None:
            break
        rawFrames = rfs.getRawData(evt, gainBitsMasked=False)
        if rawFrames is None:
            print("No contrib found")
            continue

        fG1 = rawFrames >= rfs.g0cut
        try:
            switchedPixels = np.bitwise_or(fG1, switchedPixels)
        except:
            ##print("first time hopefully")
            switchedPixels = fG1  ##copy?

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            print("switched pixels: %d" % ((switchedPixels > 0).sum()))

        if nGoodEvents > rfs.maxNevents:
            break

    np.save("roiFromSwitched_r%d_c%d.npy" % (rfs.run, rfs.camera), switchedPixels)
    print("%d pixels were in low at least once in %d events" % ((switchedPixels > 0).sum()))
