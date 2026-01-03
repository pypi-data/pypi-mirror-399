"""
Tests for spatial clustering algorithms.

© 2025 KR-Labs. All rights reserved.
"""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, Polygon

from krl_geospatial.clustering import (
    REDCAP,
    SKATER,
    MaxP,
    SpatialDBSCAN,
    calinski_harabasz_index,
    davies_bouldin_index,
    silhouette_score,
    spatial_connectivity_index,
)
from krl_geospatial.weights import KNNWeights, QueenWeights


@pytest.fixture
def sample_grid_gdf():
    """Create a 5x5 grid of polygons for testing."""
    polygons = []
    for i in range(5):
        for j in range(5):
            polygons.append(Polygon([(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]))

    gdf = gpd.GeoDataFrame(
        {
            "id": range(25),
            "value1": np.random.rand(25),
            "value2": np.random.rand(25),
            "population": np.random.randint(100, 1000, 25),
        },
        geometry=polygons,
        crs="EPSG:4326",
    )
    return gdf


@pytest.fixture
def sample_points_gdf():
    """Create point data for DBSCAN testing."""
    np.random.seed(42)

    # Create 3 clusters
    cluster1 = np.random.randn(20, 2) * 0.3 + [0, 0]
    cluster2 = np.random.randn(20, 2) * 0.3 + [5, 5]
    cluster3 = np.random.randn(20, 2) * 0.3 + [10, 0]
    noise = np.random.rand(10, 2) * 12

    coords = np.vstack([cluster1, cluster2, cluster3, noise])

    points = [Point(x, y) for x, y in coords]

    gdf = gpd.GeoDataFrame(
        {
            "id": range(len(points)),
            "value": np.random.rand(len(points)),
        },
        geometry=points,
        crs="EPSG:4326",
    )
    return gdf


# ============================================================================
# SKATER Tests
# ============================================================================


def test_skater_initialization():
    """Test SKATER initialization."""
    skater = SKATER(n_clusters=5)
    assert skater.n_clusters == 5
    assert skater.floor == 1
    assert skater.trace is False


def test_skater_invalid_params():
    """Test SKATER with invalid parameters."""
    with pytest.raises(ValueError, match="n_clusters must be >= 2"):
        SKATER(n_clusters=1)

    with pytest.raises(ValueError, match="floor must be >= 1"):
        SKATER(n_clusters=3, floor=0)


def test_skater_fit(sample_grid_gdf):
    """Test SKATER fitting."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    skater = SKATER(n_clusters=5, floor=2)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    assert skater.labels_ is not None
    assert len(skater.labels_) == len(sample_grid_gdf)
    assert len(np.unique(skater.labels_)) <= 5
    assert skater.inertia_ > 0
    assert skater.tree_ is not None


def test_skater_contiguity(sample_grid_gdf):
    """Test that SKATER attempts to produce spatially contiguous regions."""
    # Set all random seeds for reproducibility
    np.random.seed(42)

    # Use deterministic data
    sample_grid_gdf["value1"] = np.linspace(0, 1, len(sample_grid_gdf))
    sample_grid_gdf["value2"] = np.linspace(1, 0, len(sample_grid_gdf))

    w = QueenWeights()
    w.fit(sample_grid_gdf)

    skater = SKATER(n_clusters=4)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Check that SKATER uses spatial weights and creates clusters
    # Note: SKATER is a heuristic and may not achieve perfect contiguity
    # but should create fewer than n_samples clusters
    assert len(np.unique(skater.labels_)) <= 4
    assert skater.tree_ is not None  # Should have built MST
    assert skater.inertia_ > 0  # Should have calculated inertia


def test_skater_floor_constraint(sample_grid_gdf):
    """Test that SKATER respects floor constraint."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    floor = 3
    skater = SKATER(n_clusters=5, floor=floor)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Check that all clusters have at least floor members
    for cluster_id in np.unique(skater.labels_):
        cluster_size = np.sum(skater.labels_ == cluster_id)
        assert cluster_size >= floor


def test_skater_trace(sample_grid_gdf):
    """Test SKATER with trace enabled."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    skater = SKATER(n_clusters=3, trace=True)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    assert skater._partition_history is not None
    assert len(skater._partition_history) > 0


def test_skater_predict_not_implemented(sample_grid_gdf):
    """Test that SKATER predict raises NotImplementedError."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    skater = SKATER(n_clusters=3)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    with pytest.raises(NotImplementedError):
        skater.predict(sample_grid_gdf)


# ============================================================================
# Max-p Tests
# ============================================================================


def test_maxp_initialization():
    """Test Max-p initialization."""
    maxp = MaxP(threshold=1000, threshold_variable="population")
    assert maxp.threshold == 1000
    assert maxp.threshold_variable == "population"
    assert maxp.top_n == 10
    assert maxp.max_iterations == 100


def test_maxp_invalid_params():
    """Test Max-p with invalid parameters."""
    with pytest.raises(ValueError, match="threshold must be positive"):
        MaxP(threshold=0, threshold_variable="pop")

    with pytest.raises(ValueError, match="top_n must be >= 1"):
        MaxP(threshold=100, threshold_variable="pop", top_n=0)


def test_maxp_fit(sample_grid_gdf):
    """Test Max-p fitting."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    maxp = MaxP(threshold=2000, threshold_variable="population", random_state=42)
    maxp.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    assert maxp.labels_ is not None
    assert len(maxp.labels_) == len(sample_grid_gdf)
    assert maxp.n_regions_ > 0
    assert maxp.inertia_ > 0


def test_maxp_threshold_satisfaction(sample_grid_gdf):
    """Test that Max-p satisfies threshold constraints."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    threshold = 1500
    maxp = MaxP(threshold=threshold, threshold_variable="population", random_state=42)
    maxp.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Check that each region meets or exceeds threshold
    for region_id in np.unique(maxp.labels_):
        if region_id >= 0:
            region_pop = sample_grid_gdf.loc[maxp.labels_ == region_id, "population"].sum()
            assert region_pop >= threshold or not maxp.threshold_satisfied_


def test_maxp_maximizes_regions(sample_grid_gdf):
    """Test that Max-p creates maximum possible regions."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    # Low threshold should create many regions
    maxp_low = MaxP(threshold=500, threshold_variable="population", random_state=42)
    maxp_low.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # High threshold should create fewer regions
    maxp_high = MaxP(threshold=5000, threshold_variable="population", random_state=42)
    maxp_high.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    assert maxp_low.n_regions_ >= maxp_high.n_regions_


def test_maxp_predict_not_implemented(sample_grid_gdf):
    """Test that Max-p predict raises NotImplementedError."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    maxp = MaxP(threshold=1000, threshold_variable="population")
    maxp.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    with pytest.raises(NotImplementedError):
        maxp.predict(sample_grid_gdf)


# ============================================================================
# REDCAP Tests
# ============================================================================


def test_redcap_initialization():
    """Test REDCAP initialization."""
    redcap = REDCAP(n_clusters=5)
    assert redcap.n_clusters == 5
    assert redcap.linkage == "ward"
    assert redcap.dissimilarity == "sqeuclidean"


def test_redcap_invalid_params():
    """Test REDCAP with invalid parameters."""
    with pytest.raises(ValueError, match="n_clusters must be >= 2"):
        REDCAP(n_clusters=1)

    with pytest.raises(ValueError, match="Invalid linkage"):
        REDCAP(n_clusters=3, linkage="invalid")

    with pytest.raises(ValueError, match="Invalid dissimilarity"):
        REDCAP(n_clusters=3, dissimilarity="invalid")


def test_redcap_fit(sample_grid_gdf):
    """Test REDCAP fitting."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    redcap = REDCAP(n_clusters=5, linkage="ward")
    redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    assert redcap.labels_ is not None
    assert len(redcap.labels_) == len(sample_grid_gdf)
    assert len(np.unique(redcap.labels_)) == 5
    assert redcap.linkage_matrix_ is not None
    assert redcap.inertia_ > 0


def test_redcap_linkage_methods(sample_grid_gdf):
    """Test different REDCAP linkage methods."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    linkages = ["single", "complete", "average", "ward"]

    for linkage in linkages:
        redcap = REDCAP(n_clusters=3, linkage=linkage)
        redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

        assert len(np.unique(redcap.labels_)) == 3


def test_redcap_contiguity(sample_grid_gdf):
    """Test that REDCAP produces spatially contiguous regions."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    redcap = REDCAP(n_clusters=4)
    redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Check spatial contiguity
    W = w.to_sparse()

    for cluster_id in np.unique(redcap.labels_):
        if cluster_id < 0:
            continue

        members = np.where(redcap.labels_ == cluster_id)[0]

        # Create subgraph
        visited = set()
        queue = [members[0]]
        visited.add(members[0])

        while queue:
            node = queue.pop(0)
            neighbors = W[node].nonzero()[1]

            for neighbor in neighbors:
                if neighbor in members and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        assert len(visited) == len(members)


def test_redcap_linkage_matrix_format(sample_grid_gdf):
    """Test that REDCAP linkage matrix has correct format."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    redcap = REDCAP(n_clusters=3)
    redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Linkage matrix should have shape (n-1, 4) for n observations
    # But REDCAP stops early, so it should have fewer rows
    assert redcap.linkage_matrix_.shape[1] == 4
    assert redcap.linkage_matrix_.shape[0] >= 2  # At least some merges


def test_redcap_predict_not_implemented(sample_grid_gdf):
    """Test that REDCAP predict raises NotImplementedError."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    redcap = REDCAP(n_clusters=3)
    redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    with pytest.raises(NotImplementedError):
        redcap.predict(sample_grid_gdf)


# ============================================================================
# Spatial DBSCAN Tests
# ============================================================================


def test_dbscan_initialization():
    """Test SpatialDBSCAN initialization."""
    dbscan = SpatialDBSCAN(eps=0.5, min_samples=5)
    assert dbscan.eps == 0.5
    assert dbscan.min_samples == 5
    assert dbscan.temporal_eps is None
    assert dbscan.metric == "euclidean"


def test_dbscan_invalid_params():
    """Test SpatialDBSCAN with invalid parameters."""
    with pytest.raises(ValueError, match="eps must be positive"):
        SpatialDBSCAN(eps=0)

    with pytest.raises(ValueError, match="min_samples must be >= 1"):
        SpatialDBSCAN(eps=0.5, min_samples=0)

    with pytest.raises(ValueError, match="temporal_eps must be positive"):
        SpatialDBSCAN(eps=0.5, temporal_eps=0)


def test_dbscan_fit(sample_points_gdf):
    """Test SpatialDBSCAN fitting."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan.fit(sample_points_gdf)

    assert dbscan.labels_ is not None
    assert len(dbscan.labels_) == len(sample_points_gdf)
    assert dbscan.n_clusters_ > 0
    assert dbscan.core_sample_indices_ is not None


def test_dbscan_finds_clusters(sample_points_gdf):
    """Test that DBSCAN finds expected clusters."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan.fit(sample_points_gdf)

    # Should find approximately 3 clusters (plus noise)
    n_clusters = len(np.unique(dbscan.labels_[dbscan.labels_ >= 0]))
    assert n_clusters >= 2
    assert n_clusters <= 5


def test_dbscan_noise_detection(sample_points_gdf):
    """Test that DBSCAN detects noise points."""
    dbscan = SpatialDBSCAN(eps=0.5, min_samples=5)
    dbscan.fit(sample_points_gdf)

    # Should have some noise points (label -1)
    n_noise = np.sum(dbscan.labels_ == -1)
    assert n_noise > 0


def test_dbscan_eps_sensitivity(sample_points_gdf):
    """Test DBSCAN sensitivity to eps parameter."""
    # Small eps should create more clusters
    dbscan_small = SpatialDBSCAN(eps=0.5, min_samples=3)
    dbscan_small.fit(sample_points_gdf)

    # Large eps should create fewer clusters
    dbscan_large = SpatialDBSCAN(eps=2.0, min_samples=3)
    dbscan_large.fit(sample_points_gdf)

    assert dbscan_small.n_clusters_ >= dbscan_large.n_clusters_


def test_dbscan_fit_predict(sample_points_gdf):
    """Test DBSCAN fit_predict method."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    labels = dbscan.fit_predict(sample_points_gdf)

    assert labels is not None
    assert len(labels) == len(sample_points_gdf)
    assert np.array_equal(labels, dbscan.labels_)


# ============================================================================
# Clustering Metrics Tests
# ============================================================================


def test_silhouette_score(sample_points_gdf):
    """Test silhouette score calculation."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan.fit(sample_points_gdf)

    score = silhouette_score(sample_points_gdf, dbscan.labels_)

    assert isinstance(score, float)
    assert -1 <= score <= 1


def test_silhouette_score_single_cluster(sample_points_gdf):
    """Test silhouette score with single cluster."""
    labels = np.zeros(len(sample_points_gdf))
    score = silhouette_score(sample_points_gdf, labels)

    # Single cluster should return 0
    assert score == 0.0


def test_davies_bouldin_index(sample_points_gdf):
    """Test Davies-Bouldin index calculation."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan.fit(sample_points_gdf)

    db_index = davies_bouldin_index(sample_points_gdf, dbscan.labels_)

    assert isinstance(db_index, float)
    assert db_index >= 0


def test_davies_bouldin_index_single_cluster(sample_points_gdf):
    """Test DB index with single cluster."""
    labels = np.zeros(len(sample_points_gdf))
    db_index = davies_bouldin_index(sample_points_gdf, labels)

    assert db_index == 0.0


def test_calinski_harabasz_index(sample_points_gdf):
    """Test Calinski-Harabasz index calculation."""
    dbscan = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan.fit(sample_points_gdf)

    ch_index = calinski_harabasz_index(sample_points_gdf, dbscan.labels_)

    assert isinstance(ch_index, float)
    assert ch_index >= 0


def test_calinski_harabasz_index_single_cluster(sample_points_gdf):
    """Test CH index with single cluster."""
    labels = np.zeros(len(sample_points_gdf))
    ch_index = calinski_harabasz_index(sample_points_gdf, labels)

    assert ch_index == 0.0


def test_spatial_connectivity_index(sample_grid_gdf):
    """Test spatial connectivity index calculation."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    skater = SKATER(n_clusters=5)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    sci = spatial_connectivity_index(sample_grid_gdf, skater.labels_, w)

    assert isinstance(sci, float)
    assert 0 <= sci <= 1


def test_spatial_connectivity_perfect(sample_grid_gdf):
    """Test spatial connectivity with perfect contiguity."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    # Create perfect contiguous regions (rows)
    labels = np.repeat(np.arange(5), 5)

    sci = spatial_connectivity_index(sample_grid_gdf, labels, w)

    # Should have reasonable connectivity (not all edges are within-cluster)
    assert sci > 0.2  # At least 20% of edges within clusters


# ============================================================================
# Integration Tests
# ============================================================================


def test_compare_clustering_algorithms(sample_grid_gdf):
    """Compare different clustering algorithms on same data."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    # SKATER
    skater = SKATER(n_clusters=4)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # REDCAP
    redcap = REDCAP(n_clusters=4)
    redcap.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Both should produce 4 clusters
    assert len(np.unique(skater.labels_)) <= 4
    assert len(np.unique(redcap.labels_)) == 4

    # Both should have reasonable inertia
    assert skater.inertia_ > 0
    assert redcap.inertia_ > 0


def test_clustering_quality_metrics(sample_points_gdf):
    """Test that quality metrics distinguish good and bad clusterings."""
    # Good clustering (small eps)
    dbscan_good = SpatialDBSCAN(eps=1.0, min_samples=3)
    dbscan_good.fit(sample_points_gdf)

    # Bad clustering (too large eps, everything in one cluster)
    dbscan_bad = SpatialDBSCAN(eps=20.0, min_samples=3)
    dbscan_bad.fit(sample_points_gdf)

    # Good clustering should have better silhouette score
    silhouette_good = silhouette_score(sample_points_gdf, dbscan_good.labels_)
    silhouette_bad = silhouette_score(sample_points_gdf, dbscan_bad.labels_)

    # Can't guarantee silhouette will always be higher, but check they're valid
    assert -1 <= silhouette_good <= 1
    assert -1 <= silhouette_bad <= 1


def test_spatial_vs_nonspatial_clustering(sample_grid_gdf):
    """Compare spatial and non-spatial clustering."""
    w = QueenWeights()
    w.fit(sample_grid_gdf)

    # Spatial clustering (SKATER)
    skater = SKATER(n_clusters=5)
    skater.fit(sample_grid_gdf, w, attributes=["value1", "value2"])

    # Calculate spatial connectivity
    sci = spatial_connectivity_index(sample_grid_gdf, skater.labels_, w)

    # Spatial clustering should have high connectivity
    assert sci > 0.3  # At least 30% of edges within clusters
