#!/bin/bash

echo "Setting environment variables..."

# Get the current directory
current_dir=$(pwd)

export PYTHONPATH="$PYTHONPATH:$current_dir"
echo "PYTHONPATH appended with: $current_dir"

#if you usually use same config file, convenient to add the following
#export SUITE_CONFIG="<config file name>.py"
