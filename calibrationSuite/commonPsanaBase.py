import os
import sys
import logging
import importlib.util
from psana import *
from calibrationSuite.argumentParser import ArgumentParser
## standard
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

logger = logging.getLogger(__name__)

class CommonPsanaBase(object):
    def __init__(self, analysisType="scan"):
        print("in commonPsanaBase")
        logger.info("in commonPsanaBase")

        commandUsed = sys.executable + " " + " ".join(sys.argv)
        logger.info("Ran with cmd: " + commandUsed)

        self.gainModes = {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        self.ePix10k_cameraTypes = {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"}
        self.g0cut = 1 << 14  ## 2023
        self.gainBitsMask = self.g0cut - 1

        self.args = ArgumentParser().parse_args()
        logger.info("parsed cmdline args: " + str(self.args))

        # if the SUITE_CONFIG env var is set use that, otherwise if the cmd line arg is set use that
        # if neither are set, use the default 'suiteConfig.py' file
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
        knownTypes = ['epixhr', 'epixM', 'rixsCCD']
        if self.experimentHash['detectorType'] not in knownTypes:
            print ("type %s not in known types" %(self.experimentHash['detectorType']), knownTypes)
            return -1
        
    def importConfigFile(self, file_path):
        if not os.path.exists(file_path):
            print(f"The file '{file_path}' does not exist")
            return None
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module
    
    def get_config(self):
        self.config = self.ds.env().configStore() 

    def getImage(self, evt, data=None):
        return self.raw.image(evt, data)
    
    def getFivePedestalRunInfo(self):
        ## could do load_txt but would require full path so
        if self.det is None:
            self.setupPsana()

        evt = self.getEvt(self.fivePedestalRun)
        self.fpGains = self.det.gain(evt)
        self.fpPedestals = self.det.pedestals(evt)
        self.fpStatus = self.det.status(evt)  ## does this work?
        self.fpRMS = self.det.rms(evt)  ## does this work?