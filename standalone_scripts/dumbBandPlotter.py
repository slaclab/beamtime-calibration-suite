import matplotlib.pyplot as plt
import numpy as np
import sys

dataFile = sys.argv[1]
row = eval(sys.argv[2])
col = eval(sys.argv[3])

a = np.load(dataFile)
plt.plot(np.arange(a.shape[0]), a[:, row, col], ".", ms=1)
plt.xlabel("event")
plt.ylabel("Raw")
title = "pixel %d,%d in %s" % (row, col, dataFile)
plt.title(title)
plt.savefig(title.replace(" ", "_") + ".png")
