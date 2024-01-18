import numpy as np
import pytest
from fitFunctions import linear, saturatedLinear


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
