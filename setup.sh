#!/bin/bash
# Setup environment variables

# Get the current directory
current_dir=$(pwd)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$current_dir"

# so output folders are written in a shared location
export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/"

# point to which config file to use
export SUITE_CONFIG="rixSuiteConfig.py"
