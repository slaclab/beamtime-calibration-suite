import h5py
import numpy as np
import fitFunctions
import matplotlib.pyplot as plt
import argparse

class AnalyzeH5(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Configures calibration suite, overriding experimentHash",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument("-e", "--exp", help="experiment")
        ##parser.add_argument('-l', '--location', help='hutch location, e.g. MfxEndstation or DetLab')
        parser.add_argument("-r", "--run", type=int, help="run")
        parser.add_argument("-R", "--runRange", help="run range, format ...")
        parser.add_argument("-p", "--path", type=str, default="../test/", help="the base path to the output directory")
        parser.add_argument(
            "-d", "--detType", type=str, default="", help="Epix100, Epix10ka, Epix10kaQuad, Epix10ka2M, ..."
        )
        parser.add_argument(
            "-f", "--files", type=str, default=None, help="run analysis on file or comma-separated files"
        )
        parser.add_argument("-L", "--label", type=str, default="testLabel", help="analysis label")

        args = parser.parse_args()

        self.run = args.run
        self.files = args.files.replace(" ", "")
        self.outputDir = args.path
        self.label = args.label
        self.camera = 0

    def getFiles(self):
        fileNames = self.files.split(",")
        self.h5Files = []
        for currName in fileNames:
            currFile = h5py.File(currName)
            self.h5Files.append(currFile)

    def identifyAnalysis(self):
        try:
            self.analysisType = self.h5Files[0]["analysisType"]
            self.sliceEdges = self.h5Files[0]["analysisType"][()]
        except Exception:
            ## do something useful here, maybe
            ## but for now
            self.analysisType = "cluster"
            self.sliceEdges = [288 - 270, 107 - 59]

    def analyze(self):
        if self.analysisType == "cluster":
            self.clusterAnalysis()
        else:
            print("unknown analysis type %s" % (self.analysisType))

    def plotEnergyHist(self, energyHist):
        _, bins = np.histogram(energyHist, 250, [-5, 45])
        plt.hist(bins[:-1], bins, weights=energyHist)  ##, log=True)
        plt.grid(which="major", linewidth=0.5)
        plt.title = "All pixel energies in run after common mode correction"
        plt.xlabel = "energy (keV)"
        print("I hate matplotlib so much")
        plt.savefig(
            "%s/%s_r%d_c%d_%s_energyHistogram.png"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, self.label)
        )
        np.save(
            "%s/%s_r%d_c%d_%s_energyHistogram.npy"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, self.label),
            energyHist,
        )
        plt.close()

    def clusterAnalysis(self):
        clusters = None
        #energyHist = None

        clusters = np.concatenate([h5["clusterData"][()] for h5 in self.h5Files])

        # concat never works, h5 undefined
        try:
            # meant to do similar thing as clusters above?
            energyHist = None #np.concatenate(energyHist, h5["energyHistogram"][()])
            #self.plotEnergyHist(energyHist)
        except Exception:
            pass

        self.lowEnergyCut = 4  ## fix - should be 0.5 photons or something
        self.highEnergyCut = 30  ## fix - should be 1.5 photons or something
        ##tmp
        np.save("%s/r%d_clusters.npy" % (self.outputDir, self.run), clusters)
        self.analyzeSimpleClusters(clusters)

    def analyzeSimpleClusters(self, clusters):
        ax = plt.subplot()
        energy = clusters[:, :, 0]  ##.flatten()
        energy *= 2  ## temporary, due to bit shift
        ##print(energy[energy>0][666:777])
        print("mean energy above 0:", energy[energy > 0].mean())
        ax.hist(energy[energy > 0], 100)
        plt.xlabel = "energy (keV)"
        plt.title = "All pixels"
        plt.savefig(
            "%s/%s_r%d_c%d_%s_E.png" % (self.outputDir, self.__class__.__name__, self.run, self.camera, self.label)
        )
        plt.close()

        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        fitInfo = np.zeros((rows, cols, 4))  ## mean, std, mu, sigma
        for i in range(rows):
            for j in range(cols):
                pixel = np.bitwise_and((clusters[:, :, 1] == i), (clusters[:, :, 2] == j))
                small = np.bitwise_and((clusters[:, :, 3] < 4), (clusters[:, :, 4] == 1))
                smallPixel = np.bitwise_and(small, pixel)
                pixelEcut0 = np.bitwise_and(
                    smallPixel, energy > self.lowEnergyCut
                )  ## adjusted due to gains not making sense
                pixelEcut = np.bitwise_and(
                    pixelEcut0, energy < self.highEnergyCut
                )  ## would be good to get rid of these entirely when things make sense
                nPixelClusters = (pixelEcut > 0).sum()
                mean = std = mu = sigma = 0
                pixelE = energy[pixelEcut > 0]
                print("nPixelClusters: ", nPixelClusters)
                if nPixelClusters > 5:
                    print("pixel %d,%d has %d photons" % (i, j, nPixelClusters))
                    ax = plt.subplot()
                    y, bin_edges, _ = ax.hist(pixelE, 100)
                    bins = (bin_edges[:-1] + bin_edges[1:]) / 2
                    ##print(y, bins)
                    mean, std = fitFunctions.estimateGaussianParameters(pixelE)
                    try:
                        popt, pcov = fitFunctions.curve_fit(fitFunctions.gaussian, bins, y, [3, mean, std])
                        mu = popt[1]
                        sigma = popt[2]
                        fitInfo[i, j] = (mean, std, popt[1], popt[2])
                        fittedFunc = fitFunctions.gaussian(bins, *popt)
                        ax.plot(bins, fittedFunc, color="b")
                    except Exception:
                        pass

                    ax.set_xlabel("energy (keV)")
                    ax.set_title("pixel %d,%d in slice, small cluster cuts" % (i, j))
                    plt.figtext(0.7, 0.8, "%d entries" % (nPixelClusters))
                    plt.figtext(0.7, 0.75, "mu %0.2f" % (mu))
                    plt.figtext(0.7, 0.7, "sigma %0.2f" % (sigma))
                    plt.savefig(
                        "%s/%s_r%d_c%d_r%d_c%d_%s_E.png"
                        % (self.outputDir, self.__class__.__name__, self.run, self.camera, i, j, self.label)
                    )
                    plt.close()

        np.save(
            "%s/%s_r%d_c%d_r%d_c%d_%s_fitInfo.npy"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, i, j, self.label),
            fitInfo,
        )
        gains = fitInfo[:, :, 2]
        goodGains = gains[np.bitwise_and(gains > 0, gains < 30)]
        ax = plt.subplot()
        ax.hist(goodGains, 100)
        ax.set_xlabel("energy (keV)")
        ax.set_title("pixel single photon fitted energy")
        plt.savefig(
            "%s/%s_r%d_c%d_%s_gainDistribution.png"
            % (self.outputDir, self.__class__.__name__, self.run, self.camera, self.label)
        )

if __name__ == "__main__":
    ah5 = AnalyzeH5()
    ah5.getFiles()
    ah5.identifyAnalysis()
    ah5.analyze()
