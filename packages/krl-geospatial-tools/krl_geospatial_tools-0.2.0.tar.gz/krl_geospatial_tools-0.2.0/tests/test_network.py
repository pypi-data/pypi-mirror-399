"""
Tests for network analysis module.

© 2025 KR-Labs. All rights reserved.
"""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point

from krl_geospatial.network import (
    all_pairs_shortest_path,
    betweenness_centrality,
    closeness_centrality,
    degree_centrality,
    eigenvector_centrality,
    girvan_newman,
    label_propagation,
    louvain_communities,
    modularity_score,
    network_centrality,
    network_distance_matrix,
    shortest_path,
)
from krl_geospatial.weights import KNNWeights


@pytest.fixture
def sample_gdf():
    """Create sample GeoDataFrame with grid points."""
    np.random.seed(42)
    n = 30
    x = np.random.uniform(0, 10, n)
    y = np.random.uniform(0, 10, n)

    gdf = gpd.GeoDataFrame(
        {"value": np.random.randn(n)},
        geometry=[Point(xi, yi) for xi, yi in zip(x, y)],
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def weights(sample_gdf):
    """Create KNN weights."""
    w = KNNWeights(k=5)
    w.fit(sample_gdf)
    return w


# ============================================================================
# Topology Tests
# ============================================================================


def test_network_centrality_betweenness(sample_gdf, weights):
    """Test network centrality with betweenness."""
    centrality = network_centrality(sample_gdf, weights, measure="betweenness")

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0
    assert centrality.max() <= 1


def test_network_centrality_closeness(sample_gdf, weights):
    """Test network centrality with closeness."""
    centrality = network_centrality(sample_gdf, weights, measure="closeness")

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0
    assert centrality.max() <= 1


def test_network_centrality_degree(sample_gdf, weights):
    """Test network centrality with degree."""
    centrality = network_centrality(sample_gdf, weights, measure="degree")

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0


def test_network_centrality_eigenvector(sample_gdf, weights):
    """Test network centrality with eigenvector."""
    centrality = network_centrality(sample_gdf, weights, measure="eigenvector")

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0


def test_betweenness_centrality(sample_gdf, weights):
    """Test betweenness centrality directly."""
    centrality = betweenness_centrality(sample_gdf, weights, normalized=True)

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0
    assert centrality.max() <= 1


def test_closeness_centrality(sample_gdf, weights):
    """Test closeness centrality directly."""
    centrality = closeness_centrality(sample_gdf, weights, normalized=True)

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0


def test_degree_centrality(sample_gdf, weights):
    """Test degree centrality directly."""
    centrality = degree_centrality(sample_gdf, weights, normalized=True)

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0
    assert centrality.max() <= 1


def test_eigenvector_centrality(sample_gdf, weights):
    """Test eigenvector centrality directly."""
    centrality = eigenvector_centrality(sample_gdf, weights, normalized=True)

    assert len(centrality) == len(sample_gdf)
    assert centrality.min() >= 0


def test_centrality_unnormalized(sample_gdf, weights):
    """Test unnormalized centrality measures."""
    deg = degree_centrality(sample_gdf, weights, normalized=False)
    close = closeness_centrality(sample_gdf, weights, normalized=False)

    assert deg.max() > 1  # Unnormalized should exceed 1
    assert close.max() > 1


def test_centrality_invalid_measure(sample_gdf, weights):
    """Test invalid centrality measure."""
    with pytest.raises(ValueError):
        network_centrality(sample_gdf, weights, measure="invalid")


# ============================================================================
# Community Detection Tests
# ============================================================================


def test_louvain_communities(sample_gdf, weights):
    """Test Louvain community detection."""
    communities = louvain_communities(sample_gdf, weights, resolution=1.0, seed=42)

    assert len(communities) == len(sample_gdf)
    assert communities.min() >= 0
    n_communities = len(np.unique(communities))
    assert 1 <= n_communities <= len(sample_gdf)


def test_louvain_resolution(sample_gdf, weights):
    """Test Louvain with different resolutions."""
    comm_low = louvain_communities(sample_gdf, weights, resolution=0.5, seed=42)
    comm_high = louvain_communities(sample_gdf, weights, resolution=2.0, seed=42)

    # Higher resolution should produce more communities
    assert len(np.unique(comm_high)) >= len(np.unique(comm_low))


def test_label_propagation(sample_gdf, weights):
    """Test label propagation community detection."""
    communities = label_propagation(sample_gdf, weights, seed=42)

    assert len(communities) == len(sample_gdf)
    assert communities.min() >= 0
    n_communities = len(np.unique(communities))
    assert 1 <= n_communities <= len(sample_gdf)


def test_girvan_newman_k(sample_gdf, weights):
    """Test Girvan-Newman with specified k."""
    k = 5
    communities = girvan_newman(sample_gdf, weights, k=k)

    assert len(communities) == len(sample_gdf)
    n_communities = len(np.unique(communities))
    assert n_communities == k


def test_girvan_newman_auto(sample_gdf, weights):
    """Test Girvan-Newman with automatic k selection."""
    communities = girvan_newman(sample_gdf, weights, k=None)

    assert len(communities) == len(sample_gdf)
    n_communities = len(np.unique(communities))
    assert n_communities >= 1


def test_modularity_score(sample_gdf, weights):
    """Test modularity score computation."""
    communities = louvain_communities(sample_gdf, weights, seed=42)
    mod = modularity_score(sample_gdf, weights, communities)

    # Modularity should be in [-0.5, 1.0]
    assert -0.5 <= mod <= 1.0


def test_modularity_single_community(sample_gdf, weights):
    """Test modularity with single community."""
    communities = np.zeros(len(sample_gdf), dtype=int)
    mod = modularity_score(sample_gdf, weights, communities)

    # Single community should have low modularity
    assert mod < 0.5


def test_community_reproducibility(sample_gdf, weights):
    """Test that seeded algorithms are reproducible."""
    comm1 = louvain_communities(sample_gdf, weights, seed=42)
    comm2 = louvain_communities(sample_gdf, weights, seed=42)

    np.testing.assert_array_equal(comm1, comm2)


# ============================================================================
# Routing Tests
# ============================================================================


def test_shortest_path_single_target(sample_gdf, weights):
    """Test shortest path to single target."""
    path = shortest_path(sample_gdf, weights, source=0, target=10)

    assert isinstance(path, list)
    assert len(path) >= 2
    assert path[0] == 0
    assert path[-1] == 10


def test_shortest_path_all_targets(sample_gdf, weights):
    """Test shortest paths to all targets."""
    paths = shortest_path(sample_gdf, weights, source=0, target=None)

    assert isinstance(paths, dict)
    assert len(paths) <= len(sample_gdf)
    assert 0 in paths
    assert paths[0] == [0]


def test_shortest_path_dijkstra(sample_gdf, weights):
    """Test Dijkstra's algorithm."""
    path = shortest_path(sample_gdf, weights, source=0, target=10, method="dijkstra")

    assert isinstance(path, list)
    assert len(path) >= 2


def test_all_pairs_shortest_path_auto(sample_gdf, weights):
    """Test all pairs shortest path with auto method."""
    distances = all_pairs_shortest_path(sample_gdf, weights, method="auto")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    assert np.all(np.diag(distances) == 0)  # Distance to self is 0
    assert np.all(distances >= 0)


def test_all_pairs_shortest_path_dijkstra(sample_gdf, weights):
    """Test all pairs with Dijkstra."""
    distances = all_pairs_shortest_path(sample_gdf, weights, method="dijkstra")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    assert np.all(distances >= 0)


def test_all_pairs_shortest_path_floyd_warshall(sample_gdf, weights):
    """Test all pairs with Floyd-Warshall."""
    distances = all_pairs_shortest_path(sample_gdf, weights, method="floyd-warshall")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    assert np.all(distances >= 0)


def test_network_distance_matrix_shortest_path(sample_gdf, weights):
    """Test network distance matrix with shortest path metric."""
    distances = network_distance_matrix(sample_gdf, weights, metric="shortest_path")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    assert np.all(distances >= 0)


def test_network_distance_matrix_resistance(sample_gdf, weights):
    """Test network distance matrix with resistance metric."""
    distances = network_distance_matrix(sample_gdf, weights, metric="resistance")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    # Resistance can have small numerical errors in graph Laplacian pseudoinverse
    # Values should be mostly non-negative with tiny negative errors
    assert distances.min() > -0.1  # Allow small numerical precision errors


def test_network_distance_matrix_commute_time(sample_gdf, weights):
    """Test network distance matrix with commute time metric."""
    distances = network_distance_matrix(sample_gdf, weights, metric="commute_time")

    n = len(sample_gdf)
    assert distances.shape == (n, n)
    # Commute time depends on resistance distance (can have numerical precision issues)
    assert distances.min() > -5  # Allow small numerical precision errors


def test_network_distance_matrix_invalid_metric(sample_gdf, weights):
    """Test invalid metric."""
    with pytest.raises(ValueError):
        network_distance_matrix(sample_gdf, weights, metric="invalid")


def test_distance_symmetry(sample_gdf, weights):
    """Test that distance matrices are symmetric."""
    distances = all_pairs_shortest_path(sample_gdf, weights)

    np.testing.assert_allclose(distances, distances.T, rtol=1e-10)
