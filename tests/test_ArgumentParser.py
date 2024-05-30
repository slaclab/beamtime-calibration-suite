import pytest
from calibrationSuite.argumentParser import ArgumentParser


@pytest.fixture
def parser():
    parser = ArgumentParser()
    return parser


# For now, just check that some commonly used commands are parsed correctly.


# Check: python CalcNoiseAndMean.py -r 383 --special noCommonMode,slice --label calib
def test_parsing_1(parser):
    args = parser.parse_args(["-r", "383", "--special", "noCommonMode,slice", "--label", "calib"])
    assert args.run == 383
    assert args.special == "noCommonMode,slice"
    assert args.label == "calib"


# Check: python CalcNoiseAndMean.py -r 666 --skipNevents 1000
def test_parsing_2(parser):
    args = parser.parse_args(["-r", "383", "--skipNevents", "1000"])
    assert args.run == 383
    assert args.skipNevents == 1000


# Check: python SimpleClustersParallelSlice.py -r 777 --fakePedestal CalcNoiseAndMean_mean_r666_step0.npy --special regionCommonMode,FH
def test_parsing_3(parser):
    args = parser.parse_args(
        ["-r", "777", "--fakePedestal", "CalcNoiseAndMean_mean_r666_step0.npy", "--special", "regionCommonMode"]
    )
    assert args.run == 777
    assert args.fakePedestalFile == "CalcNoiseAndMean_mean_r666_step0.npy"
    assert args.special == "regionCommonMode"


# Check: python SimpleClustersParallelSlice.py -r 777 -f ../lowFlux/SimpleClustersParallel_c0_r777_n1.h5 -L cm
def test_parsing_4(parser):
    args = parser.parse_args(["-r", "777", "-f", "../lowFlux/SimpleClustersParallel_c0_r777_n1.h5", "-L", "cm"])
    assert args.run == 777
    assert args.files == "../lowFlux/SimpleClustersParallel_c0_r777_n1.h5"
    assert args.label == "cm"


# Check: python SimpleClustersParallelSlice.py -r 224 -f ../lowFlux/SimpleClusters_c0_r224_n100.h5
def test_parsing_5(parser):
    args = parser.parse_args(["-r", "224", "-f", "../lowFlux/SimpleClusters_c0_r224_n100.h5"])
    assert args.run == 224
    assert args.files == "../lowFlux/SimpleClusters_c0_r224_n100.h5"
    assert args.label is None
