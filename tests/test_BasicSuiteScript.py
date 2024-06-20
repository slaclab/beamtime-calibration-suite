import os
import subprocess
import sys

import pytest

# Quick and simple test that creates the main calibrationSuite object that all the /suite_scripts
# are built on. atm we just try to make the object and make sure nothing explodes, but should add more checks.


@pytest.fixture()
def psana_installed():
    try:
        import psana  # noqa: F401

        return True
    except ImportError:
        return False


def test_example(psana_installed):
    # only run these tests when running locally on S3DF
    if not psana_installed:
        pytest.skip("Can only test with psana library on S3DF!")
    else:
        from calibrationSuite.basicSuiteScript import BasicSuiteScript

        # make psanaBase think we ran with a normal command and setup
        sys.argv = ["SimpleClustersParallelSlice.py", "-r", "118", "-p", "/basic_suite_test"]

        # annoyingly complicated way to get root of current git repo,
        # do this so test can be run from tests/ dir or root of project
        git_repo_root = (
            subprocess.Popen(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE)
            .communicate()[0]
            .rstrip()
            .decode("utf-8")
        )

        os.environ["OUTPUT_ROOT"] = "."
        os.environ["SUITE_CONFIG"] = git_repo_root + "/tests/testingSuiteConfig.py"
        # to be sure this script acts the same as those in suite_scripts (in regards to file-paths)
        os.chdir(git_repo_root + "/suite_scripts/")
        os.makedirs("basic_suite_test", exist_ok=True)

        bSS = BasicSuiteScript()
        assert bSS is not None
        # since only test base2 for now
        assert os.environ["PS_SMD_N_EVENTS"] == "50"
        assert os.environ["PS_SRV_NODES"] == "1"

        print("have built a BasicSuiteScript")
        bSS.setupPsana()
        evt = bSS.getEvt()
        assert evt is not None

        stepGen = bSS.getStepGen()
        assert stepGen is not None

        # this is slow, don't do for now
        """
        count = 0
        maxEventsToEnumer = 100
        for nstep, step in enumerate(stepGen):
            count += 1
            if count == maxEventsToEnumer:
                break
        assert 0 == 1
        """

        # cleanup
        os.rmdir("basic_suite_test")

        # TODO: add checks that init and setupPsana stuff is set properly,
        # also call and test directly some class-methods.

        """
        # also here's a way to potentially test creating a base object
        base = PsanaBase()

        assert base.psanaType == 2
        assert base.gainModes == {
            "FH": 0,
            "FM": 1,
            "FL": 2,
            "AHL-H": 3,
            "AML-M": 4,
            "AHL-L": 5,
            "AML-L": 6,
        }
        assert base.ePix10k_cameraTypes == {
            1: "Epix10ka",
            4: "Epix10kaQuad",
            16: "Epix10ka2M",
        }
        assert base.allowed_timestamp_mismatch == 1000
        expected_experimentHash = {
            "detectorType": "epixhr",
            "exp": "rixx1003721",
            "location": "RixEndstation",
            "fluxSource": "MfxDg1BmMon",
            "fluxChannels": [15],
            "fluxSign": -1,
            "singlePixels": [
                [0, 150, 10],
                [0, 150, 100],
                [0, 275, 100],
                [0, 272, 66],
                [0, 280, 70],
                [0, 282, 90],
                [0, 270, 90],
                [0, 271, 90],
                [0, 272, 90],
                [0, 273, 90],
                [0, 287, 95],
                [0, 286, 72],
                [0, 276, 100],
                [0, 277, 100],
                [0, 278, 100],
            ],
            "ROIs": ["../data/XavierV4_2", "../data/OffXavierV4_2"],
            "regionSlice": (slice(270, 288, None), slice(59, 107, None)),
        }
        assert base.experimentHash == expected_experimentHash

        base.setupPsana()
        """
