#!/bin/bash
# sets up environment variables for running the suite.

# this script assumes you are running on S3DF and are using the psana environment,
# (you have executed 'source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh')


# current_dir=$(pwd)
git_project_root_dir=$(git rev-parse --show-toplevel)
# so scripts can find the calibrationSuite library code
export PYTHONPATH="$PYTHONPATH:$git_project_root_dir"
echo "PYTHONPATH = $PYTHONPATH"

# so output folders are written in a shared location
##export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/scratch/"
export OUTPUT_ROOT="/sdf/data/lcls/ds/rix/rixx1005922/results/"
##export OUTPUT_ROOT="/sdf/data/lcls/ds/det/detdaq21/results/"
echo "OUTPUT_ROOT = $OUTPUT_ROOT"

# point to which config file to use
export SUITE_CONFIG="$git_project_root_dir/config_files/epixMSuiteConfig.py"
##export SUITE_CONFIG="$git_project_root_dir/config_files/epix100SuiteConfig.py"
echo "SUITE_CONFIG = $SUITE_CONFIG"
