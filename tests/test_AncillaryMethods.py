import numpy as np
import pytest

from calibrationSuite.ancillaryMethods import (
    getClusterEnergies,
    getEnergeticClusters,
    getMatchedClusters,
    getSmallClusters,
    getSmallSquareClusters,
    getSquareClusters,
    goodClusters,
    makeProfile,
)


@pytest.fixture
def example_data():
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 3, 4, 5, 6])
    return x, y


def test_makeProfile(example_data):
    x, y = example_data
    bins = 3
    bin_centers, means, y_err = makeProfile(x, y, bins)

    assert np.allclose(bin_centers, np.array([1.66666667, 3.0, 4.33333333]))
    assert np.allclose(means, [2.5, 4.0, 5.5])
    assert np.allclose(y_err, [0.35355339, 0.0, 0.35355339])


def test_getEnergeticClusters():
    clusters = np.array([[[1, 1, 1], [2, 1, 2]], [[2, 1, 2], [-1, 1, 3]]])
    energetic_clusters = getEnergeticClusters(clusters)

    assert np.array_equal(energetic_clusters, [[1, 1, 1], [2, 1, 2], [2, 1, 2]])


def test_getSmallSquareClusters():
    clusters = np.array([[1, 1, 1, 1, 4, 1], [2, 1, 2, 2, 3, 1], [2, 1, 2, 2, 5, 0], [3, 1, 2, 2, 6, 1]])
    small_square_clusters = getSmallSquareClusters(clusters)

    assert np.array_equal(small_square_clusters, [[2, 1, 2, 2, 3, 1]])


def test_getSmallClusters():
    clusters = np.array([[1, 1, 1, 1, 4, 1], [2, 1, 2, 2, 3, 1], [2, 1, 2, 2, 5, 0], [3, 1, 2, 2, 6, 1]])
    small_clusters = getSmallClusters(clusters)
    assert np.array_equal(small_clusters, [[2, 1, 2, 2, 3, 1]])


def test_getSquareClusters():
    clusters = np.array([[1, 1, 1, 1, 4, 1], [2, 1, 2, 2, 3, 1], [2, 1, 2, 2, 5, 0], [3, 1, 2, 2, 6, 1]])
    square_clusters = getSquareClusters(clusters)
    assert np.array_equal(square_clusters, [[1, 1, 1, 1, 4, 1], [2, 1, 2, 2, 3, 1], [3, 1, 2, 2, 6, 1]])


def test_getMatchedClusters():
    clusters = np.array([[1, 1, 1, 6], [2, 1, 2, 6], [2, 2, 2, 6], [3, 4, 3, 6]])
    dimension = "module"
    n = 1
    matched_clusters = getMatchedClusters(clusters, dimension, n)
    assert np.array_equal(matched_clusters, [[1, 1, 1, 6], [2, 1, 2, 6]])

    dimension = "row"
    n = 1
    matched_clusters = getMatchedClusters(clusters, dimension, n)
    assert np.array_equal(matched_clusters, [[1, 1, 1, 6]])

    dimension = "column"
    n = 6
    matched_clusters = getMatchedClusters(clusters, dimension, n)
    assert np.array_equal(matched_clusters, [[1, 1, 1, 6], [2, 1, 2, 6], [2, 2, 2, 6], [3, 4, 3, 6]])


def test_goodClusters():
    clusters = np.array(
        [
            [[1, 1, 1, 1, 4, 1], [2, 1, 2, 2, 3, 1]],
            [[2, 1, 2, 2, 5, 0], [3, 1, 2, 2, 6, 1]],
        ]
    )
    module = 1
    row = 2
    col = 2
    n_pixel_cut = 4
    is_square = 1
    good = goodClusters(clusters, module, row, col, n_pixel_cut, is_square)

    assert np.array_equal(good, [[2, 1, 2, 2, 3, 1]])


def test_getClusterEnergies():
    clusters = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    energies = getClusterEnergies(clusters)
    assert np.array_equal(energies, [1, 2, 3, 4])
