import re
import subprocess


def test_environment_setup():
    # annoyingly complicated way to get root of current git repo,
    # do this so test can be run from tests/ dir or root of project
    git_repo_root = (
        subprocess.Popen(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE)
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )

    setup_script_path = git_repo_root + "/setup.sh"

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
            assert value == "$PYTHONPATH:$git_project_root_dir"
        elif key == "OUTPUT_ROOT":
            assert value != ""
        elif key == "SUITE_CONFIG":
            assert value != ""
