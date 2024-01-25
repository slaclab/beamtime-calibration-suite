import numpy as np
import pytest
from scripts.fitFunctions import linear, saturatedLinear, saturatedLinearB, gaussian, \
    estimateGaussianParameters, getHistogramMeanStd, getBinCentersFromNumpyHistogram, getRestrictedHistogram

@pytest.mark.parametrize("a, b, expected", [(2, 3, np.array([5, 7, 9, 11, 13]))])
def test_linear(a, b, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = linear(x, a, b)
    np.testing.assert_array_equal(result, expected)

@pytest.mark.parametrize("a, b, c, d, expected", [(2, 3, 4, 10, np.array([5, 7, 9, 10, 10]))])
def test_saturatedLinear(a, b, c, d, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = saturatedLinear(x, a, b, c, d)
    np.testing.assert_array_equal(result, expected)

@pytest.mark.parametrize("a, b, d, expected", [(2, 3, 10, np.array([5, 7, 9, 10, 10]))])
def test_saturatedLinearB(a, b, d, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = saturatedLinearB(x, a, b, d)
    np.testing.assert_array_equal(result, expected)

@pytest.mark.parametrize("a, mu, sigma, expected", [(1, 3, 0.5, np.array([0.0003354626279025118, 0.13533528323661267, 1.0, 0.13533528323661267, 0.0003354626279025118]))])
def test_gaussian(a, mu, sigma, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = gaussian(x, a, mu, sigma)
    np.testing.assert_allclose(result, expected)

def test_estimateGaussianParameters():
    flatData = np.array([1, 2, 3, 4, 5])
    result_mean, result_std = estimateGaussianParameters(flatData)
    expected_mean, expected_std = 3.0, 1.4142135623730951
    assert result_mean == expected_mean
    assert np.isclose(result_std, expected_std)

def test_getHistogramMeanStd():
    binCenters = np.array([1, 2, 3, 4, 5])
    counts = np.array([2, 4, 6, 4, 2])
    result_mean, result_std = getHistogramMeanStd(binCenters, counts)
    expected_mean, expected_std = 3.0, 1.1547005383792515
    assert result_mean == expected_mean
    assert np.isclose(result_std, expected_std)

def test_getBinCentersFromNumpyHistogram():
    bins = np.array([1, 2, 3, 4, 5])
    result = getBinCentersFromNumpyHistogram(bins)
    expected = np.array([1.5, 2.5, 3.5, 4.5])
    np.testing.assert_array_equal(result, expected)
    
def test_getRestrictedHistogram():
    bins = np.array([1, 2, 3, 4, 5])
    counts = np.array([2, 4, 6, 4, 2])
    x0, x1 = 2, 4
    result_x, result_y = getRestrictedHistogram(bins, counts, x0, x1)
    expected_x = np.array([2, 3, 4])
    expected_y = np.array([4, 6, 4])
    np.testing.assert_array_equal(result_x, expected_x)
    np.testing.assert_array_equal(result_y, expected_y)
