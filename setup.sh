#!/bin/bash
# Setup environment variables

# Get the current directory
current_dir=$(pwd)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$current_dir"
echo "PYTHONPATH = $PYTHONPATH"

# so output folders are written in a shared location
##export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/scratch/"
export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/results/"
echo "OUTPUT_ROOT = $OUTPUT_ROOT"

# point to which config file to use
export SUITE_CONFIG="epixMSuiteConfig.py"
echo "SUITE_CONFIG = $SUITE_CONFIG"