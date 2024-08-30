##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import sys

import h5py
import matplotlib.pyplot as plt
import numpy as np

from calibrationSuite.basicSuiteScript import BasicSuiteScript


class PersistenceCheckParallel(BasicSuiteScript):
    def __init__(self):
        super().__init__()  ##self)
        print("in", sys.argv[0])
        self.skipN = 0

    def plotData(self, data, label):
        print("plotStuff method")
        print(data.shape)
        ##        plt.graph(
        plt.scatter(data[:, 1], data[:, 0])
        plt.title("Run %d post-kick vs kick signal" % (self.run))
        plt.xlabel("pre-kick ROI mean (keV)")
        plt.ylabel("kicked ROI mean (keV)")
        plt.savefig("%s/%s_r%d_c%d%s.png" % (self.outputDir, self.className, self.run, self.camera, label))

    def analyze_h5(self, dataFile, label):
        a = h5py.File(dataFile)
        delays = np.array([k for k in a.keys()])
        delays = delays.astype("int")
        delays.sort()
        d = np.array([a[str(k)] for k in delays])
        delays = np.array([d for d in delays])

        print(delays)
        offset = len(self.ROIs)
        rois = d[:, 0:offset]
        pixels = d[:, offset:]
        runString = "_r%d" % (self.run)
        self.plotData(rois.T, pixels.T, delays, label + runString)


if __name__ == "__main__":
    pcp = PersistenceCheckParallel()
    print("have built a PC")

    if pcp.file is not None:
        pcp.analyze_h5(pcp.file, pcp.label)
        print("done with standalone analysis of %s, exiting" % (pcp.file))
        sys.exit(0)

    pcp.setupPsana()
    smd = pcp.ds.smalldata(
        filename="%s/%s_c%d_r%d_n%d.h5" % (pcp.outputDir, pcp.className, pcp.camera, pcp.run, pcp.size)
    )

    nEvent = -1
    nGoodEvents = 0

    evtGen = pcp.myrun.events()
    for nevt, evt in enumerate(evtGen):
        doFast = True  ##False ## for 2400 etc Hz
        if doFast:
            ec = pcp.getEventCodes(evt)
            if ec[137]:
                pcp.flux = pcp._getFlux(evt)  ## fix this
                pcp.fluxTS = pcp.getTimestamp(evt)
                continue
            elif ec[281]:
                pcp.framesTS = pcp.getTimestamp(evt)
                rawFrames = pcp.getRawData(evt, gainBitsMasked=False)
                frames = pcp.getCalibData(evt)
            else:
                continue
        else:
            pcp.flux = pcp._getFlux(evt)  ## fix this
            rawFrames = pcp.getRawData(evt, gainBitsMasked=False)
            frames = pcp.getCalibData(evt)

        if rawFrames is None:
            print("No contrib found")
            continue
        ## check for calib here I guess

        flux = pcp.getFlux(evt)
        if flux is None:
            print("no flux found")
            continue
        delta = pcp.framesTS - pcp.fluxTS
        if delta > 1000:
            print("frame - bld timestamp delta too large:", delta)
            continue

        rms = []
        for i, _ in enumerate(pcp.ROIs):
            rms.append(np.multiply(pcp.ROIs[i], frames).mean())

        pixelValues = []
        for i, roi in enumerate(pcp.singlePixels):
            pixelValues[i].append(frames[tuple(pcp.singlePixels[i])])

        kicked = pcp.isKicked(evt)

        smd.event(
            evt,
            timestamps=evt.datetime().timestamp(),
            rois=np.array(rms),
            pixels=np.array(pixelValues),
            kicked=np.array(kicked),
        )

    smd.done()
