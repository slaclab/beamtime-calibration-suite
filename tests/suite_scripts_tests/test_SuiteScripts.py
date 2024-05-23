import subprocess
import os
import shutil
import filecmp
import pytest

class  SuiteTester:
    def __init__(self):
        self.isPsanaInstalled = self.psana_installed()
        
        self.setup_commands = "cd ../ && source setup.sh && export OUTPUT_ROOT=. && cd suite_scripts"
        self.expected_outcome_dirs = [
            "../suite_scripts/test_linearity_scan",
        ]

        # Setup: create directories
        for directory in self.expected_outcome_dirs:
            print("making dir: ", directory)
            os.makedirs(directory, exist_ok=True)

    def psana_installed(self):
        try:
            import psana
            return True
        except ImportError:
            return False

    def run_command(self, command):
        result = subprocess.run(command, capture_output=True, text=True)
        return result

    def test_command(self, command, output_location):
        command[2] = self.setup_commands + " && " + command[2]
        result = self.run_command(command)
        print(result.stdout)
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"

        real_output_location = "../suite_scripts/" + output_location
        expected_output_location = "./test_data/" + output_location
        folders_equal = filecmp.dircmp(real_output_location, expected_output_location)

        assert folders_equal.left_only == [], f"Files missing in 'real' folder: {folders_equal.left_only}"
        assert folders_equal.right_only == [], f"Extra files in 'real' folder: {folders_equal.right_only}"
        assert folders_equal.diff_files == [], f"Differences found in files: {folders_equal.diff_files}"

@pytest.fixture(scope="module")
def suite_tester():
    tester = SuiteTester()
    yield tester
    # Teardown: remove directories
    for directory in tester.expected_outcome_dirs:
        shutil.rmtree(directory)

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
def test_LinerarityScans(suite_tester, command, output_location):
    if not suite_tester.isPsanaInstalled:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_location)


@pytest.mark.parametrize("command, output_location", [
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --maxNevents 250 -p /test_noise_1'],
     'test_noise_1'),
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --special noCommonMode,slice --label calib --maxNevents 250 -p /test_noise_2'],
     'test_noise_2'),
    (['bash', '-c', 'python CalcNoiseAndMean.py -r 102 --special regionCommonMode,slice --label common --maxNevents 250 -p /test_noise_3'],
     'test_noise_3'),
])
def test_Noise(suite_tester, command, output_location):
    if not suite_tester.isPsanaInstalled:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_location)


@pytest.mark.parametrize("command, output_location", [
    (['bash', '-c', 'python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_single_photons'],
     'test_single_photons'),
    (['bash', '-c', 'python SimpleClustersParallelSlice.py --special regionCommonMode,FH -r 102 --maxNevents 250 -p /test_single_photons'],
     'test_single_photons'),
    (['bash', '-c', 'python AnalyzeH5.py -r 102 -f ./test_single_photons/SimpleClusters__c0_r102_n1.h5 -p /test_single_photons'],
     'test_single_photons'),
])
def test_SinglePhoton(suite_tester, command, output_location):
    if not suite_tester.isPsanaInstalled:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_location)


@pytest.mark.parametrize("command, output_location", [
    (['bash', '-c', 'python TimeScanParallelSlice.py -r 102 --maxNevents 250 -p /testing_time_scan_parallel_slice_1'],
     'testing_time_scan_parallel_slice_1'),
    (['bash', '-c', 'python MapCompEnOn.py -f /testing_time_scan_parallel_slice_1/TimeScanParallel_c0_r102_n1.h5 -p /testing_time_scan_parallel_slice_1'],
     'testing_time_scan_parallel_slice_1'),
])
def test_TiminingScan(suite_tester, command, output_location):
    if not suite_tester.isPsanaInstalled:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_location)
