from calibrationSuite.detectorInfo import DetectorInfo


def test_epixhr_setup():
    detector = DetectorInfo('epixhr')

    assert detector.detectorType == 'epixhr'
    assert detector.g0cut == 1 << 14
    assert detector.nRows == 288
    assert detector.nCols == 284
    assert detector.nColsPerBank == 96
    assert detector.nBanksRow == int(detector.nCols / detector.nColsPerBank)
    assert detector.nBanksCol == 2
    assert detector.nRowsPerBank == 144
    assert detector.preferredCommonMode == 'regionCommonMode'
    assert detector.clusterShape == [3,3]
    assert detector.seedCut == 4
    assert detector.neighborCut == 0.5

def test_epixm_setup():
    detector = DetectorInfo('epixm')

    assert detector.detectorType == 'epixm'
    assert detector.g0cut == 1 << 15
    assert detector.nModules == 4
    assert detector.nRows == 192
    assert detector.nBanksRow == 4
    assert detector.nRowsPerBank == int(detector.nRows / detector.nBanksRow)
    assert detector.nCols == 384
    assert detector.nBanksCol == 6
    assert detector.nColsPerBank ==  int(detector.nCols / detector.nBanksCol)
    assert detector.preferredCommonMode == 'rowCommonMode'
    assert detector.clusterShape == [3, 3]
    assert detector.gainMode is None
    assert detector.negativeGain is True
    assert detector.aduPerKeV == 666
    assert detector.seedCut == 2
    assert detector.neighborCut == 0.25

def test_archon_setup():
    detector = DetectorInfo('archon')

    assert detector.detectorType == 'archon'
    assert detector.nTestPixelsPerBank == 36
    assert detector.nBanks == 16
    assert detector.nCols == 4800 - detector.nBanks * detector.nTestPixelsPerBank
    assert detector.nRows == 1
    assert detector.preferredCommonMode == 'rixsCCDTestPixelSubtraction'
    assert detector.clusterShape == [1, 5]