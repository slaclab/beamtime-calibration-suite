import os
import shutil
import subprocess
import filecmp
import pytest

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_directories():
    expected_directories = [
        '../suite_scripts/test_linearity_scan',
    ]

    # Setup: create directories
    for directory in expected_directories:
        print("making dir: ", directory)
        os.makedirs(directory, exist_ok=True)

    #yield

    # Teardown: remove directories
    #for directory in expected_directories:
        #shutil.rmtree(directory)


setup_commands = "cd ../ && source setup.sh && export OUTPUT_ROOT=. && cd suite_scripts"

def run_command(command):
    print("cmd: ", command)
    result = subprocess.run(command, capture_output=True, text=True)
    return result

@pytest.mark.parametrize("command, output_location", [
    (['bash', '-c', 'python LinearityPlotsParallelSlice.py -r 102 --maxNevents 250 -p /test_linearity_scan'],
     'test_linearity_scan'),
    (['bash', '-c', 'python LinearityPlotsParallelSlice.py -r 102 --maxNevents 250 -p /test_linearity_scan -f test_linearity_scan/LinearityPlotsParallel__c0_r102_n1.h5 --label fooBar'],
     'test_linearity_scan'),
    (['bash', '-c', 'python analyze_npy.py test_linearity_scan/LinearityPlotsParallel_r102_sliceFits_fooBar_raw.npy'],
     'test_linearity_scan'),
    (['bash', '-c', 'python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_linearity_scan --special slice'],
     'test_linearity_scan'),
])
def test_calculation(command, output_location):

    command[2] = setup_commands + " && " + command[2]
    result = run_command(command)
    print(result.stdout)
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

    real_output_location = "../suite_scripts/" + output_location
    expected_output_location = "./test_data/" + output_location
    folders_equal = filecmp.dircmp(real_output_location, expected_output_location)
    
    assert folders_equal.left_only == [], f"Files missing in 'real' folder: {folders_equal.left_only}"
    assert folders_equal.right_only == [], f"Extra files in 'real' folder: {folders_equal.right_only}"
    assert folders_equal.diff_files == [], f"Differences found in files: {folders_equal.diff_files}"
