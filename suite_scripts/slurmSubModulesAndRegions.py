from subprocess import call
import time
from calibrationSuite.detectorInfo import DetectorInfo
##import sys

def calculateBlock(i, step, maxStep, analysisType):
    if i == 0:
        start = 0
        stop = step
    else:
        start = step * i
        stop = start + step
        if analysisType=='cluster':
            start -= 1 ## handle fact I don't fit edges
    if i<maxStep-1:
        if analysisType=='cluster':
            stop += 1 ## handle fact I don't fit edges
    return start, stop

## maybe get below from sys.argv

detectorName = 'Epix100a'
##detectorName = 'Jungfrau'

extraWrapString = ""
if detectorName == 'Epix100a':
    ## about 0.5M
    nRowBlocks = 2 ## for Zongde
    nColBlocks = 2
    nModules = 1
    exp = 'detdaq21'
    account = 'default' ## for the moment
    runs = [57]
    darkRun = 56

if detectorName == 'Jungfrau':##4M':
    exp = 'cxic00121'
    account = exp
    runs = [110, 111]
    darkRun = 88
    nModules = 8
    ## 0.5M
    nRowBlocks = 4 ## might be the norm
    nColBlocks = 4
    extraWrapString = " --nModules 8"

makeH5 = True
analyzeH5 = False
if makeH5 and analyzeH5:
    raise RuntimeError("one step at a time")
analysisType = "cluster"


detectorInfo = DetectorInfo(detectorName, nModules)
detectorInfo.setNModules(nModules)
detectorInfo.setupDetector()

nRows = detectorInfo.nRows
nCols = detectorInfo.nCols

modules = range(nModules)
rStep = nRows/nRowBlocks
cStep = nCols/nColBlocks
lastModule = modules[-1]

queue = 'milano'
##for run in [666]:
fp = open("sbatchSubmission_%d.sh" %(time.time()), 'w')
nJobs = 0
for m in modules:
    for run in runs:
        for rb in range(nRowBlocks):
            rStart, rStop = calculateBlock(rb, rStep, nRowBlocks, analysisType)
            for cb in range(nColBlocks):
                cStart, cStop = calculateBlock(cb, cStep, nColBlocks, analysisType)

                wrapString = "python -u -m mpi4py.run SimpleClustersParallelSlice.py -r %d --fakePedestal $OUTPUT_ROOT/dark/CalcNoiseAndMean_mean__r%d_step0.npy --seedCut 4 --label m%d_r%d-r%d-c%d-c%d --special slice --analyzedModules '[%d]' --regionSlice '[%d,%d,%d,%d,%d,%d]'" %(run, darkRun, m, rStart, rStop, cStart, cStop, m, 0, lastModule, rStart, rStop, cStart, cStop)
                wrapString += extraWrapString
                command = ["sbatch", "-o",
                           "r%d_m%d_r%d-r%d-c%d-c%d.log"
                           %(run, m, rStart, rStop, cStart, cStop),
                           "-p", "%s" %(queue),
                           "--account", "lcls:%s" %(account),
                           "--wrap", wrapString]
                ##print(" ".join(command))
                ##print(command)
                fp.write(" ".join(command)+'\n')
                ##call(command)
                nJobs += 1
                ##if nJobs == 1:
                ##    raise RuntimeError("foo")
