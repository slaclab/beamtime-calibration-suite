from calibrationSuite.basicSuiteScript import *
from calibrationSuite.Stats import *


class CalcNoise(BasicSuiteScript):
    def __init__(self):
        super().__init__("dark")  ##self)


if __name__ == "__main__":
    cn = CalcNoise()
    print("have built a", cn.className, "class")

    cn.setupPsana()
    if cn.special is not None and "skip281" in cn.special:
        skip281 = True
    else:
        skip281 = False

    stepGen = cn.getStepGen()
    ##    for nstep, step in enumerate (cn.ds.steps()):
    for nstep, step in enumerate(stepGen):
        statsArray = [None for i in cn.singlePixels]
        for nevt, evt in enumerate(step.events()):
            frames = None
            if nevt < cn.skipNevents:
                print(nevt, cn.skipNevents)
                continue
            if evt is None:
                continue
            ec = cn.getEventCodes(evt)
            beamEvent = cn.isBeamEvent(evt)
            ##if ec[281] or skip281:
            if beamEvent or skip281:
                if cn.special is not None and "CommonMode" in cn.special:
                    frames = cn.getCalibData(evt)
                    if frames is None:
                        continue
                    if "noCommonMode" in cn.special:
                        frames = cn.noCommonModeCorrection(frames[0])
                    elif "rowCommonMode" in cn.special:
                        frames = cn.rowCommonModeCorrection(frames[0], 2.0)
                    elif "colCommonMode" in cn.special:
                        frames = cn.colCommonModeCorrection(frames[0], 2.0)
                    elif "regionCommonMode" in cn.special:
                        frames = cn.regionCommonModeCorrection(frames[0], cn.regionSlice, 2.0)
                else:
                    frames = cn.getRawData(evt, gainBitsMasked=True)
                    if cn.special is not None and "parity" in cn.special:
                        if cn.getPingPongParity(frames[0][144:224, 0:80]) == ("negative" in cn.special):
                            continue
                    try:
                        frames = frames[0]
                    except:
                        if frames is None:
                            ##print("None frames")
                            continue

                        print("empty non-None frames")
                        continue
            else:
                ##print(ec)
                continue
            if frames is None:
                print("no frame")
                continue
            for i, p in enumerate(cn.singlePixels):
                try:
                    statsArray[i].accumulate(np.double(frames), frames[p[1], p[2]])
                except:
                    statsArray[i] = Stats(frames.shape)
                    statsArray[i].accumulate(np.double(frames), frames[p[1], p[2]])
        stats = statsArray[2]  ## only matters for cross-correlation
        noise = stats.rms()
        means = stats.mean()
        if cn.special is not None and "slice" in cn.special:
            noise = noise[cn.regionSlice]
            print("mean, median noise:", noise.mean(), np.median(noise))
            means = means[cn.regionSlice]
        else:
            pass
        np.save("%s/CalcNoiseAndMean_rms_r%d_step%s.npy" % (cn.outputDir, cn.run, nstep), noise)
        np.save("%s/CalcNoiseAndMean_mean_r%d_step%s.npy" % (cn.outputDir, cn.run, nstep), means)
        for i, p in enumerate(cn.singlePixels):
            try:
                np.save(
                    "%s/CalcNoiseAndMean_correlation_pixel_%d_%d_%s_r%d_step%s.npy"
                    % (cn.outputDir, p[1], p[2], cn.label, cn.run, nstep),
                    statsArray[i].corr(statsArray[i].mean()[p[1], p[2]], statsArray[i].rms()[p[1], p[2]])[
                        cn.regionSlice
                    ],
                )
            except:
                ## probably rms = 0.
                continue

    cn.dumpEventCodeStatistics()
