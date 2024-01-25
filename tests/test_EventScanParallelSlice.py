import subprocess
import os
import shutil

def test_run_event_scan_parallel_slice_and_compare():
    
    # Delete existing 'scan' directory if it exists and make new one
    if os.path.exists('scan'):
        shutil.rmtree('scan')
    os.makedirs('scan')

    # run scripts
    result1 = subprocess.run(["python", "../scripts/EventScanParallelSlice.py", "-r", "349", "-p", "scan"])
    result2 = subprocess.run(["python", "../scripts/EventScanParallelSlice.py", "-r", "349", "-f", "scan/EventScanParallel_c0_r349_n1.h5"])

    #print(result1.stdout)
    #print(result1.stderr)
    #print(result2.stdout)
    #print(result2.stderr)

    assert subprocess.call(["diff", "-r", "scan", "testData/expected/eventScanParallelSliceExpected/"]) != 0