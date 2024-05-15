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
        assert 1 == 1
        '''
        from calibrationSuite.basicSuiteScript import BasicSuiteScript

        #assert os.environ["PS_SMD_N_EVENTS"] == "50" 
        #assert os.environ["PS_SRV_NODES"] == "1"
    
        
        # make psanaBase think we ran with a normal command and setup
        sys.argv = ['SimpleClustersParallelSlice.py', '-r', '118']
        os.environ['SUITE_CONFIG'] = 'testSuiteConfig.py'
        
        bSS = BasicSuiteScript()
        print("have built a BasicSuiteScript")
        bSS.setupPsana()
        evt = bSS.getEvt()
        '''


        '''    
        base = PsanaBase()
    
        assert base.psanaType == 2
        assert base.gainModes == {"FH": 0, "FM": 1, "FL": 2, "AHL-H": 3, "AML-M": 4, "AHL-L": 5, "AML-L": 6}
        assert base.ePix10k_cameraTypes == {1: "Epix10ka", 4: "Epix10kaQuad", 16: "Epix10ka2M"} 
        assert base.allowed_timestamp_mismatch == 1000
        expected_experimentHash = {
            'detectorType': 'epixhr',
            'exp': 'rixx1003721',
            'location': 'RixEndstation',
            'fluxSource': 'MfxDg1BmMon',
            'fluxChannels': [15],
            'fluxSign': -1,
            'singlePixels': [
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
                [0, 278, 100]
            ],
            'ROIs': ['../data/XavierV4_2', '../data/OffXavierV4_2'],
            'regionSlice': (slice(270, 288, None), slice(59, 107, None))
        }
        assert base.experimentHash == expected_experimentHash

        base.setupPsana()
        '''
