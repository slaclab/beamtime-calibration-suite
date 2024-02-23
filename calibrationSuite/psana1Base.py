from psana import *
from PSCalib.NDArrIO import load_txt

class PsanaBase(object):
    def __init__(self, analysisType='scan'):
        self.psanaType = 1
        print("in psana1Base")
        self.gainModes = {"FH":0, "FM":1, "FL":2, "AHL-H":3, "AML-M":4, "AHL-L":5, "AML-L":6}
        self.ePix10k_cameraTypes = {1:"Epix10ka", 4:"Epix10kaQuad", 16:"Epix10ka2M"}
        self.g0cut = 1<<14
        self.gainBitsMask = self.g0cut - 1

##        self.setupPsana()

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
        except Exception as e:
            self.wave8 = None
        self.config = None
        try:
            self.controlData = Detector('ControlData')
        except Exception as e:
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
            except Exception as e:
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
            except Exception as e:
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
            except Exception as e:
                pass
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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

