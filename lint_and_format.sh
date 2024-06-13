#!/bin/bash
# Setup environment variables

# format code (this should not change any functionality)
ruff format --line-length 120
# format imports (also should not change functionality)
ruff check --select I --fix .
# lint code and try to auto-fix issues (may report some issues
# that need to be fixed by hand)
ruff --line-length 120 --fix
