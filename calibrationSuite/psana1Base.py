from psana import *
from PSCalib.NDArrIO import load_txt
from calibrationSuite.argumentParser import ArgumentParser
from calibrationSuite.rixSuiteConfig import experimentHash

class PsanaBase(object):
    def __init__(self, analysisType='scan'):
        self.psanaType = 1
        print("in psana1Base")
        self.gainModes = {"FH":0, "FM":1, "FL":2, "AHL-H":3, "AML-M":4, "AHL-L":5, "AML-L":6}
        self.ePix10k_cameraTypes = {1:"Epix10ka", 4:"Epix10kaQuad", 16:"Epix10ka2M"}
        self.g0cut = 1<<14
        self.gainBitsMask = self.g0cut - 1

        self.camera = 0
        ##self.outputDir = '/sdf/data/lcls/ds/rix/rixx1003721/results/%s/' %(analysisType)
        self.outputDir = '../%s/' %(analysisType)
        ##self.outputDir = '/tmp'

        self.className = self.__class__.__name__

        try:
            self.location = experimentHash['location']
        except:
            pass
        try:
            self.exp = experimentHash['exp']
        except:
            pass
        try:
        ##if True:
            self.ROIfileNames = experimentHash['ROIs']
            self.ROIs = []
            for f in self.ROIfileNames:
                self.ROIs.append(np.load(f+'.npy'))
            try:  ## dumb code for compatibility or expectation
                self.ROI = self.ROIs[0]
            except:
                pass
        ##if False:
        except:
            print("had trouble finding", self.ROIfileNames)
            self.ROI = None
            self.ROIs = None
        try:
            self.singlePixels = experimentHash['singlePixels']
        except:
            self.singlePixels = None
        try:
            self.regionSlice = experimentHash['regionSlice']
        except:
            self.regionSlice = None
        if self.regionSlice is not None:
            self.sliceCoordinates = [[self.regionSlice[0].start,
                                      self.regionSlice[0].stop],
                                     [self.regionSlice[1].start,
                                      self.regionSlice[1].stop],
                                     ]
            sc = self.sliceCoordinates
            self.sliceEdges = [sc[0][1]-sc[0][0], sc[1][1]-sc[1][0]]

        try:
            self.fluxSource = experimentHash['fluxSource']
            try:
                self.fluxChannels = experimentHash['fluxChannels']
            except:
                self.fluxChannels = range(8,16) ## wave8
            try:
                self.fluxSign = experimentHash['fluxSign']
            except:
                self.fluxSign = 1
        except:
            self.fluxSource = None

        ## for non-120 Hz running
        self.nRunCodeEvents = 0
        self.nDaqCodeEvents = 0
        self.nBeamCodeEvents = 0
        self.runCode = 280
        self.daqCode = 281
        self.beamCode = 283 ## per Matt
        ##self.beamCode = 281 ## don't see 283...
        self.fakeBeamCode = False

        # Parse command-line arguments
        args_parser = ArgumentParser()
        args = args_parser.parse_args()

        # Handle cmdline arguments
        self.file = args.file
        self.label = args.label or ""

        # Run number
        self.run = args.run if args.run is not None else None
        self.camera = args.camera if args.camera is not None else self.camera
        # Experiment name
        self.exp = args.exp if args.exp is not None else self.exp
        self.location = args.location if args.location is not None else self.location
        self.maxNevents = args.maxNevents if args.maxNevents is not None else None
        self.skipNevents = args.skipNevents if args.skipNevents is not None else None
        self.outputDir = args.path if args.path is not None else self.outputDir
        self.detObj = args.detObj
        self.threshold = eval(args.threshold) if args.threshold is not None else None
        self.fluxCut = args.fluxCut if args.fluxCut is not None else None
        try:
            self.runRange = eval(args.runRange)  ## in case needed
        except Exception as e:
            print(f"An exception occurred: {e}")
            self.runRange = None
        self.fivePedestalRun = args.fivePedestalRun if args.fivePedestalRun is not None else None
        self.fakePedestal = args.fakePedestal if args.fakePedestal is not None else None
        self.fakePedestalFrame = np.load(self.fakePedestal) if self.fakePedestal is not None else None
        if args.detType == '':
            ## assume epix10k for now
            if args.nModules is not None:
                self.detType = self.ePix10k_cameraTypes[args.nModules]
        else:
            self.detType = args.detType
        self.special = args.special
        self.ds = None
        self.det = None ## do we need multiple dets in an array? or self.secondDet?
        # Done handling cmdline arguments

        ## self.setupPsana()

    def get_ds(self, run=None):
        if run is None:
            run = self.run
        return DataSource('exp=%s:run=%d:smd' %(self.exp, run))


    def setupPsana(self):
        ##print("have built basic script class, exp %s run %d" %(self.exp, self.run))
        if self.runRange is None:
            self.ds = self.get_ds(self.run)
        else:
            self.run = self.runRange[0]
            self.ds = self.get_ds()
            
        self.det = Detector('%s.0:%s.%d' %(self.location, self.detType, self.camera), self.ds.env())
        self.evrs = None
        try:
            self.wave8 = Detector(self.fluxSource, self.ds.env())
        except:
            self.wave8 = None
        self.config = None
        try:
            self.controlData = Detector('ControlData')
        except:
            self.controlData = None
            
    def getFivePedestalRunInfo(self):
        ## could do load_txt but would require full path so
        if self.det is None:
            self.setupPsana()

        evt = self.getEvt(self.fivePedestalRun)
        self.fpGains = self.det.gain(evt)
        self.fpPedestals = self.det.pedestals(evt)
        self.fpStatus = self.det.status(evt)## does this work?
        self.fpRMS = self.det.rms(evt)## does this work?
        
    def getEvt(self, run=None):
        oldDs = self.ds
        if run is not None:
            self.ds = self.get_ds(run)
        try:## or just yield evt I think
            evt = next(self.ds.events())
        except StopIteration:
            self.ds = oldDs
            return None
        self.ds = oldDs
        return evt


    def getEvtFromRunsTooSmartForMyOwnGood(self):
        for r in self.runRange:
            self.run = r
            self.ds = self.get_ds()
            try:
                evt = next(self.ds.events())
                yield evt
            except:
                continue

    def getEvtFromRuns(self):
        try:## can't get yield to work
            evt = next(self.ds.events())
            return(evt)
        except StopIteration:
            i = self.runRange.index(self.run)
            try:
                self.run = self.runRange[i+1]
                print("switching to run %d" %(self.run))
                self.ds = self.get_ds(self.run)
            except:
                print("have run out of new runs")
                return None
            ##print("get event from new run")
            evt = next(self.ds.events())
            return evt
        
    def getFlux(self, evt):
        try:
            fluxes = self.wave8.get(evt).peakA()
            if fluxes is None:
                print("No flux found")## if self.verbose?
                return None
            f = fluxes[self.fluxChannels].mean()*self.fluxSign
            try:
                if f<self.fluxCut:
                    return None
            except:
                pass
        except:
            return None
        return f

    def get_evrs(self):
        if self.config is None:
            self.get_config()

        self.evrs = []
        for key in list(self.config.keys()):
            if key.type() == EvrData.ConfigV7:
                self.evrs.append(key.src())

    def isKicked(self, evt):
        try:
            evr = evt.get(EvrData.DataV4, self.evrs[0])
        except:
            self.get_evrs()
            evr = evt.get(EvrData.DataV4, self.evrs[0])

##        kicked = False
##        try:
##            for ec in evr.fifoEvents():
##                if ec.eventCode() == 162:
##                    return True
        kicked = True
        try:
            for ec in evr.fifoEvents():
                if ec.eventCode() == 137:
                    kicked = False
        except:
            pass
        return kicked

    def get_config(self):
        self.config = self.ds.env().configStore()

    def getStepGen(self):
        return self.ds.steps()

    def getScanValue(self, foo):
        return self.controlData().pvControls()[0].value()

    def getRawData(self, evt, gainBitsMasked=True):
        frames = self.det.raw(evt)
        if frames is None:
            return None
        if gainBitsMasked:
            return frames&0x3fff
        return frames

    def getCalibData(self, evt):
        return self.det.calib(evt)

    def getImage(evt, data=None):
        return self.raw.image(evt, data)
    
    
if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))

