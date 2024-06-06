##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import numpy as np
import sys
import matplotlib.pyplot as plt

data = np.load(sys.argv[1])
if True:
    ######plot amplitude vs time

    yscale = data.max()
    sumData = data.sum(axis=1)  ## right axis?

    xavierOrder = [15, 8, 14, 13, 12, 9, 10, 11]
    xavierPosition = [1, 5, 21, 25, 8, 14, 18, 12]
    t_s = range(data.shape[0])  ##right axis?
    mksize = 1
    for k in [1, 2, 3]:
        plt.figure(k)
        scale = yscale
        label = ""
        if k == 2:
            scale = 0.2
            label = "Normalized "
        for i in range(8):
            plt.subplot(5, 5, xavierPosition[i])
            if k != 3:
                plt.plot(t_s, data[:, xavierOrder[i]], ".b", markersize=mksize)
            else:
                plt.plot(sumData, data[:, xavierOrder[i]], ".b", markersize=mksize)
            plt.title("Diode %d" % (xavierOrder[i]))
            plt.ylim(0, scale)
        if k != 3:
            plt.suptitle("%sFlux Wave8 VS time (s)" % (label))
        else:
            plt.suptitle("Flux Wave8 vs total")

    plt.figure(4)
    plt.plot(t_s, sumData, ".b", markersize=mksize)
    plt.title("Sum of all Wave8 tiles VS event")
    #    plt.show()

    plt.figure(5)
    for i in range(8):
        plt.subplot(8, 1, i + 1)
        plt.hist(data[:, i + 8], 100)
        plt.ylabel("Diode %d" % (i + 8))

    plt.figure(6)
    for i in range(8):
        plt.subplot(8, 1, i + 1)
        plt.hist(data[:, i + 8], 1000)
        plt.ylabel("Diode norm should not matter %d" % (i + 8))

    plt.show()
