#!/bin/bash
# Setup environment variables

# setup for running all the tests
# only needs to be run once in each download of this repo
# (as opposed to setup.sh which needs to be run each new terminal session)

# dependencies used in tests + formatting/linting script
# (these might already be installed into the S3DF env, if so the following cmds should simply do nothing)
pip install pytest
pip install pillow
pip install ruff

# nice output formatting for pytest
pip install pytest-sugar

# setup test_data submodule
git submodule init
git submodule update
