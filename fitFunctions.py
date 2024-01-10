import numpy as np
from scipy.stats import norm
from statsmodels.nonparametric.bandwidths import bw_silverman

def linear(x, a, b):
    return a*x + b

def saturatedLinear(x, a, b, c, d):
    return [a*X + b if X < c else d for X in x]

def saturatedLinearB(x, a, b, d):
    return [a*X + b if a*X+b < d else d for X in x]

def gaussian(x, a, mu, sigma):
    return a*np.exp(-(x-mu)**2/(2*sigma**2))

def estimateGaussianParameters(flatData):
    return flatData.mean(), flatData.std()

def getHistogramMeanStd(binCenters, counts):
    mean = np.average(binCenters, weights=counts)
    var = np.average((binCenters - mean)**2, weights=counts)
    return mean, np.sqrt(var)

def getBinCentersFromNumpyHistogram(bins):
    return (bins[1:] + bins[:-1])/2.

def getRestrictedHistogram(bins, counts, x0, x1):
    cut = np.where(np.logical_and(bins>=x0, bins<=x1))
    x = bins[cut]
    y = counts[cut]
    return x, y

def getGaussianFitFromHistogram(binCenters, counts, x0=None, x1=None):
    ## binned 1d data, optional fit restriction to [x0, x1]
    x = binCenters
    y = counts
    if x0 is not None:
        x, y = getRestrictedHistogram(x, y, x0, x1)
        
    mean, std = getHistogramMeanStd(x, y)
    popt, pcov = curve_fit(fitFunctions.gaussian, x, y, [3, mean, std])
    mu = popt[1]
    sigma = popt[2]
    fitInfo[i,j] = (mean, std, popt[1], popt[2])
    fittedFunc = fitFunctions.gaussian(x, *popt)

    ## should perhaps return an object with attributes for future flexibility
    return mu, sigma, fittedFunc
    
def fitNorm(data):
    mean, std = norm.fit(data)
    return mean, std


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
    return d.std()/a.std(), bw_silverman(d)/bw_silverman(a)

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
    c = np.where(b!=50)
    print("rms for a gap in gaussian, notched gaussian:", a.std(), b[c][:1000].std())
    print("Silverman for a gap in gaussian, notched gaussian:", bw_silverman(a), bw_silverman(b[c][:1000]))
    print("rms for a gap in gaussian/notched gaussian:", a.std()/b[c][:1000].std())
    print("Silverman for a gap in gaussian/notched gaussian:", bw_silverman(a)/bw_silverman(b[c][:1000]))

    
def missingBinTest(binCenters, counts):
    mu, sigma = getHistogramMeanStd(binCenters, counts)
    binCenters, counts = getRestrictedHistogram(binCenters, counts, mu-sigma, mu+sigma)
    ##print(len(b), len(c))
    n = len(counts)
    if n>=10:
        step = int(n/10)
    else:
        step = n
        
    cuts = range(1, 6)
    missingBins = np.zeros(len(cuts))
        
    for i in range(step):
        i0 = step*i
        i1 = min(step*(i+1), n)
        med = np.median(counts[i0:i1])
        mean = counts[i0:i1].mean()
        rootN = np.sqrt(mean)
        for k in cuts:
            for j in range(i0, i1):
                if counts[j]<med-k*rootN:
                    missingBins[k] += 1
                    ##print(n, step, i, i0, i1, k, j, binCenters[j], counts[j], med-k*rootN)
    return missingBins


def testMissingBinTest():
    nSamples = 5000
    a = np.random.normal(0, 100, nSamples)
    b = np.random.normal(0, 100, nSamples*2)
    missingValue = 30
    c = np.where(np.logical_or(b>(missingValue+1), b<missingValue))
    b = b[c][:nSamples]
    ##print(50 in a, 50 in b)
    ha, bins = np.histogram(a, 600, [-300, 300])
    hb,_ = np.histogram(b, 600, [-300, 300])
    binCenters = getBinCentersFromNumpyHistogram(bins)
    ##print(binCenters, ha, hb)
    if True:
        import matplotlib.pyplot as plt
        plt.stairs(ha, bins)
        plt.stairs(hb, bins, color='b')
        plt.show()

    mbt_a = missingBinTest(binCenters, ha)
    mbt_b = missingBinTest(binCenters, hb)
    print("per n sigma check for gap in gaussian, notched gaussian:", mbt_a, mbt_b)
    print((range(1,6)*mbt_a).sum(), (range(1,6)*mbt_b).sum())
