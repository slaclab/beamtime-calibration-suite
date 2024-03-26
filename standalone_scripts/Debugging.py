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

file_path = "../scan/TimeScanParallel_c0_r496_n1.h5"  # Replace with the actual file path

with h5py.File(file_path, "r") as file:
    # Print the first few lines of the HDF5 file
    print("File Information:")
    print(f"File Path: {file_path}")
    print(f"File Keys: {list(file.keys())}")  # Print the keys/groups in the root of the file

    # Print information from specific groups and datasets
    group_name = "your_group"  # Replace with the actual group name
    if group_name in file:
        print(f"\nGroup Information ({group_name}):")
        group = file[group_name]

        # Print keys/datasets within the group
        print(f"Group Keys: {list(group.keys())}")

        # Print information from specific datasets within the group
        dataset_name = "your_dataset"  # Replace with the actual dataset name
        if dataset_name in group:
            dataset = group[dataset_name]
            print(f"\nDataset Information ({dataset_name}):")
            print(f"Shape: {dataset.shape}")
            print(f"Dtype: {dataset.dtype}")

            # Print a subset of the dataset (adjust the indices accordingly)
            print("\nSubset of the Dataset:")
            print(dataset[:10])  # Print the first 10 elements, adjust as needed
        else:
            print(f"Dataset '{dataset_name}' not found in the group.")
    else:
        print(f"Group '{group_name}' not found in the HDF5 file.")