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
import logging
logger = logging.getLogger(__name__)

def setupPsana1(baseObj):

    if baseObj.runRange is None:
        baseObj.ds = baseObj.get_ds(baseObj.run)
    else:
        baseObj.run = baseObj.runRange[0]
        baseObj.ds = baseObj.get_ds()

    baseObj.det = Detector("%s.0:%s.%d" % (baseObj.location, baseObj.detType, baseObj.camera), baseObj.ds.env())
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

def getFluxPsana1(baseObj, evt):
    try:
        fluxes = baseObj.wave8.get(evt).peakA()
        if fluxes is None:
            print("No flux found")  ## if baseObj.verbose?
            logger.error("No flux found")
            return None
        f = fluxes[baseObj.fluxChannels].mean() * baseObj.fluxSign
        try:
            if f < baseObj.fluxCut:
                return None
        except:
            pass
    except:
        return None
    return f

def isKickedPsana1(baseObj, evt):
    try:
        evr = evt.get(EvrData.DataV4, baseObj.evrs[0])
    except:
        baseObj.get_evrs()
        evr = evt.get(EvrData.DataV4, baseObj.evrs[0])

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

def getEvtPsana1(baseObj, run=None):
    oldDs = baseObj.ds
    if run is not None:
        baseObj.ds = baseObj.get_ds(run)
    try:  ## or just yield evt I think
        evt = next(baseObj.ds.events())
    except StopIteration:
        baseObj.ds = oldDs
        return None
    baseObj.ds = oldDs
    return evt

def getRawDataPsana1(baseObj, evt, gainBitsMasked=True):
    frames = baseObj.det.raw(evt)
    if frames is None:
        return None
    if gainBitsMasked:
        return frames & 0x3FFF
    return frames
