from scipy.stats import poisson
import matplotlib.pyplot as plt
import sys
import numpy as np

samples = 1000
transmissions = [1,0.0001,0.8,0.0002,0.61,0.0005,0.4,0.0007,0.2,0.001,0.5,0.1,0.0015,0.05,0.002,0.02,0.005,0.01,0.007]
photonEnergy = 9.8
spectrum = []

photonRateAtLowestTransmission = eval(sys.argv[1])
minTransmission = min(transmissions)

for t in transmissions:
    n = samples * t
    poissonDistEnergy =  poisson.rvs(photonRateAtLowestTransmission * t/minTransmission, size=samples)*photonEnergy
    spectrum += list(poissonDistEnergy)

spectrum = np.array(spectrum)
clipEnergy = spectrum[spectrum>0].mean()*5

plt.hist(spectrum[spectrum>0].clip(0, clipEnergy), 100)
plt.title(r'spectrum: $\gamma$ rate %0.4f at %0.4f transmission and $\gamma$ energy %0.1f' %(photonRateAtLowestTransmission, minTransmission, photonEnergy))
plt.xlabel("keV")
plt.show()
