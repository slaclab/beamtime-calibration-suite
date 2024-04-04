##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
from calibrationSuite.psanaBase import *
logger = logging.getLogger(__name__)

def setupPsana2(baseObj):

    if baseObj.runRange is None:
        baseObj.ds = baseObj.get_ds(baseObj.run)
    else:
        baseObj.run = baseObj.runRange[0]
        baseObj.ds = baseObj.get_ds()

    baseObj.myrun = next(baseObj.ds.runs())
    try:
        baseObj.step_value = baseObj.myrun.Detector("step_value")
        baseObj.step_docstring = baseObj.myrun.Detector("step_docstring")
    except:
        baseObj.step_value = baseObj.step_docstring = None

    ## baseObj.det = Detector('%s.0:%s.%d' %(baseObj.location, baseObj.detType, baseObj.camera), baseObj.ds.env())
    ## make this less dumb to accomodate epixM etc.
    ## use a dict etc.
    baseObj.det = baseObj.myrun.Detector(baseObj.experimentHash['detectorType'])
    if baseObj.det is None:
        print("no det object for epixhr, what?  Pretend it's ok.")
        ##raise Exception
    ## could set to None and reset with first frame I guess, or does the det object know?

    baseObj.timing = baseObj.myrun.Detector("timing")
    baseObj.desiredCodes = {"120Hz": 272, "4kHz": 273, "5kHz": 274}

    try:
        baseObj.mfxDg1 = baseObj.myrun.Detector("MfxDg1BmMon")
    except:
        baseObj.mfxDg1 = None
        print("No flux source found")  ## if baseObj.verbose?
        logger.exception("No flux source found")
    try:
        baseObj.mfxDg2 = baseObj.myrun.Detector("MfxDg2BmMon")
    except:
        baseObj.mfxDg2 = None
    ## fix hardcoding in the fullness of time
    baseObj.detEvts = 0
    baseObj.flux = None

    baseObj.evrs = None
    try:
        baseObj.wave8 = Detector(baseObj.fluxSource, baseObj.ds.env())
    except:
        baseObj.wave8 = None
    baseObj.config = None
    try:
        baseObj.controlData = Detector("ControlData")
    except:
        baseObj.controlData = None

def getEvtPsana2(baseObj):
    try:
        evt = next(baseObj.myrun.events())
        ## dumb to do the below everywhere, should best not call this method
        ##try:
        ##    baseObj.flux = baseObj._getFlux(evt)
        ##except:
        ##    pass

    except StopIteration:
        return None
    return evt

def getRawDataPsana2(baseObj, evt, gainBitsMasked=True):
    frames = baseObj.det.raw.raw(evt)
    if frames is None:
        return None
    if baseObj.special:
        if 'thirteenBits' in baseObj.special:
            frames = (frames & 0xfffe)
            ##print("13bits")
        elif 'twelveBits' in baseObj.special:
            frames = (frames & 0xfffc)
            ##print("12bits")
        elif 'elevenBits' in baseObj.special:
            frames = (frames & 0xfff8)
            ##print("11bits")
        elif 'tenBits' in baseObj.special:
            frames = (frames & 0xfff0)
            ##print("10bits")
    if gainBitsMasked:
        return frames & baseObj.gainBitsMask
    return frames

