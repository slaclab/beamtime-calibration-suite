from calibrationSuite.basicSuiteScript import *
from calibrationSuite.Stats import *
import calibrationSuite.loggingSetup as ls

# for logging from current file
logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging("../logs/" + currFileName[:-3] + ".log", logging.INFO)  # change to logging.INFO for full logging output


class CalcNoise(BasicSuiteScript):
    def __init__(self):
        super().__init__("dark")


if __name__ == "__main__":
    cn = CalcNoise()
    print("have built a " + cn.className + "class")
    logger.info("have built a " + cn.className + "class")

    cn.setupPsana()
    if cn.special is not None and "skip281" in cn.special:
        skip281 = True
    else:
        skip281 = False

    stepGen = cn.getStepGen()
    ##for nstep, step in enumerate (cn.ds.steps()):
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
                    commonModeCut = 2.0## keV, calib
                    if cn.detObj and cn.detObj == 'raw':
                        frames = cn.getRawData(evt).astype('float')
                        commonModeCut = 16384
                    else:
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
                        frames = cn.regionCommonModeCorrection(frames[0], cn.regionSlice, commonModeCut)
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
                        logger.info("empty non-None frames")
                        continue
            else:
                ##print(ec)
                continue
            if frames is None:
                print("no frame")
                logger.info("no frame")
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
            print("mean, median noise:" + str(noise.mean()) + str(np.median(noise)))
            logger.info("mean, median noise:" + str(noise.mean()) + str(np.median(noise)))
            means = means[cn.regionSlice]
        else:
            pass

        meanRmsFileName = "%s/CalcNoiseAndMean_%s_rms_r%d_step%s.npy" % (cn.outputDir, cn.label, cn.run, nstep)
        np.save(meanRmsFileName, noise)
        meanFileName = "%s/CalcNoiseAndMean_mean_%s_r%d_step%s.npy" % (cn.outputDir, cn.label, cn.run, nstep)
        np.save(meanFileName, means)
        logger.info("Wrote file: " + meanRmsFileName)
        logger.info("Wrote file: " + meanFileName)

        for i, p in enumerate(cn.singlePixels):
            try:
                meanCorrelationFileName = "%s/CalcNoiseAndMean_correlation_pixel_%d_%d_%s_r%d_step%s.npy" % (cn.outputDir, p[1], p[2], cn.label, cn.run, nstep),
                np.save(meanCorrelationFileName, statsArray[i].corr(statsArray[i].mean()[p[1], p[2]], statsArray[i].rms()[p[1], p[2]])[cn.regionSlice],)
                logging.info("Wrote file: " + meanCorrelationFileName)
            except:
                ## probably rms = 0.
                continue

    cn.dumpEventCodeStatistics()