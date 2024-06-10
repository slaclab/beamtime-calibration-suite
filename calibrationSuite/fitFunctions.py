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

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from statsmodels.nonparametric.bandwidths import bw_silverman

logger = logging.getLogger(__name__)


def linear(x, a, b):
    return a * x + b


def saturatedLinear(x, a, b, c, d):
    return [a * X + b if X < c else d for X in x]


def saturatedLinearB(x, a, b, d):
    return [a * X + b if a * X + b < d else d for X in x]


def gaussian(x, a, mu, sigma):
    return a * np.exp(-((x - mu) ** 2) / (2 * sigma**2))


def gaussianArea(a, sigma):
    return a * sigma * 6.28


def estimateGaussianParametersFromUnbinnedArray(flatData):
    sigma = flatData.std()
    entries = len(flatData)
    ## will crash if sigma is 0
    return entries / (sigma * 6.28), flatData.mean(), sigma


def estimateGaussianParametersFromXY(x, y):
    mean, sigma = getHistogramMeanStd(x, y)
    ## will crash if sigma is 0
    return sum(y) / (sigma * 6.28), mean, sigma


def getHistogramMeanStd(binCenters, counts):
    mean = np.average(binCenters, weights=counts)
    var = np.average((binCenters - mean) ** 2, weights=counts)
    return mean, np.sqrt(var)


def calculateFitR2(y, fit):
    ss_res = np.sum((y - fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    try:
        r2 = 1 - (ss_res / ss_tot)
    except Exception:
        r2 = 1  ## I guess

    return r2


def getBinCentersFromNumpyHistogram(bins):
    return (bins[1:] + bins[:-1]) / 2.0


def getRestrictedHistogram(bins, counts, x0, x1):
    cut = np.where(np.logical_and(bins >= x0, bins <= x1))
    x = bins[cut]
    y = counts[cut]
    return x, y


def getGaussianFitFromHistogram(binCenters, counts, x0=None, x1=None):
    ## binned 1d data, optional fit restriction to [x0, x1]
    x = binCenters
    y = counts
    if x0 is not None:
        x, y = getRestrictedHistogram(x, y, x0, x1)

    a, mean, std = estimateGaussianParametersFromXY(x, y)
    popt, pcov = curve_fit(gaussian, x, y, [3, mean, std])
    ##a = popt[0]
    ##mu = popt[1]
    ##sigma = popt[2]
    fittedFunc = gaussian(x, *popt)

    ## should perhaps return an object with attributes for future flexibility
    return popt, fittedFunc


def fitNorm(data):
    mean, std = norm.fit(data)
    return mean, std


def fitLinearUnSaturatedData(x, y, saturated=False):  ##, gainMode, label):
    if saturated:
        ##f = saturatedLinear
        ##p0 = [1, 0, x.mean(), y.max()]
        f = linear
        p0 = [0, y.mean()]
        popt, pcov = curve_fit(f, x, y, p0=p0)
        f = saturatedLinearB
        p0 = [popt[0], popt[1], y.max()]
    else:
        f = linear
        ##m = y.mean(axis=-1)
        ##print("m.shape", m.shape, x.shape, y.shape)
        ##p0 = [m*0, m]
        p0 = [0, y.mean()]
    popt, pcov = curve_fit(f, x, y, p0=p0)
    y_fit = f(x, *popt)
    r2 = calculateFitR2(y, y_fit)

    ##condition = np.linalg.cond(pcov)
    return popt, pcov, y_fit, r2


def fitMatrixOfLinearFits(x, y):
    if len(x.shape) != 1:
        print("y data shape is %dd, not 1d" %(len(s)))
        raise Exception
    yShape = y.shape
    if len(yShape) != 4:
        print("y data shape is %dd, not 4d" %(len(yShape)))
        raise Exception
    slopesAndIntercepts = [fitLinearUnSaturatedData(a, ds[m, r, c, :])[0] for m in range(yShape[0]) for r in range(yShape[1]) for c in range(yShape[2])]
    return np.array(slopesAndIntercepts)


def linearFitTest():
    a = np.linspace(0, 9, 10)
    d0 = np.random.normal(1, 1, [3,5])
    d = np.array([d0 + i for i in range(10)])
    ds = np.stack(d, axis=-1)
    print("single pixel fit:")
    print(np.ravel(fitLinearUnSaturatedData(a, ds[2,2,:])[0]))

    print("array fit:")
    dss = ds.shape
    ## print(fitLinearUnSaturatedData(a, ds.reshape(np.prod(dss[0:-1]), dss[-1])))
    ## curve_fit wants a 1-d y array, can't see how to pass a matrix
    fitArray = [fitLinearUnSaturatedData(a, ds[i, j, :])[0][0] for i in range(dss[0]) for j in range(dss[1])]
    print(fitArray)

    print("array fit, all popt:")
    fitArray = [np.ravel(fitLinearUnSaturatedData(a, ds[i, j, :])[0]) for i in range(dss[0]) for j in range(dss[1])]
    fitArray = np.array(fitArray)
    print(fitArray)

    ##print("matrix call:")
    ##print(fitMatrixOfLinearFits(a, ds))
    
def twoGaussSilvermanModeTest(x0, x1):
    a = np.random.normal(0, 1, 1000)
    b = np.random.normal(x0, 1, 500)
    c = np.random.normal(x1, 1, 500)
    d = np.append(b, c)
    if False:
        import matplotlib.pyplot as plt

        plt.hist(d, 100)
        ##plt.hist(a, 100)
        plt.show()
    print(a.mean(), a.std(), d.mean(), d.std())
    print(x0, x1, bw_silverman(a), bw_silverman(d))
    return d.std() / a.std(), bw_silverman(d) / bw_silverman(a)


def testSilvermanModeTest():
    a = np.linspace(0, 3, 10)
    noise = []
    S = []
    for x1 in a:
        r0, r1 = twoGaussSilvermanModeTest(0, x1)
        noise.append(r0)
        S.append(r1)

    import matplotlib.pyplot as plt

    plt.plot(noise, S)
    plt.title("Two gaussian test of Silverman's test separating peaks")
    plt.xlabel("two peak rms/one peak rms")
    plt.ylabel("two peak Silverman/one peak Silverman")
    plt.show()

    a = np.random.normal(0, 100, 1000)
    b = np.random.normal(0, 100, 10000)
    c = np.where(b != 50)
    print("rms for a gap in gaussian, notched gaussian:", a.std(), b[c][:1000].std())
    print("Silverman for a gap in gaussian, notched gaussian:", bw_silverman(a), bw_silverman(b[c][:1000]))
    print("rms for a gap in gaussian/notched gaussian:", a.std() / b[c][:1000].std())
    print("Silverman for a gap in gaussian/notched gaussian:", bw_silverman(a) / bw_silverman(b[c][:1000]))


def missingBinTest(binCenters, counts):
    mu, sigma = getHistogramMeanStd(binCenters, counts)
    binCenters, counts = getRestrictedHistogram(binCenters, counts, mu - sigma, mu + sigma)
    ##print(len(b), len(c))
    n = len(counts)
    if n >= 10:
        step = int(n / 10)
    else:
        step = n

    cuts = range(1, 6)
    missingBins = np.zeros(len(cuts))

    for i in range(step):
        i0 = step * i
        i1 = min(step * (i + 1), n)
        med = np.median(counts[i0:i1])
        mean = counts[i0:i1].mean()
        rootN = np.sqrt(mean)
        for k in cuts:
            for j in range(i0, i1):
                if counts[j] < med - k * rootN:
                    missingBins[k] += 1
                    ##print(n, step, i, i0, i1, k, j, binCenters[j], counts[j], med-k*rootN)
    return missingBins


def testMissingBinTest():
    nSamples = 5000
    a = np.random.normal(0, 100, nSamples)
    b = np.random.normal(0, 100, nSamples * 2)
    missingValue = 30
    c = np.where(np.logical_or(b > (missingValue + 1), b < missingValue))
    b = b[c][:nSamples]
    ##print(50 in a, 50 in b)
    ha, bins = np.histogram(a, 600, [-300, 300])
    hb, _ = np.histogram(b, 600, [-300, 300])
    binCenters = getBinCentersFromNumpyHistogram(bins)
    ##print(binCenters, ha, hb)
    if True:
        import matplotlib.pyplot as plt

        plt.stairs(ha, bins)
        plt.stairs(hb, bins, color="b")
        plt.show()

    mbt_a = missingBinTest(binCenters, ha)
    mbt_b = missingBinTest(binCenters, hb)
    print("per n sigma check for gap in gaussian, notched gaussian:", mbt_a, mbt_b)
    print((range(1, 6) * mbt_a).sum(), (range(1, 6) * mbt_b).sum())
