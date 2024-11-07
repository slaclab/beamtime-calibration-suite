import filecmp
import os
import shutil
import subprocess

import pytest

# diffing .pngs is a bit tricky without PIL
from PIL import Image, ImageChops

"""
This file tests the following commands:
(based on script usage described here: https://confluence.slac.stanford.edu/display/LCLSDET/Feb+2024+beamtime+analysis+instructions)

python CalcNoiseAndMean.py -r 102 --maxNevents 250 -p /test_noise_1
python CalcNoiseAndMean.py -r 102 --special noCommonMode,slice --label calib --maxNevents 250 -p /test_noise_2
python CalcNoiseAndMean.py -r 102 --special regionCommonMode,slice --label common --maxNevents 250 -p /test_noise_3

python TimeScanParallelSlice.py -r 102 --maxNevents 250 -p /test_time_scan_parallel_slice

python LinearityPlotsParallelSlice.py -r 102 --maxNevents 250 -p /test_linearity_scan'
python LinearityPlotsParallelSlice.py -r 102 --maxNevents 250 -p /test_linearity_scan -f test_linearity_scan/LinearityPlotsParallel__c0_r102_n1.h5 --label fooBar
python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_linearity_scan --special slice

python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_simple_photon
python SimpleClustersParallelSlice.py --special regionCommonMode,FH -r 102 --maxNevents 250 -p /test_simple_photon


python EventScanParallelSlice.py -r 120 --maxNevents 250 -p /test_event_scan_parallel_slice
python EventScanParallelSlice.py -r 120 -f ../suite_scripts/test_event_scan_parallel_slice/EventScanParallel_c0_r120__n1.h5 --maxNevents 120 -p /test_event_scan_parallel_slice

python findMinSwitchValue.py -r 102 --maxNevents 6 -d Epix10ka -p /test_find_min_switch_value

python roiFromSwitched.py -r 102 -c 1 -t 40000 --detObj calib -d Epix10ka --maxNevents 250 -p /test_roi
python roiFromSwitched.py -r 102 -c 1 -t 40000 --detObj calib -d Epix10ka --maxNevents 250 -p /test_roi


## these tests are disabled atm, the cmnds dont work fully ...
python searchForNonSwitching.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_search_for_non_switching

python histogramFluxEtc.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_histogram_flux_etc

python persistenceCheck.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_persistence_check

python persistenceCheckParallel.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_persistence_check
"""


"""
How these tests work:

To verify the scripts, we execute the scripts as we would during a beamtime.
The chosen run-numbers are chosen as runs where the data can be accessed with no issues.

We verify the result files of the script by diffing them against golden-values in the tests/test_data dir.
This dir is a git submodule found here: https://github.com/slaclab/beamtime-calibration-suite-test-data

To setup the submodule (only need to do if running this test-file), from the projet root run:
 git submodule init
 git submodule update

And you can optionally undo this (if no longer using tests and want to free up space) with:
 git submodule deinit tests/test_data

More test data can be added to the tests/test_data submodule by doing 'cd tests/test_data',
then copying the new data into the folder, and then commiting the data as usual into git.
Git will save the data to the submodule's repo if you are inside the 'test_data' dir when executing the commands.
Then 'cd' back outside the 'test_data' dir and 'git add test_data', to have the main-repo track the new submodule commit. 


Adding New Tests:

You can copy an existing test-case (ex: test_FindMinSwitchValue),
and change the test-case name and parametirized arguments (the part with '@pytest.mark.parametrize...')
Each paramtirized argument contains a tuple of the cmd the be tested, and then the cmds output folder. 

You also need to add the cmds output folder name to the 'expected_outcome_dirs' array in the SuiteTester class,
so the output folder can be created and later deleted at end of the test.
"""


class SuiteTester:
    def __init__(self):
        # annoyingly complicated way to get root of current git repo,
        # do this so test can be run from tests/ dir or root of project
        self.git_repo_root = (
            subprocess.Popen(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE)
            .communicate()[0]
            .rstrip()
            .decode("utf-8")
        )

        # avoid any weirdness and make sure curr-dir is that of tested scripts
        os.chdir(self.git_repo_root + "/suite_scripts")

        # tests can only run if the following are true (skip if not):
        # 1) pasna library is avaliable (i.e running on S3DF)
        # 2) tests/test-data submodule is installed
        self.canTestsRun = self.can_tests_run()

        suite_scripts_root = self.git_repo_root + "/suite_scripts/"
        tests_root = self.git_repo_root + "/tests/"

        # setup environment and then move to suite_scripts dir so we can run scripts
        self.setup_commands = (
            "export PYTHONPATH=$PYTHONPATH:"
            + self.git_repo_root
            + " && export OUTPUT_ROOT="
            + suite_scripts_root
            + " && export SUITE_CONFIG="
            + tests_root
            + "testingSuiteConfig.py"
            + " && cd "
            + suite_scripts_root
        )

        # we need to mkdir these, so scipts we test can output to them
        self.expected_outcome_dirs = [
            "test_linearity_scan",
            "test_noise_1",
            "test_noise_2",
            "test_noise_3",
            "test_simple_photon",
            "test_time_scan_parallel_slice",
            "test_event_scan_parallel_slice",
            "test_find_min_switch_value",
            "test_histogram_flux_etc",
            "test_roi",
            "test_search_for_non_switching",
            "test_analyze_h5",
        ]

        # lets have the 'real output' folders just be in /suite_scripts
        for i in range(len(self.expected_outcome_dirs)):
            self.expected_outcome_dirs[i] = self.git_repo_root + "/suite_scripts/" + self.expected_outcome_dirs[i]

        for dir in self.expected_outcome_dirs:
            os.makedirs(dir, exist_ok=True)

    # we skip tests if they can't be ran, so remaining tests can still go (such as locally or in github-actions)
    def can_tests_run(self):
        try:
            import psana  # noqa: F401
        except ImportError:
            return False
        return True

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
        if result.returncode != 0:
            assert False, f"Script failed with error: {result.stderr}"

        # let's not diff output files if user doesn't have download the /tests/test_data submodule,
        # since the exact output of scripts can often change a small amount so diffing the output files
        # is mainly useful when refactoring or when sure output data won't change.
        # testing without diffing output will still test if scripts can run to completion without error!
        data_path = self.git_repo_root + "/tests/test_data"
        if not os.path.exists(data_path) or not os.path.exists(data_path + "/test_roi"):
            print("/tests/test_data submodule not setup, not diffing output against expected output files")
            return

        real_output_location = self.git_repo_root + "/suite_scripts/" + output_location
        expected_output_location = self.git_repo_root + "/tests/test_data/" + output_location

        # diff real output vs expected output files
        for root, dirs, files in os.walk(real_output_location):
            for file in files:
                real_file_path = real_output_location + "/" + file
                expected_file_path = expected_output_location + "/" + file

                # Check if files are PNGs
                if real_file_path.endswith(".png") and expected_file_path.endswith(".png"):
                    if self.are_images_same(real_file_path, expected_file_path) == 0:
                        assert False, f"PNG files {real_file_path} and {expected_file_path} are different"
                else:
                    # For non-PNG files, perform directory comparison
                    if filecmp.cmp(real_file_path, expected_file_path) == 0:
                        assert False, f"files {real_file_path} and {expected_file_path} are different"


@pytest.fixture(scope="module")
def suite_tester():
    tester = SuiteTester()
    yield tester

    '''
    # teardown
    # can re-enable if everyone's home dirs are getting too filled up, but not deleting avoids confusion on how to find real output files.
    for dir in tester.expected_outcome_dirs:
        # the folders won't exist if passing b/c of missing dependencies
        if os.path.exists(dir):
            shutil.rmtree(dir)
    '''


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python CalcNoiseAndMean.py -r 102 --special testRun --maxNevents 250 -p /test_noise_1",
            ],
            "test_noise_1",
        ),
        (
            [
                "bash",
                "-c",
                "python CalcNoiseAndMean.py -r 102 --special noCommonMode,slice,testRun --label calib --maxNevents 250 -p /test_noise_2",
            ],
            "test_noise_2",
        ),
        (
            [
                "bash",
                "-c",
                "python CalcNoiseAndMean.py -r 102 --special regionCommonMode,slice,testRun --label common --maxNevents 250 -p /test_noise_3",
            ],
            "test_noise_3",
        ),
    ],
)
def test_Noise(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


# this is an example of testing for an expected failure, only one case like this atm.
@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        # for this script we expect run 102 to fail assert, the run has issues returning step_values
        # and should fail-out because of this.
        (
            [
                "bash",
                "-c",
                "python TimeScanParallelSlice.py -r 102 --maxNevents 250 -p /test_time_scan_parallel_slice",
            ],
            "test_time_scan_parallel_slice",
        ),
    ],
)
def test_TimingScanExpectedFail(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")

    with pytest.raises(AssertionError):  # PASS if the script fails assert, FAIL if not
        suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        # for this script we expect run 102 to fail, the run has issues returning step_values
        # (['bash', '-c', 'python TimeScanParallelSlice.py -r 102 --maxNevents 250 -p /test_time_scan_parallel_slice'],
        # 'test_time_scan_parallel_slice'),
        (
            [
                "bash",
                "-c",
                "python TimeScanParallelSlice.py -r 82 --maxNevents 250 -p /test_time_scan_parallel_slice",
            ],
            "test_time_scan_parallel_slice",
        ),
    ],
)
def test_TimingScan(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_simple_photon",
            ],
            "test_simple_photon",
        ),
        (
            [
                "bash",
                "-c",
                "python SimpleClustersParallelSlice.py --special regionCommonMode,FH -r 102 --maxNevents 250 -p /test_simple_photon",
            ],
            "test_simple_photon",
        ),
    ],
)
def test_SimplePhoton(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python LinearityPlotsParallelSlice.py -r 102 --maxNevents 250 -p /test_linearity_scan",
            ],
            "test_linearity_scan",
        ),
        (
            [
                "bash",
                "-c",
                # this cmd runs pretty long, so we use '--special testing' and '-maxNevents 2' to stop pixel-analysis early
                "python LinearityPlotsParallelSlice.py -r 102 --special testing --maxNevents 2 -p /test_linearity_scan -f test_linearity_scan/LinearityPlotsParallel__c0_r102_n1.h5 --label fooBar",
            ],
            "test_linearity_scan",
        ),
        (
            [
                "bash",
                "-c",
                "python simplePhotonCounter.py -r 102 --maxNevents 250 -p /test_linearity_scan --special slice",
            ],
            "test_linearity_scan",
        ),
    ],
)
def test_LinearityScans(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python EventScanParallelSlice.py -r 120 --maxNevents 250 -p /test_event_scan_parallel_slice",
            ],
            "test_event_scan_parallel_slice",
        ),
        (
            [
                "bash",
                "-c",
                "python EventScanParallelSlice.py -r 120 -f ../suite_scripts/test_event_scan_parallel_slice/EventScanParallel_c0_r120__n666.h5 --maxNevents 120 -p /test_event_scan_parallel_slice",
            ],
            "test_event_scan_parallel_slice",
        ),
    ],
)
def test_EventScans(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python findMinSwitchValue.py -r 102 --maxNevents 6 -d Epix10ka -p /test_find_min_switch_value",
            ],
            "test_find_min_switch_value",
        ),
    ],
)
def test_FindMinSwitchValue(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python roiFromSwitched.py -r 102 -c 1 -t 40000 --detObj calib -d Epix10ka --maxNevents 250 -p /test_roi",
            ],
            "test_roi",
        ),
        (
            [
                "bash",
                "-c",
                "python roiFromThreshold.py -r 102 -c 1 -t 40000 --detObj calib -d Epix10ka --maxNevents 250 -p /test_roi",
            ],
            "test_roi",
        ),
    ],
)
def test_RoiFromSwitched(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python searchForNonSwitching.py -r 102 --special testing --maxNevents 250 -p /test_search_for_non_switching | grep gain > test_search_for_non_switching/out.txt",
            ],
            "test_roi",
        ),
    ],
)
def test_SearchNonSwitching(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "python histogramFluxEtc.py -r 102 --maxNevents 250 -p /test_histogram_flux_etc",
            ],
            "test_histogram_flux_etc",
        ),
    ],
)
def test_HistogramFlux(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


# this test uses input data from sdf filepath (available on s3df),
# and we remove r102_custers.npy from the correctness comparison b/c this file is around 10gb!
@pytest.mark.parametrize(
    "command, output_dir_name",
    [
        (
            [
                "bash",
                "-c",
                "time python AnalyzeH5.py -r 102 -f /sdf/data/lcls/ds/rix/rixx1005922/results/lowFlux/SimpleClusters_testData_c0_r47_n666.h5 -p ./test_analyze_h5 --special testRun && rm ./test_analyze_h5/r102_clusters.npy",
            ],
            "test_analyze_h5",
        ),
    ],
)
def test_Analyze_h5(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)


# non-working commands...
"""
@pytest.mark.parametrize("command, output_dir_name", [
    (['bash', '-c', 'python persistenceCheck.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_persistence_check'],
     'test_persistence_check'),
    (['bash', '-c', 'python persistenceChceckParallel.py -r 102 -d Epix10ka2M --maxNevents 250 -p /test_persistence_check],
     'test_persistence_check'),
])
def test_PersistenceCheck(suite_tester, command, output_dir_name):
    if not suite_tester.canTestsRun:
        pytest.skip("Can only test with psana library on S3DF!")
    suite_tester.test_command(command, output_dir_name)
"""
