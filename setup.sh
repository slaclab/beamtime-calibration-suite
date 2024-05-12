#!/bin/bash
# Setup environment variables

# Get the current directory
current_dir=$(pwd)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$current_dir"

# so output folders are written in a shared location
echo "export OUTPUT_ROOT="\"$OUTPUT_ROOT\"

# point to which config file to use
#export SUITE_CONFIG="rixSuiteConfig.py"
export SUITE_CONFIG="epixMSuiteConfig.py"
echo "export SUITE_CONFIG="\"$SUITE_CONFIG\"
