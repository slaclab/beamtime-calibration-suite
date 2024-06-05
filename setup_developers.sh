#!/bin/bash
# Setup environment variables

# setup for running all the tests
# only needs to be run once in each download of this repo
# (as opposed to setup.sh which needs to be run each new terminal session)
pip install pillow
git submodule init
git submodule update
