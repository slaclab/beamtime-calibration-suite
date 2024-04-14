##############################################################################
## This file is part of 'SLAC Beamtime Calibration Suite'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'SLAC Beamtime Calibration Suite', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################
import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks, peak_prominences
from scipy.signal import savgol_filter
import sys
import os
import math

if len(sys.argv) != 3 or sys.argv[1] != "-f":
    print("Usage: python MapCompEnOn.py -f filename")
    sys.exit(1)

file_name = sys.argv[2]

base_filename = os.path.splitext(os.path.basename(file_name))[0]

# Open the HDF5 file
with h5py.File(file_name, "r") as file:
    # Define the name of the group containing the datasets
    group_name = "slice"  # Change this to the actual group name
    dataset_names = list(file[group_name].keys())

    # Create an empty list to store all the datasets
    all_datasets = []

    # Loop through all the datasets in the group and stack them into a 3D array
    for dataset_name in dataset_names:
        dataset = file[group_name][dataset_name]
        data = dataset[...]
        all_datasets.append(data)

    # Stack all the datasets to create a 3-dimensional array
    combined_data = np.stack(all_datasets, axis=0)

# Access and plot a specific slice from the combined data (e.g., the first slice)
slice_to_display = combined_data[2, :, :]
# plt.imshow(slice_to_display, cmap='viridis')  # Adjust the colormap as needed
# plt.colorbar()  # Add a colorbar for reference
# plt.show()


timeVec = [float(x) * 1 for x in dataset_names]


rowsNum = combined_data.shape[1]
colsNum = combined_data.shape[2]


X1 = np.zeros((rowsNum, colsNum))
Y1 = np.zeros((rowsNum, colsNum))
X2 = np.zeros((rowsNum, colsNum))
Y2 = np.zeros((rowsNum, colsNum))
X3 = np.zeros((rowsNum, colsNum))
Y3 = np.zeros((rowsNum, colsNum))

Xinterp = np.linspace(min(timeVec), max(timeVec), 5000)

AvAll = np.mean(combined_data, axis=(1, 2))

# for ir in range(0,rowsNum):
#    for ic in range(0,colsNum):
minir = 0
maxir = rowsNum
minic = 0
maxic = colsNum
for ir in range(minir, maxir):
    for ic in range(minic, maxic):
        # print('row :',ir)
        # print('col :',ic)

        # for ir in range(10,11):
        #    for ic in range(30,31):
        timelineToDisplay = combined_data[:, ir, ic]
        f = interp1d(timeVec, timelineToDisplay, kind="linear")
        y_new = f(Xinterp)
        y_new_2ndpart = f(Xinterp[Xinterp > (np.mean(timeVec))])
        thediff = np.diff(y_new)
        thediff_2ndpart = np.diff(y_new_2ndpart)
        window_size = 150
        polynomial_order = 1

        # Apply Savitzky-Golay filtering
        smoothed_data = savgol_filter(thediff, window_size, polynomial_order)
        differencialfiltered = np.array(smoothed_data)

        smoothed_data_2ndpart = savgol_filter(thediff_2ndpart, window_size, polynomial_order)
        differencialfiltered_2ndpart = np.array(smoothed_data_2ndpart)
        X = Xinterp[0:-1]
        Y = smoothed_data
        X1[ir, ic] = Xinterp[np.argmax(smoothed_data)]
        Y1[ir, ic] = y_new[np.argmax(smoothed_data)]
        X2[ir, ic] = Xinterp[np.argmin(smoothed_data)]
        Y2[ir, ic] = y_new[np.argmin(smoothed_data)]
        X3[ir, ic] = min(X[Y == min(Y[len(Y) // 2 : -1])])
        Y3[ir, ic] = y_new_2ndpart[np.argmin(smoothed_data[(len(smoothed_data) // 2) : -1])]

        if False:
            plt.subplot(3, 1, 1)
            plt.plot(Xinterp, y_new, "k")
            plt.plot(Xinterp[np.argmin(smoothed_data)], y_new[np.argmin(smoothed_data)], "r*")
            plt.plot(Xinterp[np.argmax(smoothed_data)], y_new[np.argmax(smoothed_data)], "b*")
            plt.plot(
                min(X[Y == min(Y[len(Y) // 2 : -1])]),
                y_new_2ndpart[np.argmin(smoothed_data[(len(smoothed_data) // 2) : -1])],
                "y*",
            )

            plt.subplot(3, 1, 2)
            plt.hist(y_new, 100)
            plt.subplot(3, 1, 3)

            plt.plot(thediff, "b.")
            plt.plot(smoothed_data, "r")
            plt.show()

#        print(X1[ir,ic])
#        print(X2[ir,ic])
#        print(X3[ir,ic])
#        print(Y1[ir,ic])
#        print(Y2[ir,ic])
#        print(Y3[ir,ic])
#        print('%%%%%%%%%%%%%%%%%%%%%%')

fig = plt.figure()
# fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(4, 12))  # Adjust figsize as needed
plt.suptitle("Click on figure to see the timeline of a pixel", fontsize=12)
plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
plt.subplot(3, 1, 1)
# plt.imshow(X3,vmin=X3.min(),vmax=X3.max())
plt.imshow(X3, vmin=(np.mean(X3) - 1 * (np.std(X3))), vmax=(np.mean(X3) + 1 * (np.std(X3))))
plt.title("Onset transfer function")
plt.colorbar()
# plt.tight_layout()

plt.subplot(3, 1, 2)
plt.imshow(X2, vmin=X2.min(), vmax=X2.max())
plt.imshow(X2, vmin=(np.mean(X2) - 1 * (np.std(X2))), vmax=(np.mean(X2) + 1 * (np.std(X2))))
plt.title("Onset CompEnOn")
plt.colorbar()
# plt.tight_layout()

plt.subplot(3, 1, 3)
# plt.imshow(X3[minir:maxir,minic:maxic]-X1[minir:maxir,minic:maxic])
X4 = X3 - X1
# plt.imshow(X3-X1,vmin=(X3-X1).min(),vmax=(X3-X1).max())
plt.imshow(X4, vmin=(np.mean(X4) - 1 * (np.std(X4))), vmax=(np.mean(X4) + 1 * (np.std(X4))))
plt.title("Length transfer function")
plt.colorbar()
# plt.tight_layout()

# fig = plt.figure()
# plt.imshow(X2,vmin=X2.min(),vmax=X2.max())
# plt.imshow(X2,vmin=(np.mean(X2)-1*(np.std(X2))),vmax=(np.mean(X2)+1*(np.std(X2))))
# plt.title('Onset CompEnOn')
# plt.colorbar()
# plt.tight_layout()


# Save the plotted image to a PNG file with the filename
save_path = "/sdf/data/lcls/ds/rix/rixx1003721/results/scan/{}_plot.png".format(base_filename)
plt.savefig(save_path)


def onclick(event):
    ix, iy = event.xdata, event.ydata
    colsel = math.trunc(ix)
    rowsel = math.trunc(iy)
    # print(f'x = {ix}, y = {iy}')

    timelineToDisplay = combined_data[:, rowsel, colsel]
    f = interp1d(timeVec, timelineToDisplay, kind="linear")
    y_new = f(Xinterp)
    y_new_2ndpart = f(Xinterp[Xinterp > (np.mean(timeVec))])
    thediff = np.diff(y_new)
    thediff_2ndpart = np.diff(y_new_2ndpart)
    window_size = 150
    polynomial_order = 1

    # Apply Savitzky-Golay filtering
    smoothed_data = savgol_filter(thediff, window_size, polynomial_order)
    differencialfiltered = np.array(smoothed_data)

    smoothed_data_2ndpart = savgol_filter(thediff_2ndpart, window_size, polynomial_order)
    differencialfiltered_2ndpart = np.array(smoothed_data_2ndpart)
    X = Xinterp[0:-1]
    Y = smoothed_data
    X1[ir, ic] = Xinterp[np.argmax(smoothed_data)]
    Y1[ir, ic] = y_new[np.argmax(smoothed_data)]
    X2[ir, ic] = Xinterp[np.argmin(smoothed_data)]
    Y2[ir, ic] = y_new[np.argmin(smoothed_data)]
    X3[ir, ic] = min(X[Y == min(Y[len(Y) // 2 : -1])])
    Y3[ir, ic] = y_new_2ndpart[np.argmin(smoothed_data[(len(smoothed_data) // 2) : -1])]
    #    plt.figure(10)
    #    plt.close(10)
    #    plt.subplots_adjust(left=0.2, bottom=0.2, right=1.0, top=1.0)
    plt.figure(10)
    plt.ion()
    plt.clf()
    plt.show(block=False)
    plt.plot(Xinterp, y_new, "k")
    plt.plot(Xinterp[np.argmin(smoothed_data)], y_new[np.argmin(smoothed_data)], "r*")
    plt.plot(Xinterp[np.argmax(smoothed_data)], y_new[np.argmax(smoothed_data)], "b*")
    plt.plot(
        min(X[Y == min(Y[len(Y) // 2 : -1])]),
        y_new_2ndpart[np.argmin(smoothed_data[(len(smoothed_data) // 2) : -1])],
        "y*",
    )
    plt.title(f"Pixel:{colsel},{rowsel}")
    plt.show()
    # print('Do you get there????')


cid = fig.canvas.mpl_connect("button_press_event", onclick)


plt.show()
