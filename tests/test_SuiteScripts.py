import subprocess
import os
import shutil
import filecmp
import pytest
import subprocess
from PIL import Image, ImageChops

class SuiteTester:
    def __init__(self):
        self.isPsanaInstalled = self.psana_installed()

        # annoyingly complicated way to get root of current git repo
        git_repo_root = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8') 
        self.setup_commands = ("export PYTHONPATH=$PYTHONPATH:" + git_repo_root + " && export OUTPUT_ROOT=. && "
        "export SUITE_CONFIG=" + git_repo_root + "/tests/testingSuiteConfig.py" + " && cd ../suite_scripts")
        
        self.expected_outcome_dirs = [
            git_repo_root + "/suite_scripts/test_linearity_scan",
            git_repo_root + "/suite_scripts/test_noise_1",
            git_repo_root + "/suite_scripts/test_noise_2",
            git_repo_root + "/suite_scripts/test_noise_3",
            git_repo_root + "/suite_scripts/test_single_photon",
            git_repo_root + "/suite_scripts/test_time_scan_parallel_slice",
        ]

        for dir in self.expected_outcome_dirs:
            print (dir)
            os.makedirs(dir, exist_ok=True)
        exit(1)
    
    def psana_installed(self):
        try:
            import psana
            return True
        except ImportError:
            return False

    def run_command(self, command):
        result = subprocess.run(command, capture_output=True, text=True)
        return result

    def are_images_same(self, img1_path, img2_path):
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        diff = ImageChops.difference(img1, img2)
        if diff.getbbox():
            return False
        else:
            return True

    def test_command(self, command, output_location):
        command[2] = self.setup_commands + " && " + command[2]
        result = self.run_command(command)
        print(result.stdout)
        print (command[2])
        #exit(1)
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"

        real_output_location = "../suite_scripts/" + output_location
        expected_output_location = "./test_data/" + output_location
        
        # Compare files in directories
        for root, dirs, files in os.walk(real_output_location):
            for file in files:
                real_file_path = real_output_location + "/" + file
                expected_file_path = expected_output_location + "/" + file

                print("real: ", real_file_path)
                print("expected: ", expected_file_path)
                # Check if files are PNGs
                if real_file_path.endswith('.png') and expected_file_path.endswith('.png'):
                    assert self.are_images_same(real_file_path, expected_file_path), f"PNG files {real_file_path} and {expected_file_path} are different"
                else:
                    # For non-PNG files, perform directory comparison
                    assert filecmp.cmp(real_file_path, expected_file_path), f"files {real_file_path} and {expected_file_path} are different"


@pytest.fixture(scope="module")
def suite_tester():
    tester = SuiteTester()
    yield tester
    
    # teardown
    for dir in tester.expected_outcome_dirs:
        shutil.rmtree(dir)

'''
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

'''
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

'''
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
    (['bash', '-c', 'python TimeScanParallelSlice.py -r 102 --maxNevents 250 -p /test_time_scan_parallel_slice'],
     'test_time_scan_parallel_slice'),
    (['bash', '-c', 'python MapCompEnOn.py -f /testing_time_scan_parallel_slice_1/TimeScanParallel_c0_r102_n1.h5 -p /test_time_scan_parallel_slice'],
     'test_time_scan_parallel_slice'),
])
def test_TiminingScan(suite_tester, command, output_location):
    if not suite_tester.isPsanaInstalled:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_location)
'''
