import h5py
import numpy as np
import pixelAnalysis
import matplotlib.pyplot as plt
import argparse
import logging


class FileNamingInfo:
    def __init__(self, outputDir, className, run, camera, label):
        self.outputDir = outputDir
        self.className = className
        self.run = run
        self.camera = camera
        self.label = label

# Setup logging.
# Log file gets appended to each new run, can manually delete for fresh log.
# Could change so makes new unique log each run or overwrites existing log.
logging.basicConfig(
    filename='analyze_h5.log',
    level=logging.INFO, # For full logging set to INFO which includes ERROR logging too
    format='%(asctime)s - %(levelname)s - %(message)s' # levelname is log severity (ERROR, INFO, etc)
)


# Analysis of Hierarchical Data Format files (.h5 files)
class AnalyzeH5(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Configures calibration suite, overriding experimentHash",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument("-e", "--exp", help="experiment")
        # parser.add_argument('-l', '--location', help='hutch location, e.g. MfxEndstation or DetLab')
        parser.add_argument("-r", "--run", type=int, help="run")
        parser.add_argument("-R", "--runRange", help="run range, format ...")
        parser.add_argument("-p", "--path", type=str, default="../test/", help="the base path to the output directory")
        parser.add_argument(
            "-d", "--detType", type=str, default="", help="Epix100, Epix10ka, Epix10kaQuad, Epix10ka2M, ..."
        )
        parser.add_argument(
            "-f", "--files", type=str, default=None, help="run analysis on file or comma-separated files"
        )
        parser.add_argument("-s", "--slice_edges", type=str, help="two ints for row and col, separated by ','")
        parser.add_argument("-L", "--label", type=str, default="testLabel", help="analysis label")
        parser.add_argument("-sb", "--shift_energy_bits", action="store_true", help="use if want energy-values << 1")
        parser.add_argument("-a", "--analysis_mode", type=int, help="choose analysis mode 1 or 2")
        args = parser.parse_args()

        if args.files == None:
            print("No input files specified, quitting...")
            logging.info("No input files specified, quitting...")
            exit(1)

        self.files = args.files.replace(" ", "")
        self.lowEnergyCut = 4  # fix - should be 0.5 photons or something
        self.highEnergyCut = 30  # fix - should be 1.5 photons or something
        self.sliceEdges = None
        if args.slice_edges is not None:
            self.sliceEdges = args.slice_edges.split(",")
            self.sliceEdges = [int(curr) for curr in self.sliceEdges]
        self.nBins = 100
        self.shiftEnergy = False if args.shift_energy_bits == None else True
        self.analysisNum = 1 if args.analysis_mode == None else int(args.analysis_mode)
        self.fileNameInfo = FileNamingInfo(args.path, self.__class__.__name__, args.run, 0, args.label,)
        print("Output dir: " + self.fileNameInfo.outputDir)
        logging.info("Output dir: " + self.fileNameInfo.outputDir)

    def getFiles(self):
        fileNames = self.files.split(",")
        self.h5Files = []
        for currName in fileNames:
            currFile = h5py.File(currName)
            self.h5Files.append(currFile)
            print("Using input file: " + currFile.filename)
            logging.info("Using input file: " + currFile.filename)

    def identifyAnalysis(self):
        # script fails earlier if not >= 1 h5 file
        if "analysisType" in self.h5Files[0]:
            self.analysisType = self.h5Files[0]["analysisType"]
            # '[()]' gets us the data and not a reference
            self.sliceCoordinates = self.h5Files[0]["sliceCoordinates"][()]
        else:
            # do something useful here, maybe
            # but for now
            self.analysisType = "cluster"
            if self.sliceEdges == None:  # set if not already by cmdline args
                self.sliceEdges = [288 - 270, 107 - 59]
            self.sliceCoordinates = [[270, 288], [59, 107]]

    def analyze(self):
        if self.analysisType == "cluster":
            self.clusterAnalysis()
        else:
            errorString = "unknown analysis type %s" % (self.analysisType)
            print(errorString)
            logging.error(errorString)

    def clusterAnalysis(self):
        # energyHist = None
        clusters = np.concatenate([h5["clusterData"][()] for h5 in self.h5Files])

        # concat never works here since h5 undefined
        try:
            # meant to do similar thing as clusters above?
            energyHist = None  # np.concatenate(energyHist, h5["energyHistogram"][()])
            # self.plotEnergyHist(energyHist, self.fileNameInfo)
        except Exception as e:
            print(f"An exception occurred: {e}")
            logging.error(f"An exception occurred: {e}")
            pass

        fileName = "%s/r%d_clusters.npy" % (self.fileNameInfo.outputDir, self.fileNameInfo.run)
        logging.info("Writing npy: " + fileName)
        np.save(fileName, clusters)

        self.analyzeSimpleClusters(clusters)

    def plotEnergyHist(self, energyHist, fileInfo):
        _, bins = np.histogram(energyHist, 250, [-5, 45])

        plt.hist(bins[:-1], bins, weights=energyHist)  # , log=True)
        plt.grid(which="major", linewidth=0.5)
        plt.title = "All pixel energies in run after common mode correction"
        plt.xlabel = "energy (keV)"
        print("I hate matplotlib so much")
        logging.info("I hate matplotlib so much")

        fileNamePlot = "%s/%s_r%d_c%d_%s_energyHistogram.png" % (
            fileInfo.outputDir,
            fileInfo.className,
            fileInfo.run,
            fileInfo.camera,
            fileInfo.label,
        )
        logging.info("Writing plot: " + fileNamePlot)
        plt.savefig(fileNamePlot)

        fileNameNpy = "%s/%s_r%d_c%d_%s_energyHistogram.npy" % (
            fileInfo.outputDir,
            fileInfo.className,
            fileInfo.run,
            fileInfo.camera,
            fileInfo.label,
        )
        logging.info("Writing npy: " + fileNameNpy)
        np.save(fileNameNpy, energyHist)
        plt.close()

    def plot_overall_energy_distribution(self, energy, fileInfo):
        ax = plt.subplot()

        # print(energy[energy>0][666:777])
        print("mean energy above 0:", energy[energy > 0].mean())
        logging.info("mean energy above 0:" + str(energy[energy > 0].mean()))

        ax.hist(energy[energy > 0], 100)  # 100 bins
        plt.xlabel = "energy (keV)"
        plt.title = "All pixels"

        fileName = "%s/%s_r%d_c%d_%s_E.png" % (
            fileInfo.outputDir,
            fileInfo.className,
            fileInfo.run,
            fileInfo.camera,
            fileInfo.label,
        )
        logging.info("Writing plot: " + fileName)
        plt.savefig(fileName)
        plt.close()

    def save_fit_information(self, fitInfo, rows, cols, fileInfo):
        fileName = "%s/%s_r%d_c%d_r%d_c%d_%s_fitInfo.npy" % (
            fileInfo.outputDir,
            fileInfo.className,
            fileInfo.run,
            fileInfo.camera,
            rows - 1,
            cols - 1,
            fileInfo.label,
        )
        logging.info("Writing npy: " + fileName)
        np.save(fileName, fitInfo)

    def plot_gain_distribution(self, fitInfo, fileInfo, fitIndex):
        gains = fitInfo[:, :, fitIndex]
        goodGains = gains[np.bitwise_and(gains > 0, gains < 30)]

        ax = plt.subplot()
        ax.hist(goodGains, 100)
        ax.set_xlabel("energy (keV)")
        ax.set_title("pixel single photon fitted energy")
        fileName = "%s/%s_r%d_c%d_%s_gainDistribution.png" % (
            fileInfo.outputDir,
            fileInfo.className,
            fileInfo.run,
            fileInfo.camera,
            fileInfo.label,
        )
        logging.info("Writing plot: " + fileName)
        plt.savefig(fileName)

    def analyzeSimpleClusters(self, clusters):
        energy = clusters[:, :, 0] #.flatten()
        if self.shiftEnergy:
            energy *= 2  # temporary, due to bit shift
        rows = self.sliceEdges[0]
        cols = self.sliceEdges[1]
        fitInfo = np.zeros((rows, cols, 4)) # mean, std, mu, sigma
        fitIndex = 0

        self.plot_overall_energy_distribution(energy, self.fileNameInfo)
        
        print("Analysis Mode: " + str(self.analysisNum))
        logging.info("Analysis Mode: " + str(self.analysisNum))
        if self.analysisNum == 1:
            fitIndex = 2
            fitInfo = pixelAnalysis.analysis_one(clusters, energy, rows, cols, fitInfo, self.lowEnergyCut, self.highEnergyCut, self.fileNameInfo)
        else:
            fitIndex = 3
            fitInfo = pixelAnalysis.analysis_two(clusters, self.nBins, self.sliceCoordinates, rows, cols, fitInfo, self.lowEnergyCut, self.highEnergyCut, self.fileNameInfo)

        self.save_fit_information(fitInfo, rows, cols, self.fileNameInfo)
        self.plot_gain_distribution(fitInfo, self.fileNameInfo, fitIndex)


if __name__ == "__main__":
    print("Starting new run!")
    logging.info("Starting new run!")
    ah5 = AnalyzeH5()
    ah5.getFiles()
    ah5.identifyAnalysis()
    ah5.analyze()
