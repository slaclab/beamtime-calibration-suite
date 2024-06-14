import numpy as np

from calibrationSuite.cluster import BuildClusters, Cluster


def test_cluster_initialization():
    cluster = Cluster(1, 1, 10)
    assert cluster.seedCol == 1
    assert cluster.seedRow == 1
    assert cluster.seedEnergy == 10
    assert cluster.nPixels == 1
    assert cluster.nMaskedPixels == 0
    assert cluster.eTotal == 10
    assert cluster.eTotalNoCuts == 10
    assert cluster.eSecondaryPixelNoCuts == 0
    assert cluster.goodCluster is True
    assert cluster.clusterSide == 3

    expectedE = np.zeros((3, 3))
    expectedE[1][1] = 10
    assert np.array_equal(cluster.pixelE, expectedE)


def test_cluster_add_pixel():
    cluster = Cluster(1, 1, 10)
    cluster.addPixel(0, 1, 5)
    assert cluster.nPixels == 2
    assert cluster.eTotal == 15
    assert np.array_equal(cluster.pixelE, np.array([[0, 0, 0], [0, 10, 5], [0, 0, 0]]))


def test_cluster_centroid():
    cluster = Cluster(1, 1, 10)
    cluster.addPixel(0, 1, 5)
    centroid = cluster.centroid()
    assert np.allclose(centroid, (1.0, 1.33333))


def test_build_clusters_find_clusters():
    frame = np.array([[0, 0, 0], [0, 10, 0], [0, 0, 0]])
    build_clusters = BuildClusters(frame, seedCut=5, neighborCut=3)
    clusters = build_clusters.findClusters()
    assert len(clusters) == 1
    assert clusters[0].seedCol == 1
    assert clusters[0].seedRow == 1
    assert clusters[0].seedEnergy == 10
    assert clusters[0].nPixels == 1
    assert clusters[0].eTotal == 10
    assert clusters[0].eTotalNoCuts == 10
    assert clusters[0].eSecondaryPixelNoCuts == 0
    assert clusters[0].goodCluster is True
    assert np.array_equal(
        clusters[0].pixelE, np.array([[0, 0, 0], [0, 10, 0], [0, 0, 0]])
    )
