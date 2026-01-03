"""Tests for hot spot analysis."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from krl_geospatial.analysis.hotspot import GetisOrdGiStar, spatial_scan
from krl_geospatial.weights import KNNWeights


@pytest.fixture
def hot_spot_data():
    """Create synthetic data with hot spot."""
    np.random.seed(42)

    # Create grid
    x = np.repeat(np.arange(10), 10)
    y = np.tile(np.arange(10), 10)

    # Hot spot in center
    values = np.random.normal(10, 2, 100)
    for i in range(100):
        if 4 <= x[i] <= 6 and 4 <= y[i] <= 6:
            values[i] += 20  # Hot spot

    geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
    gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

    return gdf


@pytest.fixture
def cold_spot_data():
    """Create synthetic data with cold spot."""
    np.random.seed(123)

    x = np.repeat(np.arange(10), 10)
    y = np.tile(np.arange(10), 10)

    values = np.random.normal(20, 2, 100)
    for i in range(100):
        if 2 <= x[i] <= 4 and 2 <= y[i] <= 4:
            values[i] -= 15  # Cold spot

    geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
    gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

    return gdf


class TestGetisOrdGiStar:
    """Tests for GetisOrdGiStar class."""

    def test_init_default(self):
        """Test default initialization."""
        gi = GetisOrdGiStar()
        assert gi.star is True
        assert gi.permutations is None
        assert gi.correction == "fdr"

    def test_init_permutations(self):
        """Test initialization with permutations."""
        gi = GetisOrdGiStar(permutations=999, correction="bonferroni")
        assert gi.permutations == 999
        assert gi.correction == "bonferroni"

    def test_fit_hot_spot(self, hot_spot_data):
        """Test hot spot detection."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar()
        gi.fit(hot_spot_data, w, "value")

        assert hasattr(gi, "gi_values_")
        assert hasattr(gi, "z_scores_")
        assert hasattr(gi, "p_values_")
        assert len(gi.gi_values_) == len(hot_spot_data)

        # Should detect hot spots in center
        hot_spots = gi.hot_spots_
        assert hot_spots.any()

    def test_fit_cold_spot(self, cold_spot_data):
        """Test cold spot detection."""
        w = KNNWeights(k=8)
        w.fit(cold_spot_data)
        gi = GetisOrdGiStar()
        gi.fit(cold_spot_data, w, "value")

        # Should detect cold spots
        cold_spots = gi.cold_spots_
        assert cold_spots.any()

    def test_no_star(self, hot_spot_data):
        """Test Gi without self-inclusion."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar(star=False)
        gi.fit(hot_spot_data, w, "value")

        assert hasattr(gi, "gi_values_")

    def test_permutation_inference(self, hot_spot_data):
        """Test permutation-based inference."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar(permutations=99)
        gi.fit(hot_spot_data, w, "value")

        assert hasattr(gi, "p_values_")
        assert all(gi.p_values_ >= 0) and all(gi.p_values_ <= 1)

    def test_bonferroni_correction(self, hot_spot_data):
        """Test Bonferroni correction."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar(correction="bonferroni")
        gi.fit(hot_spot_data, w, "value", alpha=0.05)

        # Bonferroni is more conservative
        assert hasattr(gi, "p_values_")

    def test_fdr_correction(self, hot_spot_data):
        """Test FDR correction."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar(correction="fdr")
        gi.fit(hot_spot_data, w, "value", alpha=0.05)

        assert hasattr(gi, "p_values_")

    def test_get_cluster_map(self, hot_spot_data):
        """Test cluster map generation."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar()
        gi.fit(hot_spot_data, w, "value")

        cluster_map = gi.get_cluster_map(alpha=0.05)
        assert len(cluster_map) == len(hot_spot_data)

        # Should have hot spots (1), cold spots (-1), and non-significant (0)
        unique_values = np.unique(cluster_map)
        assert set(unique_values).issubset({-1, 0, 1})

    def test_different_alpha(self, hot_spot_data):
        """Test different significance levels."""
        w = KNNWeights(k=8)
        w.fit(hot_spot_data)
        gi = GetisOrdGiStar()

        gi.fit(hot_spot_data, w, "value", alpha=0.01)
        cluster_map_01 = gi.get_cluster_map(alpha=0.01)

        gi.fit(hot_spot_data, w, "value", alpha=0.10)
        cluster_map_10 = gi.get_cluster_map(alpha=0.10)

        # More liberal alpha should detect more spots
        assert (cluster_map_10 != 0).sum() >= (cluster_map_01 != 0).sum()

    def test_uniform_data(self):
        """Test with uniform data (no hot spots)."""
        np.random.seed(42)
        x = np.repeat(np.arange(5), 5)
        y = np.tile(np.arange(5), 5)
        values = np.ones(25) * 10  # Constant

        geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
        gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

        w = KNNWeights(k=8)
        w.fit(gdf)
        gi = GetisOrdGiStar()
        gi.fit(gdf, w, "value")

        # Should have no significant hot or cold spots
        assert not gi.hot_spots_.any()
        assert not gi.cold_spots_.any()


class TestSpatialScan:
    """Tests for spatial scan statistic."""

    def test_basic_scan(self, hot_spot_data):
        """Test basic spatial scan."""
        clusters = spatial_scan(hot_spot_data, "value", max_radius=3.0, n_circles=5, alpha=0.05)

        assert isinstance(clusters, list)
        if len(clusters) > 0:
            cluster = clusters[0]
            assert "center_idx" in cluster
            assert "radius" in cluster
            assert "llr" in cluster
            assert "p_value" in cluster

    def test_detect_hot_cluster(self, hot_spot_data):
        """Test detection of hot spot cluster."""
        clusters = spatial_scan(hot_spot_data, "value", max_radius=4.0, n_circles=10, alpha=0.05)

        # Should detect at least one cluster
        assert len(clusters) > 0

        # Cluster should be in center region
        if len(clusters) > 0:
            cluster = clusters[0]
            center_x = hot_spot_data.geometry.x.iloc[cluster["center_idx"]]
            center_y = hot_spot_data.geometry.y.iloc[cluster["center_idx"]]

            # Center should be around (5, 5)
            assert 3 <= center_x <= 7
            assert 3 <= center_y <= 7

    def test_no_clusters(self):
        """Test with uniform data (no clusters)."""
        np.random.seed(42)
        x = np.repeat(np.arange(5), 5)
        y = np.tile(np.arange(5), 5)
        values = np.random.normal(10, 0.5, 25)

        geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
        gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

        clusters = spatial_scan(gdf, "value", max_radius=2.0, n_circles=3, alpha=0.01)

        # Should detect few or no clusters
        assert len(clusters) <= 1

    def test_different_radii(self, hot_spot_data):
        """Test with different maximum radii."""
        clusters_small = spatial_scan(hot_spot_data, "value", max_radius=2.0, n_circles=5)

        clusters_large = spatial_scan(hot_spot_data, "value", max_radius=6.0, n_circles=5)

        # Larger radius may detect more/larger clusters
        assert isinstance(clusters_small, list)
        assert isinstance(clusters_large, list)

    def test_llr_positive(self, hot_spot_data):
        """Test that detected clusters have positive LLR."""
        clusters = spatial_scan(hot_spot_data, "value", max_radius=4.0, n_circles=10, alpha=0.05)

        for cluster in clusters:
            assert cluster["llr"] > 0

    def test_pvalue_range(self, hot_spot_data):
        """Test that p-values are in valid range."""
        clusters = spatial_scan(hot_spot_data, "value", max_radius=4.0, n_circles=10, alpha=0.05)

        for cluster in clusters:
            assert 0 <= cluster["p_value"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
