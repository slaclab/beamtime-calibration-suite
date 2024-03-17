##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import matplotlib.pyplot as plt
import h5py

file_name = "../scan/TimeScanParallel_c0_r286_n1.h5"  # Update with your file name

with h5py.File(file_name, "r") as file:
    dataset = file["dataset_name"]  # Replace 'dataset_name' with the actual dataset name
    data = dataset[:]  # Load the dataset into a NumPy array


# Assuming 'data' is a 2D image
plt.imshow(data, cmap="viridis")  # Adjust cmap and other parameters as needed
plt.colorbar()
plt.show()
