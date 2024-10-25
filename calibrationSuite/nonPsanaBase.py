import os
import sys

import h5py
import numpy as np

## actually not psana, should rename
## need this for DataSource.smalldata in analysis script
from calibrationSuite.psana2Base import *  ##DataSource

##from calibrationSuite.argumentParser import ArgumentParser
##import importlib.util
from calibrationSuite.psanaCommon import PsanaCommon

## do we actually need this?


class PsanaBase(PsanaCommon):  ## not actually psana, should rename
    def __init__(self, analysisType="scan"):
        super().__init__(analysisType)
        commandUsed = sys.executable + " " + " ".join(sys.argv)
        ##logger.info("Ran with cmd: " + commandUsed)

        self.psanaType = 0
        print("in nonPsanaBase")
        ##logger.info("in nonPsanaBase")
        self.myrun = None
        self.setupNonPsana()

    def setupNonPsana(self):
        ## temp hack ##
        ##self.args = ArgumentParser().parse_args()
        ## now done in PsanaCommon
        defaultConfigFileName = "suiteConfig.py"
        secondaryConfigFileName = defaultConfigFileName if self.args.configFile is None else self.args.configFile
        # secondaryConfigFileName is returned if env var not set
        configFileName = os.environ.get("SUITE_CONFIG", secondaryConfigFileName)
        config = self.importConfigFile(configFileName)
        if config is None:
            print("\ncould not find or read config file: " + configFileName)
            print("please set SUITE_CONFIG env-var or use the '-cf' cmd-line arg to specify a valid config file")
            print("exiting...")
            sys.exit(1)
        self.experimentHash = config.experimentHash
        ## temp ##
        nonXtcFiles = self.args.nonXtcFiles
        if nonXtcFiles is not None:
            self.file = None  ## nonPsanaBase only used as substitute xtc reader
            print(nonXtcFiles)
            self.setupNonXtcFiles(nonXtcFiles)

        if "run" not in dir(self) or self.run is None:
            self.run = 666666

        self.ignoreEventCodeCheck = True

    def setupNonXtcFiles(self, nonXtcFiles):
        if nonXtcFiles.endswith("h5"):
            self.h5File = h5py.File(nonXtcFiles)  ## need concat
            self.getDataFromFile()
            self.getStepInfoFromFile()
            self.npyFile = False
        elif nonXtcFiles.endswith("npy"):
            if "," in nonXtcFiles:
                self.data = np.concatenate([np.load(f) for f in nonXtcFiles.split(",")])
            else:
                self.data = np.load(nonXtcFiles)
                fixAlexOrdering = True
                if fixAlexOrdering:
                    self.data = np.array([np.array([self.data[:, :, i]]) for i in range(self.data.shape[2])])

            self.setDataArray(self.data)
            self.h5File = False
        else:
            raise Exception("non-psana file formats h5 and npy only")

    ##    def importConfigFile(self, file_path):
    ##        if not os.path.exists(file_path):
    ##            print(f"The file '{file_path}' does not exist")
    ##            return None
    ##        spec = importlib.util.spec_from_file_location("config", file_path)
    ##        config_module = importlib.util.module_from_spec(spec)
    ##        spec.loader.exec_module(config_module)
    ##        return config_module

    def getDataFromFile(self):
        self.data = self.h5File["frames"][()]
        self.setDataArray(self.data)

    def getStepInfoFromFile(self):
        try:
            self.step_value = self.h5File["step_value"][()]
        except:
            print("could not find step_value in h5 file foo")
            self.step_value = [None]

    def setDataArray(self, data):
        self.data = data
        print("data shape:", self.data.shape)
        self.dataIter = iter(self.data)
        print("have set up dataIter")
        self.myrun = MyRun(self.data)

    def getStepGen(self):
        self.stepIndex = -1  ## needed?
        return self.stepGen()

    def setupPsana(self):  ## should rename to setupBase or whatever
        print("in fake setupPsana; get info from npy or h5 and fake stuff")
        if False:
            self.ds = DataSource(files=[nonXtcFiles])  ## to make smalldata happy
            print("data source is", self.ds)
        else:
            self.ds = psana.DataSource(exp="rixx1005922", run=6)  ##66)
            ##self.ds = psana.MPIDataSource('exp=detdaq23:run=1')##66)
            ## get event to make smd call happy
            ##evt = next(self.ds.events())
        self.skipZeroCheck = True  ## some Alex data gets entirely lost else

        if False:
            self.getDataFromFile()
            self.getStepInfoFromFile()

    def stepGen(self):
        while True:
            try:
                self.stepIndex += 1
                step = Step(next(self.dataIter), self.stepIndex)
                yield step
            except:
                ##raise StopIteration
                return
            ##print("in stepGen, stepIndex:", self.stepIndex)

    def getScanValue(self, step, useStringInfo=False):
        if useStringInfo:
            ##print("no idea how to use stringInfo, giving up")
            ##sys.exit(0)
            pass
        ##print(self.step_value[step.nStep])
        ##print(type(self.step_value[step.nStep]))
        return self.step_value[step.nStep]

    def getEventCodes(self, foo):
        return [283]

    def plainGetRawData(self, evt):
        return evt.astype("uint16")

    def getFlux(self, foo):
        return 1

    def get_smalldata(self, filename):  ##, gather_interval=100):
        try:
            return self.ds.smalldata(filename=filename)  ##, gather_interval=gather_interval)
        except Exception:
            print("can't make smalldata - is datasource defined?")
        return None


class MyRun(object):
    def __init__(self, array):
        ## it would probably be smarter to have a reader (?) class instead
        ## of loading everything into memory
        ## could do
        ## with h5py.File('TID.data') as data:
        ##     frames = data['frames']
        ##     eventN = 0
        ##     while True:
        ##         try:
        ##             event = frames[eventN++, :...]
        ##             yield event
        ##         except:
        ##             return
        self.array = array

    def events(self):
        ## it would be smarter to yield the next event instead of filling RAM
        ##return(np.vstack(self.array))
        return self.array


class Step(object):
    def __init__(self, array, nStep):
        self.array = array
        self.nStep = nStep

    def events(self):
        return self.array


if __name__ == "__main__":
    npb = NonPsanaBase()

    print("try running over 2, 3, 2 step data with step calls")
    ##npb.setDataArray(np.load("../data/testStepData.npy"))
    npb.setDataArray(np.load("testStepData.npy"))
    stepGen = npb.getStepGen()
    ##stepGen = npb.dataIter doesn't work because we want step.events below
    for nStep, step in enumerate(stepGen):
        print("step %d" % (nStep))
        for nEvt, evt in enumerate(step.events()):
            print("nEvt, evt:", nEvt, evt)

    print("end up with stepIndex:", npb.stepIndex)

    if True:
        print("try running over 1, 3, 2 non-step data with step calls")
        npb.setDataArray(np.load("../data/testNoStepData.npy"))
        stepGen = npb.getStepGen()
        for nStep, step in enumerate(stepGen):
            print("step %d" % (nStep))
            for nEvt, evt in enumerate(step.events()):
                print(nEvt, evt)

    print("try running over 2, 3, 2 non-step data with event call")
    npb.setDataArray(np.load("../data/testStepData.npy"))
    evtGen = npb.myrun.events()
    for nEvt, evt in enumerate(evtGen):
        print(nEvt, evt)

    print("try running over 1, 3, 2 non-step data with event call")
    npb.setDataArray(np.load("../data/testNoStepData.npy"))
    evtGen = npb.myrun.events()
    for nEvt, evt in enumerate(evtGen):
        print(nEvt, evt)
