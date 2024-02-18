##import psana
from library.basicSuiteScript import *
import sys
import numpy as np

class FPS(BasicSuiteScript):
    def __init__(self):
        super().__init__()##self)
        print("in", sys.argv[0])

    def foo(self):
        print("foo")
        print("%d" %(self.run))

if __name__ == "__main__":
    fps = FPS()
    print("have built an FPS")
    fps.foo()
    fps.getFivePedestalRunInfo()
    ped = fps.fpPedestals
    print(ped[fps.gainModes['FH']].mean())
    print(ped[fps.gainModes['FH']].shape)
    print(ped[fps.gainModes['FM']])
    ## get mean of -r run data set here for some forced low run sya
    ## compare to fps.gainModes['FL']
    print(fps.run)
