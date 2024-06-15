##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import argparse


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Configures calibration suite, overriding experimentHash",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.parser.add_argument("-e", "--exp", help="experiment")
        self.parser.add_argument("-l", "--location", help="hutch location, e.g. MfxEndstation or DetLab")
        self.parser.add_argument("-r", "--run", type=int, help="run")
        self.parser.add_argument("-R", "--runRange", help="run range, format ...")
        self.parser.add_argument("--fivePedestalRun", type=int, help="5 pedestal run")
        self.parser.add_argument("--fakePedestalFile", type=str, help="fake pedestal file")
        self.parser.add_argument("--g0PedFile", type=str, help="g0 pedestal file")
        self.parser.add_argument("--g1PedFile", type=str, help="g1 pedestal file")
        self.parser.add_argument("--g0GainFile", type=str, help="g0 gain file")
        self.parser.add_argument("--g1GainFile", type=str, help="g1 gain file")
        self.parser.add_argument("--offsetFile", type=str, help="offset file for stitching")
        self.parser.add_argument("-c", "--camera", type=int, help="camera.n")
        self.parser.add_argument("-p", "--path", type=str, help="the base path to the output directory")
        self.parser.add_argument("-n", "--nModules", type=int, help="nModules")
        self.parser.add_argument(
            "--mode", type=str, help="detector mode (1d, 2d, ...?"
        )  ## might be discoverable otherwise
        self.parser.add_argument(
            "-d", "--detType", type=str, default="", help="Epix100, Epix10ka, Epix10kaQuad, Epix10ka2M, ..."
        )
        self.parser.add_argument("--maxNevents", type=int, default="666666", help="max number of events to analyze")
        self.parser.add_argument(
            "--skipNevents", type=int, default=0, help="max number of events to skip at the start of each step"
        )
        self.parser.add_argument(
            "--configScript",
            type=str,
            default="experimentSuiteConfig.py",
            help="name of python config file to load if any",
        )
        self.parser.add_argument("--detObj", help='"raw", "calib", "image"')
        self.parser.add_argument(
            "-f", "--files", type=str, default=None, help="run analysis on file or comma-separated files"
        )
        self.parser.add_argument("-cf", "--configFile", type=str, help="config file path, can be relative or full path")
        self.parser.add_argument("-L", "--label", type=str, help="analysis label")
        self.parser.add_argument("-t", "--threshold", help="threshold (ADU or keV or wave8) depending on --detObj")
        self.parser.add_argument("--fluxCutMin", type=float, help="minimum flux to be included in analysis")
        self.parser.add_argument("--fluxCutMax", type=float, help="maximum flux to be included in analysis")
        self.parser.add_argument("--seedCut", help="seed cut for clustering")
        self.parser.add_argument(
            "--special",
            type=str,
            help="comma-separated list of special behaviors - maybe this is too lazy.  E.g. positiveParity,doKazEvents,...",
        )

    def parse_args(self, testing_args=None):
        if testing_args is None:
            return self.parser.parse_args()
        else:
            return self.parser.parse_args(testing_args)
