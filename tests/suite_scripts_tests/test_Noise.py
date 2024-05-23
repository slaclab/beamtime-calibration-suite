import os
import shutil
import subprocess
import filecmp
import pytest

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_directories():
    expected_directories = [
        '../suite_scripts/test_noise_1',
        '../suite_scripts/test_noise_2',
        '../suite_scripts/test_noise_3',
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

def psana_installed():
    try:
        import psana
        return True
    except ImportError:
        return False
    
def run_command(command):
    print("cmd: ", command)
    result = subprocess.run(command, capture_output=True, text=True)
    return result

@pytest.mark.skipif(not psana_installed(), reason="Can only test with psana library on S3DF!")
@pytest.mark.parametrize("command, output_location", [
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --maxNevents 250 -p /test_noise_1'],
     'test_noise_1'),
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --special noCommonMode,slice --label calib --maxNevents 250 -p /test_noise_2'],
     'test_noise_2'),
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --special regionCommonMode,slice --label common --maxNevents 250 -p /test_noise_3'],
     'test_noise_3'),
])
def test_calculation(command, output_location):
    try:
        import psana
    except ImportError:
        pass

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
