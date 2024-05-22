import os
import subprocess
import filecmp
import pytest

def run_command(command):
    print("cmd: ", command)
    result = subprocess.run(command, capture_output=True, text=True)
    return result

@pytest.mark.parametrize("command, real_output_location, expected_output_location", [
    (['bash', '-c', 'cd ../ && source setup.sh && cd suite_scripts  && python CalcNoiseAndMean.py -r 102'],
     '../suite_scripts/dark',
     './test_data/calc_noise_mean_no_common'),
    (['bash', '-c', 'cd ../ && source setup.sh && cd suite_scripts  && python CalcNoiseAndMean.py -r 102'],
     '../suite_scripts/dark',
     './test_data/calc_noise_mean_no_common'),
])
def test_calculation(command, real_output_location, expected_output_location):
    result = run_command(command)
    #print(result.stdout)
    assert result.returncode == 0, f"Script failed with error: {result.stderr.decode()}"

    folders_equal = filecmp.dircmp(real_output_location, expected_output_location)
    assert folders_equal.left_only == [], f"Files missing in 'real' folder: {folders_equal.left_only}"
    assert folders_equal.right_only == [], f"Extra files in 'real' folder: {folders_equal.right_only}"
    assert folders_equal.diff_files == [], f"Differences found in files: {folders_equal.diff_files}"
