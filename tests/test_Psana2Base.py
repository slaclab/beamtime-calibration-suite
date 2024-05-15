import pytest

@pytest.fixture()
def psana_installed():
    try:
        import psana
        return True
    except ImportError:
        return False

def test_example(psana_installed):
    if not psana_installed:
        pass # only run these tests when running locally on S3DF
    else:
        from calibrationSuite.psana2Base import PsanaBase
        sys.argv = ['LinearityPlotsParallel.py', '-r', '159', '-f', '../scan/LinearityPlotsParallel_c0_r159_n100.h5']
        base = PsanaBase()
        print ('Hello!!')
        exit(1)