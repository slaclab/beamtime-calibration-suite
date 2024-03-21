import subprocess
import time
import os
import shutil
import sys
import logging
import calibrationSuite.loggingSetup as ls
# for logging from current file        print ("Hello")

logger = logging.getLogger(__name__)
# log to file named <curr script name>.log
currFileName = os.path.basename(__file__)
ls.setupScriptLogging("../logs/test_SuiteScripts.log", logging.INFO) # change to logging.INFO for full logging output

def setup_test_dirs():
    test_dirs = ["../test_1", "../test_2", "../test_3"]
    for dir in test_dirs:
        if os.path.exists(dir):
            print( "removing dir: " + dir + " for clean test")
            logger.info ("removing dir: " + dir + " for clean test")
            shutil.rmtree(dir)
        os.makedirs(dir)

def run_command_with_time(cmd):
    start_time = time.time()
    print ("running command: " + cmd)
    logger.info (f"running command: '{cmd}'")

    env = os.environ.copy() # Create a copy of the current environment
    env["PYTHONPATH"] = f"../:{env.get('PYTHONPATH', '')}"
    env["SUITE_CONFIG"] = "../suite_scripts/rixSuiteConfig.py"
    env["OUTPUT_ROOT"] = ""

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    
    stdout, stderr = process.communicate()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print (f"command: '{cmd}' took {execution_time:.2f} seconds")

    logger.info (f"command: '{cmd}' took {execution_time:.2f} seconds")
    logger.info ("Stdout: " + stdout)
    logger.info ("Stderr: " + stderr)
    
    if process.returncode != 0:
        print ("failed with exit code " + str(process.returncode))
        logger.info ("failed with exit code " + str(process.returncode))

def test_calc_noise_and_mean():
    print ("testing CalcNoiseAndMean.py ...")
    cmd = "python ../suite_scripts/CalcNoiseAndMean.py -r 583 -p ../test_1" 
    run_command_with_time(cmd)

def test_linearity_plots_parallel_slice():
    print ("testing LinearityPlotsParallelSlice.py ...")
    cmd1 = "python ../suite_scripts/LinearityPlotsParallelSlice.py -r 591 -p ../test_2"
    cmd2 = "python ../suite_scripts/LinearityPlotsParallelSlice.py -r 591 -f ../test_2/LinearityPlotsParallel__c0_r591_n1.h5 --label fooBar -p ../test_2"
    run_command_with_time(cmd1)
    run_command_with_time(cmd2)

def test_analyze_npy():
    print ("testing analyze_npy.py ...")
    cmd = "python ../suite_scripts/analyze_npy.py ../test_2/LinearityPlotsParallel_r591_sliceFits_fooBar_raw.npy"
    run_command_with_time(cmd)

def test_time_scan_parallel_slice():
    print ("testing TimeScanParallelSlice.py ...")
    cmd1 = "python ../suite_scripts/TimeScanParallelSlice.py -r 498 -t 100 -p ../test_3"
    cmd2 = "python ../suite_scripts/TimeScanParallelSlice.py -r 498 --threshold 0 -p ../test_3"
    run_command_with_time(cmd1)
    run_command_with_time(cmd2)

def test_map_comp_en_on():
    print ("testing MapCompEnOn.py ...")
    cmd = "python ../standalone_scripts/MapCompEnOn.py -f ../test_3/TimeScanParallel__c0_r498_n1.h5"
    run_command_with_time(cmd)

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "-c":
        setup_test_dirs()
    test_calc_noise_and_mean()
    test_linearity_plots_parallel_slice()
    test_analyze_npy()
    test_time_scan_parallel_slice()
    test_map_comp_en_on()

if __name__ == "__main__":
    main()