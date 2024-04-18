#!/bin/bash
# Setup environment variables

# Get the current directory
current_dir=$(pwd)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$current_dir"

# so output folders are written in a shared location
#export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1003721/results/scripts/"
export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/scratch/"
echo "export OUTPUT_ROOT="\"$OUTPUT_ROOT\"

# point to which config file to use
#export SUITE_CONFIG="rixSuiteConfig.py"
config_file_dir="$current_dir/config_files"
export SUITE_CONFIG="$config_file_dir/epixMSuiteConfig.py"
echo "export SUITE_CONFIG="\"$SUITE_CONFIG\"