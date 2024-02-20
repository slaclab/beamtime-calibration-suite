import os
import numpy as np
from calibrationSuite.rixSuiteConfig import experimentHash

if os.getenv('foo') == '1':
    print("psana1")
    from calibrationSuite.psana1Base import *
else:
    print("psana2")
    from calibrationSuite.psana2Base import *

def sortArrayByList(a, data):
    return [x for _,x in sorted(zip(a, data), key=lambda pair:pair[0])]

class BasicSuiteScript(PsanaBase):
    def __init__(self, analysisType='scan'):
        super().__init__()
        print("in BasicSuiteScript, inheriting from PsanaBase, type is psana%d" %(self.psanaType)) 
    
    def setROI(self, roiFile=None, roi=None):
        """Call with both file name and roi to save roi to file and use,
        just name to load,
        just roi to set for current job"""
        if roiFile is not None:
            if roi is None:
                self.ROIfile = roiFile
                self.ROI = np.load(roiFile)
                return
            else:
                np.save(roiFile, roi)
        self.ROI = roi

    def noCommonModeCorrection(self, frame):
        return frame
    
    def regionCommonModeCorrection(self, frame, region, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon
        regionCM = np.median(frame[region][frame[region]<arbitraryCut])
        return frame - regionCM
    
    def rowCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon
        for r in range(self.detRows):
            colOffset = 0
            for b in range(0, 2):
                try:
                    rowCM = np.median(frame[r, colOffset:colOffset + self.detColsPerBank][frame[r, colOffset:colOffset + self.detColsPerBank]<arbitraryCut])
                    frame[r, colOffset:colOffset + self.detColsPerBank] -= rowCM
                except:
                    rowCM = -666
                    print("rowCM problem")
                    print(frame[r, colOffset:colOffset + self.detColsPerBank])
                colOffset += self.detColsPerBank
        return frame
    
    def colCommonModeCorrection(self, frame, arbitraryCut=1000):
        ## this takes a 2d frame
        ## cut keeps photons in common mode - e.g. set to <<1 photon
        for c in range(self.detCols):
            rowOffset = 0
            for b in range(0, self.detNbanksCol):
                try:
                    colCM = np.median(frame[rowOffset:rowOffset + self.detRowsPerBank, c][frame[rowOffset:rowOffset + self.detRowsPerBank, c]<arbitraryCut])
                    frame[rowOffset:rowOffset + self.detRowsPerBank, c] -= colCM
                except:
                    colCM = -666
                    print("colCM problem")
                    print(frame[rowOffset:rowOffset + self.detRowsPerBank], c)
                rowOffset += self.detRowsPerBank
        return frame

    def isBeamEvent(self, evt):
        ec = self.getEventCodes(evt)

        if ec[self.runCode]:
            self.nRunCodeEvents += 1

        if ec[self.daqCode]:
            self.nDaqCodeEvents += 1
            if self.fakeBeamCode:
                return True

        if ec[self.beamCode]:
            self.nBeamCodeEvents += 1
            return True

        return False

    def dumpEventCodeStatistics(self):
        print("have counted %d run triggers, %d DAQ triggers, %d beam events"
              %(self.nRunCodeEvents,
                self.nDaqCodeEvents,
                self.nBeamCodeEvents)
              )

if __name__ == "__main__":
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))