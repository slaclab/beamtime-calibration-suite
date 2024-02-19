import matplotlib.pyplot as plt
import h5py

file_name = '../scan/TimeScanParallel_c0_r286_n1.h5'  # Update with your file name

with h5py.File(file_name, 'r') as file:
    dataset = file['dataset_name']  # Replace 'dataset_name' with the actual dataset name
    data = dataset[:]  # Load the dataset into a NumPy array


# Assuming 'data' is a 2D image
plt.imshow(data, cmap='viridis')  # Adjust cmap and other parameters as needed
plt.colorbar()
plt.show()
    
