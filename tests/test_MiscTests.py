import os
import re

def test_environment_setup():
    # so we can run from project root or 'tests' folder
    curr_dir = os.getcwd()
    setup_script_path = "" 
    if "tests" in curr_dir:
        setup_script_path = "../setup.sh"
    else:
        setup_script_path = "setup.sh"
    
    # Read the script to extract expected values
    expected_values = {}
    with open(setup_script_path, "r") as f:
        for line in f:
            match = re.match(r'^export (\w+)="(.*)"', line)
            if match:
                key, value = match.groups()
                expected_values[key] = value

    assert "PYTHONPATH" in expected_values
    assert "OUTPUT_ROOT" in expected_values
    assert "SUITE_CONFIG" in expected_values

    # Iterate and print out the values of expected_values
    for key, value in expected_values.items():
        if key == "PYTHONPATH":
            assert value == "$PYTHONPATH:$current_dir"
        elif key == "OUTPUT_ROOT":
            assert value != ""
        elif key == "SUITE_CONFIG":
            assert value != ""