##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import numpy


def dumpvars(prefix, c):
    for key, val in vars(c).items():
        name = prefix + "." + key
        if isinstance(val, int) or isinstance(val, float) or isinstance(val, str) or isinstance(val, list):
            print("{:} {:}".format(name, val))
        elif isinstance(val, numpy.ndarray):
            print("{:}[{:}] {:}".format(name, val.shape, val))
        elif hasattr(val, "value"):
            print("{:} {:}".format(name, val.names[val.value]))
        else:
            try:
                dumpvars(name, val)
            except Exception:
                print("Error dumping {:} {:}".format(name, type(val)))


def dump_seg(seg, cfg):
    print("-- segment {:} --".format(seg))
    dumpvars("config", cfg.config)


def dump_det_config(det, name):
    for config in det._configs:
        if name not in config.__dict__:
            print("Skipping config {:}".format(config.__dict__))
            continue
        scfg = getattr(config, name)
        for seg, segcfg in scfg.items():
            dump_seg(seg, segcfg)
