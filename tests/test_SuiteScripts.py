import os
import subprocess
import filecmp

def test_calculation():
    # Run the script with the specified command
    #result = subprocess.run(['python', '../suite_scripts/CalcNoiseAndMean.py', '-r', '102'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.run(['bash', '-c', 'cd ../ && source setup.sh && cd suite_scripts  && python CalcNoiseAndMean.py -r 102'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   
    print(result.stdout)
    # Check if the script ran successfully
    assert result.returncode == 0, f"Script failed with error: {result.stderr.decode()}"

    # Define the paths to the 'dark' and 'expected' folders
    dark_folder = '../suite_scripts/dark'
    expected_folder = './test_data/calc_noise_mean_no_common'
    
    # Compare the contents of the 'dark' folder with the 'expected' folder
    folders_equal = filecmp.dircmp(dark_folder, expected_folder)

    # Check if the folders are identical
    assert folders_equal.left_only == [], f"Files missing in 'dark' folder: {folders_equal.left_only}"
    assert folders_equal.right_only == [], f"Extra files in 'dark' folder: {folders_equal.right_only}"
    assert folders_equal.diff_files == [], f"Differences found in files: {folders_equal.diff_files}"
