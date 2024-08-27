#!/bin/bash
# Setup environment variables


# current_dir=$(pwd)
git_project_root_dir=$(git rev-parse --show-toplevel)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$git_project_root_dir"
echo "PYTHONPATH = $PYTHONPATH"

# so output folders are written in a shared location
##export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/scratch/"
##export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/results/"
export OUTPUT_ROOT="/sdf/data/lcls/ds/det/detdaq21/results/"
echo "OUTPUT_ROOT = $OUTPUT_ROOT"

# point to which config file to use
##export SUITE_CONFIG="$git_project_root_dir/config_files/epixMSuiteConfig.py"
export SUITE_CONFIG="$git_project_root_dir/config_files/epix10kQuadSuiteConfig.py"
echo "SUITE_CONFIG = $SUITE_CONFIG"
