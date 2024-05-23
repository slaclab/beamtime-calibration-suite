import os
import shutil
import subprocess
import filecmp
import pytest
import suiteScriptTestsHelpers


expected_outcome_dirs = [
    "../suite_scripts/test_linearity_scan",

]
 # Setup: create directories
for directory in expected_outcome_dirs:
    print("making dir: ", directory)
    os.makedirs(directory, exist_ok=True)

    #yield

    # Teardown: remove directories
    #for directory in expected_directories:
        #shutil.rmtree(directory)

@pytest.mark.skipif(not psana_installed(), reason="Can only test with psana library on S3DF!")
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
    try:
        import psana
    except ImportError:
        pass

