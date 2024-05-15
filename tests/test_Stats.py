import numpy as np
from calibrationSuite.Stats import Stats


def test_Stats_mean():
    test_size = 10
    data = np.random.rand(test_size)  # Generate random data
    s = Stats(data.shape)
    
    assert s._x.shape == (test_size,)
    assert s._xx.shape == (test_size,)
    assert s._xy.shape == (test_size,)
    
    expected_n = test_size
    expected_x = 0
    expected_xx = 0
    expected_xy = 0
    y = 0 # default val when y arg not passed
    for d in data:
        s.accumulate(d) # not passing y
        expected_x += d
        expected_xx += d * d
        expected_xy += d * y

    assert s._n == expected_n    
    assert s._x[0] == expected_x
    assert s._xx[0] == expected_xx
    assert s._xy[0] == expected_xy

    calculated_mean = s.mean()
    expected_mean = np.mean(data)
    assert np.isclose(calculated_mean[0], expected_mean) , "Mean calculation incorrect"


def test_Stats_rms():
    test_size = 10
    data = np.random.rand(test_size)
    s = Stats(data.shape)
    
    expected_n = test_size
    expected_x = 0
    expected_xx = 0
    for d in data:
        s.accumulate(d)
        expected_x += d
        expected_xx += d * d

    calculated_rms = s.rms()
    expected_rms = ((expected_xx/ expected_n - (expected_x / expected_n) ** 2)).clip(0) ** 0.5
    
    assert np.isclose(calculated_rms[0], expected_rms), "RMS calculation incorrect"


def test_Stats_corr():
    test_size = 10
    x_data = np.random.rand(test_size)
    y_data = np.random.rand(test_size)

    expected_x = 0
    expected_xx = 0
    expected_xy = 0
    s = Stats(x_data.shape)
    for x, y in zip(x_data, y_data):
        s.accumulate(x, y)
        expected_x += x
        expected_xx += x * x
        expected_xy += x * y

    assert s._x[0] == expected_x
    assert s._xx[0] == expected_xx
    assert s._xy[0] == expected_xy

    y_mean = np.mean(y_data)
    y_sigma = np.std(y_data)
    calculated_corr = s.corr(y_mean, y_sigma)
    expected_corr = np.corrcoef(x_data, y_data)[0, 1]

    assert np.isclose(calculated_corr[0], expected_corr), "Correlation calculation incorrect"