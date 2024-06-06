#!/bin/bash
# Setup environment variables

ruff format --line-length 120
ruff --line-length 120 --fix
