from library.basicSuiteScript import *
import Stats

class CalcNoise(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
            
if __name__ == "__main__":
    cn = CalcNoise()
    print("have built a", cn.className, "class")

    cn.setupPsana()

    stepGen = cn.getStepGen()
##    for nstep, step in enumerate (cn.ds.steps()):
    for nstep, step in enumerate (stepGen):
        stats = None
        for nevt, evt in enumerate(step.events()):
            if evt is None:
                continue
            ec = cn.getEventCodes(evt)
            if ec[281]:
                frames = cn.getRawData(evt, gainBitsMasked=True)
            else:
                continue
            if frames is None:
                ##print("no frame")
                continue
            try:
                stats.accumulate(np.double(frames), frames[0, 13, 66])
            except:
                stats = Stats.Stats(frames.shape)
                stats.accumulate(np.double(frames), frames[0, 13, 66])
                
        np.save("CalcNoise_r%d_step%s.npy" %(cn.run, nstep), stats.rms())
