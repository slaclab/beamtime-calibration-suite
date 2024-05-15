from calibrationSuite.basicSuiteScript import BasicSuiteScript

def test_makeProfile(example_data):
    bSS = BasicSuiteScript()
    print("have built a BasicSuiteScript")
    bSS.setupPsana()
    evt = bSS.getEvt()
    print(dir(evt))