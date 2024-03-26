#!/bin/bash

# print cmds executed
set -x

cd ..
source setup.sh
cd suite_scripts
export OUTPUT_ROOT=

# create directories if they don't exist
mkdir -p test_1
mkdir -p test_2
mkdir -p test_3

# replace the following with commands for upcoming beamtime
python CalcNoiseAndMean.py -r 583 -p ../test_1
python LinearityPlotsParallelSlice.py -r 591 -p ../test_2
python LinearityPlotsParallelSlice.py -r 591 -f ../test_2/LinearityPlotsParallel__c0_r591_n1.h5 --label fooBar -p ../test_2
python analyze_npy.py ../test_2/LinearityPlotsParallel_r591_sliceFits_fooBar_raw.npy
python TimeScanParallelSlice.py -r 498 -t 100 -p ../test_3
python TimeScanParallelSlice.py -r 498 --threshold 0 -p ../test_3
python MapCompEnOn.py -f ../test_3/TimeScanParallel__c0_r498_n1.h5
