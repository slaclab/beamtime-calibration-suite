from calibrationSuite.basicSuiteScript import *

class SimplePhotonCounter(BasicSuiteScript):
    def __init__(self):
        super().__init__(analysisType='lowFlux')
        
if __name__ == "__main__":
    spc = SimplePhotonCounter()
    spc.setupPsana()

    nGoodEvents = 0
    thresholded = None
    while True:
        evt = spc.getEvt()
        if evt is None:
            break
        if not spc.isBeamEvent(evt):
            continue
        
        gain = None
        if spc.special is not None and 'fakePedestal' in spc.special:
            if 'FH' in spc.special:
                gain = 20 ##17.## my guess
            elif 'FM' in spc.special:
                gain = 6.66 #20/3
            else:
                raise Exception
            print('using gain correction', gain)

            frames = rawFrames.astype('float') - spc.fakePedestalFrame
            frames /= gain ## this helps with the bit shift
            spc.photonCut = 6.
        else:
            frames = spc.getCalibData(evt)
            spc.photonCut = 6#.*2 ## keV
            ## *2 because of bit shift

        if frames is None:
            ##print("No contrib found")
            continue
        try:
            thresholded += (frames>spc.photonCut)*1.
        except:
            thresholded = (frames>spc.photonCut)*1.
        
        nGoodEvents += 1
        if nGoodEvents%100 == 0:
            print("n good events analyzed: %d" %(nGoodEvents))

        if nGoodEvents > spc.maxNevents:
            break
    if spc.special is not None and 'slice' in spc.special:
        thresholded = thresholded[0][spc.regionSlice]
        
    np.save("%s/%s_r%d_c%d_%s.npy" %(spc.outputDir, spc.className, spc.run, spc.camera, spc.exp), thresholded/nGoodEvents)
    print("likelihood of a photon or photons per pixel using cut %0.2f is %0.3f"
          %(spc.photonCut, (thresholded/nGoodEvents).mean()))
    print("total photons in detector using cut %0.2f is %0.3f"
          %(spc.photonCut, (thresholded).sum()))

    spc.dumpEventCodeStatistics()
    
    
