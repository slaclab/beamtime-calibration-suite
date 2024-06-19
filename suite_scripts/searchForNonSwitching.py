##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import matplotlib.pyplot as plt

from calibrationSuite.basicSuiteScript import BasicSuiteScript


class LinearityPlotsAutoranging(BasicSuiteScript):
    def __init__(self):
        super().__init__("scan")  ##self)

    def plotAutorangingData(self, g0s, g1s, g0Fluxes, g1Fluxes, label):
        ## this is just be for single pixels
        ## index in case that's ever supported
        ## only really makes sense as calib
        for i, p in enumerate(self.singlePixels):
            if len(g0s[i]) > 0:
                plt.scatter(g0Fluxes[i], g0s[i], c="r")
            if len(g1s[i]) > 0:
                plt.scatter(g1Fluxes[i], g1s[i], c="b")
            plt.xlabel("wave8 flux (ADU)")
            if "raw" in label:
                plt.ylabel("Red medium, blue low (ADU)")
            else:
                plt.ylabel("Red medium, blue low (keV)")
            if "yClip" in label:
                plt.ylim(0, 4000)
            if "xClip" in label:
                if len(g1Fluxes[i]) > 0:
                    plt.xlim(g1Fluxes[i].min() * 0.95, max(g1Fluxes[i].max(), g1Fluxes[i].max()) * 1.05)
                else:
                    plt.clf()
                    return
                ##lot of hackiness here

            plt.title(label)
            plt.savefig("%s/%s_p%d_r%d_c%d_%s.png" % (self.outputDir, self.className, i, self.run, self.camera, label))
            plt.clf()

    def plotDataROIs(self, means, flux, label, raw=True):
        ## assume no autoranging
        ## raw or calib
        if raw:
            ylabel = "ADU"
        else:
            ylabel = "keV"
        for i, roi in enumerate(self.ROIs):
            plt.scatter(flux, means[i])
            plt.xlabel("wave8 flux (ADU)")
            plt.ylabel("detector ROI mean (%s)" % (ylabel))
            plt.savefig(
                "%s/%s_roi%d_r%d_c%d_%s.png" % (self.outputDir, self.className, i, self.run, self.camera, label)
            )
            plt.clf()


if __name__ == "__main__":
    lpa = LinearityPlotsAutoranging()
    print("have built an LPA")
    doKazFlux = False
    if doKazFlux:
        print("doing Kaz flux events")
    else:
        print("not doing Kaz events")

    lpa.setupPsana()
    ##    efs.setROI('roiFromSwitched_e398_rmfxx1005021.npy')
    if lpa.run >= 550 and lpa.run < 590:  ## pinhole study range
        lpa.singlePixels = [[0, 115, 183], [0, 103, 172], [0, 116, 160], [0, 117, 160], [0, 293, 232], [0, 300, 240]]
        if doKazFlux:
            for i in range(-5, 5):
                for j in range(-5, 5):
                    if i == j == 0:
                        continue
                    lpa.singlePixels.append([0, 115 + i, 183 + j])

    if lpa.run > 650:
        if lpa.camera == 1:
            lpa.singlePixels = [[0, 20, 130], [0, 45, 133], [0, 95, 136], [0, 110, 139], [0, 125, 140], [0, 144, 145]]

    nGoodEvents = 0
    fluxes = []  ## common for all ROIs
    roiMeans = [[] for i in lpa.ROIs]
    g0s = [[] for i in lpa.singlePixels]
    g1s = [[] for i in lpa.singlePixels]
    g0Fluxes = [[] for i in lpa.singlePixels]
    g1Fluxes = [[] for i in lpa.singlePixels]
    gains = {}

    while True:
        if lpa.runRange is None:
            evt = lpa.getEvt()
        else:
            ##            evt = lpa.getEvtFromRuns()
            evt = lpa.getEvtFromRuns()
        if evt is None:
            break

        doFast = True  ## for 2400 etc Hz
        if doFast:
            ec = lpa.getEventCodes(evt)
            if ec[137]:
                lpa.flux = lpa._getFlux(evt)  ## fix this
                ##print("found flux", lpa.flux)
                continue
                # frames = lpa.det.calib(evt)
                ##frames = lpa.det.raw(evt)&0x3fff
            elif ec[281]:
                rawFrames = lpa.getRawData(evt, gainBitsMasked=False)
                frames = lpa.getCalibData(evt)
            else:
                continue
        else:
            lpa.flux = lpa._getFlux(evt)  ## fix this
            rawFrames = lpa.getRawData(evt, gainBitsMasked=False)
            frames = lpa.getCalibData(evt)

        ##rawFrames = lpa.det.raw(evt)
        ##frames = lpa.det.calib(evt)
        ##        rawFrames = lpa.getRawData(evt, gainBitsMasked=True)
        ##        frames = lpa.getCalibData(evt)
        if rawFrames is None:
            print("No contrib found")
            continue
        ## check for calib here I guess

        flux = lpa.getFlux(evt)
        if flux is None:
            print("no flux found")
            continue
        for i, roi in enumerate(lpa.ROIs):
            ##m = np.multiply(roi, frames).mean()
            m = frames[roi == 1].mean()
            roiMeans[i].append(m)
            if i == 0:
                fluxes.append(flux)

        if doKazFlux:
            rf = rawFrames[tuple(lpa.singlePixels[0])]
            if not (flux < 20000 and rf >= lpa.g0cut and rf > 2950):
                ##not a Kaz event
                nGoodEvents += 1
                if nGoodEvents > lpa.maxNevents:
                    break
                continue

        rows = 10 if (lpa.special and "testing" in lpa.special) else lpa.detectorInfo.nRows
        cols = 10 if (lpa.special and "testing" in lpa.special) else lpa.detectorInfo.nCols
        for x in range(rows):
            for y in range(cols):
                if "{}x{}".format(x, y) not in gains:
                    gains["{}x{}".format(x, y)] = [1 if rawFrames[0][x][y] > lpa.g0cut else 0]
                else:
                    gains["{}x{}".format(x, y)].append(1 if rawFrames[0][x][y] > lpa.g0cut else 0)

        nGoodEvents += 1
        if nGoodEvents % 100 == 0:
            print("n good events analyzed: %d" % (nGoodEvents))
            ##            print("switched pixels: %d" %((switchedPixels>0).sum()))

        if nGoodEvents > lpa.maxNevents:
            break

    for k in gains.keys():
        if 0 in gains[k] and 1 not in gains[k]:
            print("{}: high/medium gain".format(k))
            # continue #searching for low gain only
        elif 1 in gains[k] and 0 not in gains[k]:
            print("{}: low gain".format(k))
        else:
            continue
