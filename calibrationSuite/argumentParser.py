import argparse

class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Configures calibration suite, overriding experimentHash',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.parser.add_argument('-e', '--exp', help='experiment name')
        self.parser.add_argument('-l', '--location', help='hutch location, e.g. MfxEndstation or DetLab')
        self.parser.add_argument('-r', '--run', type=int, help='run number')
        self.parser.add_argument('-R', '--runRange', help='run range, format ...')
        self.parser.add_argument('--fivePedestalRun', type=int, help='5 pedestal run')
        self.parser.add_argument('--fakePedestal', type=str, help='fake pedestal file')
        self.parser.add_argument('-c', '--camera', type=int, help='camera.n')
        self.parser.add_argument('-p', '--path', type=str, help='the base path to the output directory')
        self.parser.add_argument('-n', '--nModules', type=int, help='nModules')
        self.parser.add_argument('-d', '--detType', type=str, default='', help='Epix100, Epix10ka, Epix10kaQuad, Epix10ka2M, ...')
        self.parser.add_argument('--maxNevents', type=int, default='666666', help='max number of events to analyze, also prevents mpi hanging')
        self.parser.add_argument('--skipNevents', type=int, default=0, help='max number of events to skip at the start of each step')
        self.parser.add_argument('--configScript', type=str, default='experimentSuiteConfig.py', help='name of python config file to load if any')
        self.parser.add_argument('--detObj', help='"raw", "calib", "image"')
        self.parser.add_argument('-f','--file', type=str, help='run analysis only on file')
        self.parser.add_argument('-L','--label', type=str, help='analysis label')
        self.parser.add_argument('-t', '--threshold', help="threshold (ADU or keV or wave8) depending on --detObj")
        self.parser.add_argument('--fluxCut', type=float, help="minimum flux to be included in analysis")
        self.parser.add_argument('--special', type=str, help='comma-separated list of special behaviors - maybe this is too lazy.  E.g. positiveParity,doKazEvents,...')

    def parse_args(self):
        return self.parser.parse_args()