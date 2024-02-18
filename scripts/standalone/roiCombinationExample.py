import numpy as np
import copy

a = np.load("roiFromSwitched_e550_rmfxx1005021.npy")
b = copy.copy(a)*0
b[0, 150:250, 150:250] = 1
c = np.bitwise_and(a, b)
np.save("maskedRoiFromSwitched_e550_rmfxx1005021.npy", c)

