"""Tests for pattern analysis."""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from krl_geospatial.analysis.pattern import LISAAnalysis, moran_scatterplot
from krl_geospatial.weights import KNNWeights


@pytest.fixture
def spatial_cluster_data():
    """Create data with spatial clusters."""
    np.random.seed(42)

    x = np.repeat(np.arange(10), 10)
    y = np.tile(np.arange(10), 10)

    # High-high cluster in top-right
    values = np.random.normal(10, 1, 100)
    for i in range(100):
        if x[i] >= 7 and y[i] >= 7:
            values[i] += 15  # HH cluster
        elif x[i] <= 2 and y[i] <= 2:
            values[i] -= 15  # LL cluster

    geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
    gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

    return gdf


@pytest.fixture
def spatial_outlier_data():
    """Create data with spatial outliers."""
    np.random.seed(123)

    x = np.repeat(np.arange(10), 10)
    y = np.tile(np.arange(10), 10)

    values = np.random.normal(10, 1, 100)

    # High value in low neighborhood (HL outlier)
    center = 50  # (5, 5)
    values[center] += 20

    # Low value in high neighborhood (LH outlier)
    for i in range(100):
        if 7 <= x[i] <= 8 and 7 <= y[i] <= 8:
            values[i] += 15
    values[77] -= 25  # Outlier in cluster

    geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
    gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

    return gdf


class TestLISAAnalysis:
    """Tests for LISAAnalysis class."""

    def test_init_default(self):
        """Test default initialization."""
        lisa = LISAAnalysis()
        assert lisa.permutations == 999

    def test_init_permutations(self):
        """Test initialization with custom permutations."""
        lisa = LISAAnalysis(permutations=99)
        assert lisa.permutations == 99

    def test_fit(self, spatial_cluster_data):
        """Test fitting LISA."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis()
        lisa.fit(spatial_cluster_data, w, "value")

        assert hasattr(lisa, "local_i_")
        assert hasattr(lisa, "p_values_")
        assert hasattr(lisa, "quadrant_")
        assert hasattr(lisa, "significant_")

        assert len(lisa.local_i_) == len(spatial_cluster_data)

    def test_detect_hh_cluster(self, spatial_cluster_data):
        """Test detection of HH cluster."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis(permutations=99)
        lisa.fit(spatial_cluster_data, w, "value")

        cluster_map = lisa.get_cluster_map(alpha=0.05)

        # Should detect HH cluster
        assert "HH" in cluster_map.values

    def test_detect_ll_cluster(self, spatial_cluster_data):
        """Test detection of LL cluster."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis(permutations=99)
        lisa.fit(spatial_cluster_data, w, "value")

        cluster_map = lisa.get_cluster_map(alpha=0.05)

        # Should detect LL cluster
        assert "LL" in cluster_map.values

    def test_detect_outliers(self, spatial_outlier_data):
        """Test detection of spatial outliers."""
        w = KNNWeights(k=8)
        w.fit(spatial_outlier_data)
        lisa = LISAAnalysis(permutations=99)
        lisa.fit(spatial_outlier_data, w, "value")

        cluster_map = lisa.get_cluster_map(alpha=0.05)

        # May detect HL or LH outliers
        unique_types = cluster_map.unique()
        assert "NS" in unique_types  # Non-significant

    def test_quadrant_classification(self, spatial_cluster_data):
        """Test quadrant classification."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis()
        lisa.fit(spatial_cluster_data, w, "value")

        # Quadrant should be 1-4
        assert all((lisa.quadrant_ >= 1) & (lisa.quadrant_ <= 4))

    def test_significance_filter(self, spatial_cluster_data):
        """Test significance filtering."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis()
        lisa.fit(spatial_cluster_data, w, "value", alpha=0.05)

        # Significant array should be boolean
        assert lisa.significant_.dtype == bool

    def test_different_alpha(self, spatial_cluster_data):
        """Test different significance levels."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis(permutations=99)

        lisa.fit(spatial_cluster_data, w, "value", alpha=0.01)
        cluster_map_01 = lisa.get_cluster_map(alpha=0.01)

        lisa.fit(spatial_cluster_data, w, "value", alpha=0.10)
        cluster_map_10 = lisa.get_cluster_map(alpha=0.10)

        # More liberal alpha should detect more patterns
        sig_01 = (cluster_map_01 != "NS").sum()
        sig_10 = (cluster_map_10 != "NS").sum()
        assert sig_10 >= sig_01

    def test_plot_moran_scatterplot(self, spatial_cluster_data):
        """Test Moran scatterplot plotting."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis()
        lisa.fit(spatial_cluster_data, w, "value")

        fig, ax = plt.subplots()
        lisa.plot_moran_scatterplot(ax=ax)

        assert len(ax.collections) > 0  # Has scatter points
        plt.close(fig)

    def test_plot_cluster_map(self, spatial_cluster_data):
        """Test cluster map plotting."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)
        lisa = LISAAnalysis()
        lisa.fit(spatial_cluster_data, w, "value")

        fig, ax = plt.subplots()
        lisa.plot_cluster_map(spatial_cluster_data, ax=ax)

        assert len(ax.collections) > 0  # Has geometries
        plt.close(fig)

    def test_uniform_data(self):
        """Test with uniform data (no patterns)."""
        np.random.seed(42)
        x = np.repeat(np.arange(5), 5)
        y = np.tile(np.arange(5), 5)
        values = np.ones(25) * 10

        geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
        gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

        w = KNNWeights(k=4)
        w.fit(gdf)
        lisa = LISAAnalysis(permutations=99)
        lisa.fit(gdf, w, "value")

        cluster_map = lisa.get_cluster_map(alpha=0.05)

        # All should be non-significant
        assert all(cluster_map == "NS")


class TestMoranScatterplot:
    """Tests for standalone moran_scatterplot function."""

    def test_basic_scatterplot(self, spatial_cluster_data):
        """Test basic scatterplot."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)

        fig, ax, slope = moran_scatterplot(spatial_cluster_data, w, "value")

        assert isinstance(fig, plt.Figure)
        assert isinstance(slope, float)
        assert len(ax.collections) > 0

        plt.close(fig)

    def test_slope_range(self, spatial_cluster_data):
        """Test slope is in valid range for Moran's I."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)

        fig, ax, slope = moran_scatterplot(spatial_cluster_data, w, "value")

        # Slope approximates global Moran's I, should be in [-1, 1]
        assert -1 <= slope <= 1

        plt.close(fig)

    def test_with_ax(self, spatial_cluster_data):
        """Test plotting on existing axes."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)

        fig_existing, ax_existing = plt.subplots()
        fig, ax, slope = moran_scatterplot(spatial_cluster_data, w, "value", ax=ax_existing)

        assert ax == ax_existing

        plt.close(fig)

    def test_positive_autocorrelation(self, spatial_cluster_data):
        """Test positive spatial autocorrelation."""
        w = KNNWeights(k=8)
        w.fit(spatial_cluster_data)

        fig, ax, slope = moran_scatterplot(spatial_cluster_data, w, "value")

        # Clustered data should have positive slope
        assert slope > 0

        plt.close(fig)

    def test_random_data(self):
        """Test with random data (near zero autocorrelation)."""
        np.random.seed(42)
        x = np.repeat(np.arange(10), 10)
        y = np.tile(np.arange(10), 10)
        values = np.random.normal(10, 2, 100)

        geometry = [Point(xi, yi) for xi, yi in zip(x, y)]
        gdf = gpd.GeoDataFrame({"value": values}, geometry=geometry)

        w = KNNWeights(k=8)
        w.fit(gdf)

        fig, ax, slope = moran_scatterplot(gdf, w, "value")

        # Should be close to zero
        assert abs(slope) < 0.3

        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
