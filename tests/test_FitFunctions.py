import numpy as np
import pytest

from calibrationSuite.fitFunctions import (
    calculateFitR2,
    estimateGaussianParametersFromUnbinnedArray,
    estimateGaussianParametersFromXY,
    fitNorm,
    gaussian,
    gaussianArea,
    getBinCentersFromNumpyHistogram,
    getHistogramMeanStd,
    getRestrictedHistogram,
    linear,
    saturatedLinear,
    saturatedLinearB,
)


@pytest.mark.parametrize("a, b, expected", [(2, 3, np.array([5, 7, 9, 11, 13]))])
def test_linear(a, b, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = linear(x, a, b)
    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    "a, b, c, d, expected", [(2, 3, 4, 10, np.array([5, 7, 9, 10, 10]))]
)
def test_saturatedLinear(a, b, c, d, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = saturatedLinear(x, a, b, c, d)
    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize("a, b, d, expected", [(2, 3, 10, np.array([5, 7, 9, 10, 10]))])
def test_saturatedLinearB(a, b, d, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = saturatedLinearB(x, a, b, d)
    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    "a, mu, sigma, expected",
    [
        (
            1,
            3,
            0.5,
            np.array(
                [
                    0.0003354626279025118,
                    0.13533528323661267,
                    1.0,
                    0.13533528323661267,
                    0.0003354626279025118,
                ]
            ),
        )
    ],
)
def test_gaussian(a, mu, sigma, expected):
    x = np.array([1, 2, 3, 4, 5])
    result = gaussian(x, a, mu, sigma)
    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize("a, sigma, expected", [(10, 0.5, 31.4)])
def test_gaussianArea(a, sigma, expected):
    result = gaussianArea(a, sigma)
    assert np.isclose(result, expected)


def test_estimateGaussianParametersFromUnbinnedArray():
    flatData = np.array([1, 2, 3, 4, 5])
    result_amp, result_mean, result_sigma = estimateGaussianParametersFromUnbinnedArray(
        flatData
    )
    expected_amp, expected_mean, expected_sigma = (
        0.5629831060402448,
        3.0,
        1.4142135623730951,
    )
    assert np.isclose(result_amp, expected_amp)
    assert result_mean == expected_mean
    assert np.isclose(result_sigma, expected_sigma)


def test_estimateGaussianParametersFromXY():
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 4, 2])
    result_amp, result_mean, result_sigma = estimateGaussianParametersFromXY(x, y)
    expected_amp, expected_mean, expected_sigma = (
        2.482238418490429,
        3.0,
        1.1547005383792515,
    )
    assert np.isclose(result_amp, expected_amp)
    assert result_mean == expected_mean
    assert np.isclose(result_sigma, expected_sigma)


def test_getHistogramMeanStd():
    binCenters = np.array([1, 2, 3, 4, 5])
    counts = np.array([2, 4, 6, 4, 2])
    result_mean, result_std = getHistogramMeanStd(binCenters, counts)
    expected_mean, expected_std = 3.0, 1.1547005383792515
    assert result_mean == expected_mean
    assert np.isclose(result_std, expected_std)


@pytest.mark.parametrize(
    "y, fit, expected_r2", [(np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3, 4, 6]), 0.9)]
)
def test_calculateFitR2(y, fit, expected_r2):
    result_r2 = calculateFitR2(y, fit)
    print(result_r2)
    assert np.isclose(result_r2, expected_r2)


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


@pytest.mark.parametrize(
    "data, expected_mean, expected_std",
    [(np.array([1, 2, 3, 4, 5]), 3.0, 1.4142135623730951)],
)
def test_fitNorm(data, expected_mean, expected_std):
    result_mean, result_std = fitNorm(data)
    assert np.isclose(result_mean, expected_mean)
    assert np.isclose(result_std, expected_std)
