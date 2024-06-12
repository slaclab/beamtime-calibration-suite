import pytest

from calibrationSuite.argumentParser import ArgumentParser


@pytest.fixture
def parser():
    parser = ArgumentParser()
    return parser


# These tests are to make sure the args we need are still options in the argument-parser.

# Now check that some commonly used commands are parsed correctly.


# Check: python CalcNoiseAndMean.py -r 102 --special regionCommonMode,slice --label common --maxNevents 250 -p /test_noise_3
def test_parsing_1(parser):
    args = parser.parse_args(
        [
            "-r",
            "102",
            "--special",
            "regionCommonMode,slice",
            "--label",
            "common",
            "--maxNevents",
            "250",
            "-p",
            "/test_noise_3",
        ]
    )
    assert args.run == 102
    assert args.special == "regionCommonMode,slice"
    assert args.label == "common"
    assert args.maxNevents == 250
    assert args.path == "/test_noise_3"


# Check: python CalcNoiseAndMean.py -r 666 --skipNevents 1000
def test_parsing_2(parser):
    args = parser.parse_args(["-r", "383", "--skipNevents", "1000"])
    assert args.run == 383
    assert args.skipNevents == 1000


# Check: python SimpleClustersParallelSlice.py -r 777 --fakePedestal CalcNoiseAndMean_mean_r666_step0.npy --special regionCommonMode,FH
def test_parsing_3(parser):
    args = parser.parse_args(
        [
            "-r",
            "777",
            "--fakePedestal",
            "CalcNoiseAndMean_mean_r666_step0.npy",
            "--special",
            "regionCommonMode",
        ]
    )
    assert args.run == 777
    assert args.fakePedestalFile == "CalcNoiseAndMean_mean_r666_step0.npy"
    assert args.special == "regionCommonMode"


# Check: python SimpleClustersParallelSlice.py -r 777 -f ../lowFlux/SimpleClustersParallel_c0_r777_n1.h5 -L cm
def test_parsing_4(parser):
    args = parser.parse_args(
        [
            "-r",
            "777",
            "-f",
            "../lowFlux/SimpleClustersParallel_c0_r777_n1.h5",
            "-L",
            "cm",
        ]
    )
    assert args.run == 777
    assert args.files == "../lowFlux/SimpleClustersParallel_c0_r777_n1.h5"
    assert args.label == "cm"


# Check: python SimpleClustersParallelSlice.py -r 224 -f ../lowFlux/SimpleClusters_c0_r224_n100.h5
def test_parsing_5(parser):
    args = parser.parse_args(
        ["-r", "224", "-f", "../lowFlux/SimpleClusters_c0_r224_n100.h5"]
    )
    assert args.run == 224
    assert args.files == "../lowFlux/SimpleClusters_c0_r224_n100.h5"
    assert args.label is None
