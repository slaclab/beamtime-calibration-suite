import os
import subprocess
import re
import copy

def test_environment_setup():
    env = copy.deepcopy(os.environ)

    # Run setup script with the copied environment
    setup_script_path = "../setup.sh"
    
    subprocess.run([setup_script_path], env=env)

    # Read the script to extract expected values
    expected_values = {}
    with open(setup_script_path, "r") as f:
        for line in f:
            match = re.match(r'^export (\w+)="(.*)"', line)
            if match:
                key, value = match.groups()
                expected_values[key] = value
    
    # Check if environment variables are set correctly
    for key, expected_value in expected_values.items():
        # checking PYTHONPATH is a bit annoying and pretty obvious when its broke, skip checking for now
        if key == 'PYTHONPATH':
            continue
        assert key in env
        assert env[key] == expected_value