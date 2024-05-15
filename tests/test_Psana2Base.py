import pytest
import sys
import os

@pytest.fixture()
def psana_installed():
    try:
        import psana
        return True
    except ImportError:
        return False

def test_example(psana_installed):
    # only run these tests when running locally on S3DF
    if not psana_installed:
        pass
    else:
        from calibrationSuite.psana2Base import PsanaBase
        
        # make psanaBase think we ran with a normal command and setup
        sys.argv = ['LinearityPlotsParallel.py', '-r', '159', '-f', '../scan/LinearityPlotsParallel_c0_r159_n100.h5']
        os.environ['SUITE_CONFIG'] = '../suite_scripts/rixSuiteConfig.py'
        base = PsanaBase()



