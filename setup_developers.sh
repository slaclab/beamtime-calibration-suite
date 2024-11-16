#!/bin/bash
# this script sets things up for running the tests and linting/formatting scripts.
# only needs to be run once in each download of this repo
# (as opposed to setup.sh which needs to be run each new terminal session)

# this script assumes you are running on S3DF and are using the psana environment,
# (you have executed 'source /sdf/group/lcls/ds/ana/sw/conda2/manage/bin/psconda.sh')

# dependencies used in tests + formatting/linting script
# (these might already be installed into the S3DF env, if so the following cmds should simply do nothing)
pip install pytest
pip install pillow
pip install ruff

# nice output formatting for pytest
pip install pytest-sugar

# init git large file storage (LFS)
# (assumes git LFS is installed on system already)
git lfs install

# setup test_data submodule
git submodule init
git submodule update
