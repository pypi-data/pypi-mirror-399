"""
Tests for spatial weights module.

This module tests all spatial weight classes including contiguity-based,
distance-based, and kernel weights.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from krl_geospatial.weights import (
    DistanceBandWeights,
    EpanechnikovWeights,
    GaussianWeights,
    InverseDistanceWeights,
    KernelWeights,
    KNNWeights,
    QueenWeights,
    RookWeights,
    SpatialWeights,
    TriangularWeights,
)

# Fixtures for test data


@pytest.fixture
def point_gdf():
    """Create a simple point GeoDataFrame for testing."""
    points = [
        Point(0, 0),
        Point(1, 0),
        Point(0, 1),
        Point(1, 1),
        Point(2, 2),
    ]
    return gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")


@pytest.fixture
def polygon_gdf():
    """Create a simple polygon GeoDataFrame for testing."""
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),  # Square 1
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),  # Square 2 (adjacent to 1)
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),  # Square 3 (adjacent to 1)
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),  # Square 4 (adjacent to 2 and 3)
        Polygon([(3, 3), (4, 3), (4, 4), (3, 4)]),  # Square 5 (isolated)
    ]
    return gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")


# Test Base SpatialWeights Class


class ConcreteSpatialWeights(SpatialWeights):
    """Concrete implementation for testing abstract base class."""

    def fit(self, gdf):
        self._validate_geodataframe(gdf)
        self.n = len(gdf)
        # Simple: connect each to next
        self.neighbors = {i: [i + 1] if i < self.n - 1 else [] for i in range(self.n)}
        self.weights = {i: [1.0] if i < self.n - 1 else [] for i in range(self.n)}
        self._fitted = True
        return self


class TestSpatialWeightsBase:
    """Test the abstract SpatialWeights base class."""

    def test_initialization(self):
        """Test base class initialization."""
        w = ConcreteSpatialWeights()
        assert w.n == 0
        assert w.weights == {}
        assert w.neighbors == {}
        assert not w.is_standardized
        assert not w._fitted

    def test_validate_geodataframe_valid(self, point_gdf):
        """Test validation with valid GeoDataFrame."""
        w = ConcreteSpatialWeights()
        w._validate_geodataframe(point_gdf)  # Should not raise

    def test_validate_geodataframe_not_gdf(self):
        """Test validation fails with non-GeoDataFrame."""
        w = ConcreteSpatialWeights()
        with pytest.raises(ValueError, match="must be a GeoDataFrame"):
            w._validate_geodataframe(pd.DataFrame({"a": [1, 2, 3]}))

    def test_validate_geodataframe_empty(self):
        """Test validation fails with empty GeoDataFrame."""
        w = ConcreteSpatialWeights()
        empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        with pytest.raises(ValueError, match="cannot be empty"):
            w._validate_geodataframe(empty_gdf)

    def test_validate_geodataframe_null_geometries(self):
        """Test validation fails with null geometries."""
        w = ConcreteSpatialWeights()
        gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), None], crs="EPSG:4326")
        with pytest.raises(ValueError, match="null geometries"):
            w._validate_geodataframe(gdf)

    def test_standardize_before_fit(self):
        """Test standardize fails before fitting."""
        w = ConcreteSpatialWeights()
        with pytest.raises(ValueError, match="must be fitted before standardization"):
            w.standardize()

    def test_standardize_inplace(self, point_gdf):
        """Test in-place standardization."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        result = w.standardize(inplace=True)
        assert result is None
        assert w.is_standardized
        # Check weights sum to 1
        for i in w.neighbors:
            if w.neighbors[i]:
                assert np.isclose(sum(w.weights[i]), 1.0)

    def test_standardize_copy(self, point_gdf):
        """Test standardization with copy."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        w_std = w.standardize(inplace=False)
        assert not w.is_standardized
        assert w_std.is_standardized

    def test_to_sparse(self, point_gdf):
        """Test conversion to sparse matrix."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        sparse_matrix = w.to_sparse()
        assert sparse_matrix.shape == (w.n, w.n)
        assert sparse_matrix.nnz == w.n - 1  # n-1 connections

    def test_to_dense(self, point_gdf):
        """Test conversion to dense matrix."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        dense_matrix = w.to_dense()
        assert dense_matrix.shape == (w.n, w.n)
        assert np.sum(dense_matrix > 0) == w.n - 1

    def test_cardinality(self, point_gdf):
        """Test cardinality statistics."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        card = w.cardinality()
        assert card["min"] == 0  # Last observation
        assert card["max"] == 1
        assert card["mean"] == 0.8  # 4/5
        assert len(card["islands"]) == 1  # Last observation

    def test_symmetry_check(self, point_gdf):
        """Test symmetry check."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        is_symmetric, asymmetric = w.symmetry_check()
        assert not is_symmetric  # Chain is not symmetric
        assert len(asymmetric) > 0

    def test_summary(self, point_gdf):
        """Test summary generation."""
        w = ConcreteSpatialWeights().fit(point_gdf)
        summary = w.summary()
        assert isinstance(summary, pd.DataFrame)
        assert "Property" in summary.columns
        assert "Value" in summary.columns


# Test Queen Contiguity Weights


class TestQueenWeights:
    """Test Queen contiguity weights."""

    def test_initialization(self):
        """Test Queen weights initialization."""
        w = QueenWeights(order=1)
        assert w.order == 1
        assert not w._fitted

    def test_initialization_invalid_order(self):
        """Test initialization with invalid order."""
        with pytest.raises(ValueError, match="Order must be at least 1"):
            QueenWeights(order=0)

    def test_fit(self, polygon_gdf):
        """Test fitting Queen weights."""
        w = QueenWeights().fit(polygon_gdf)
        assert w._fitted
        assert w.n == len(polygon_gdf)
        # Square 0 should have 3 neighbors (1, 2, 3 - shares vertex with all)
        assert len(w.neighbors[0]) == 3

    def test_fit_non_polygons(self, point_gdf):
        """Test fitting fails with non-polygon geometries."""
        w = QueenWeights()
        with pytest.raises(TypeError, match="requires polygon geometries"):
            w.fit(point_gdf)

    def test_higher_order(self, polygon_gdf):
        """Test higher-order contiguity."""
        # Higher-order contiguity logs a warning but uses first-order
        import warnings

        with warnings.catch_warnings(record=True):
            w = QueenWeights(order=2).fit(polygon_gdf)
        assert w._fitted
        assert w.n == len(polygon_gdf)

    def test_repr(self, polygon_gdf):
        """Test string representation."""
        w = QueenWeights(order=1)
        assert "fitted=False" in repr(w)
        w.fit(polygon_gdf)
        assert "fitted=False" not in repr(w)
        assert f"n={w.n}" in repr(w)


# Test Rook Contiguity Weights


class TestRookWeights:
    """Test Rook contiguity weights."""

    def test_initialization(self):
        """Test Rook weights initialization."""
        w = RookWeights(order=1)
        assert w.order == 1
        assert not w._fitted

    def test_fit(self, polygon_gdf):
        """Test fitting Rook weights."""
        w = RookWeights().fit(polygon_gdf)
        assert w._fitted
        assert w.n == len(polygon_gdf)

    def test_fit_non_polygons(self, point_gdf):
        """Test fitting fails with non-polygon geometries."""
        w = RookWeights()
        with pytest.raises(TypeError, match="requires polygon geometries"):
            w.fit(point_gdf)

    def test_rook_vs_queen(self, polygon_gdf):
        """Test that Rook may have fewer neighbors than Queen."""
        w_queen = QueenWeights().fit(polygon_gdf)
        w_rook = RookWeights().fit(polygon_gdf)

        # For our test data, they should be similar but Rook could be more restrictive
        queen_total = sum(len(neighbors) for neighbors in w_queen.neighbors.values())
        rook_total = sum(len(neighbors) for neighbors in w_rook.neighbors.values())
        assert rook_total <= queen_total


# Test KNN Weights


class TestKNNWeights:
    """Test K-Nearest Neighbors weights."""

    def test_initialization(self):
        """Test KNN weights initialization."""
        w = KNNWeights(k=3)
        assert w.k == 3
        assert w.p == 2.0
        assert not w._fitted

    def test_initialization_invalid_k(self):
        """Test initialization with invalid k."""
        with pytest.raises(ValueError, match="k must be at least 1"):
            KNNWeights(k=0)

    def test_initialization_invalid_p(self):
        """Test initialization with invalid p."""
        with pytest.raises(ValueError, match="p must be positive"):
            KNNWeights(k=3, p=0)

    def test_fit(self, point_gdf):
        """Test fitting KNN weights."""
        w = KNNWeights(k=2).fit(point_gdf)
        assert w._fitted
        assert w.n == len(point_gdf)
        # Each observation should have exactly k neighbors
        for neighbors in w.neighbors.values():
            assert len(neighbors) == 2

    def test_fit_k_too_large(self, point_gdf):
        """Test fitting fails when k >= n."""
        w = KNNWeights(k=10)
        with pytest.raises(ValueError, match="k.*must be less than"):
            w.fit(point_gdf)

    def test_manhattan_distance(self, point_gdf):
        """Test KNN with Manhattan distance (p=1)."""
        w = KNNWeights(k=2, p=1.0).fit(point_gdf)
        assert w._fitted
        assert w.p == 1.0


# Test Distance Band Weights


class TestDistanceBandWeights:
    """Test distance band weights."""

    def test_initialization(self):
        """Test distance band weights initialization."""
        w = DistanceBandWeights(threshold=1.0)
        assert w.threshold == 1.0
        assert w.binary
        assert not w._fitted

    def test_initialization_invalid_threshold(self):
        """Test initialization with invalid threshold."""
        with pytest.raises(ValueError, match="threshold must be positive"):
            DistanceBandWeights(threshold=0)

    def test_fit(self, point_gdf):
        """Test fitting distance band weights."""
        w = DistanceBandWeights(threshold=1.5).fit(point_gdf)
        assert w._fitted
        assert w.n == len(point_gdf)

    def test_binary_weights(self, point_gdf):
        """Test binary distance weights."""
        w = DistanceBandWeights(threshold=1.5, binary=True).fit(point_gdf)
        # All weights should be 1.0 for neighbors
        for weights in w.weights.values():
            assert all(np.isclose(weight, 1.0) for weight in weights)

    def test_inverse_distance_weights(self, point_gdf):
        """Test inverse distance weights via binary=False."""
        w = DistanceBandWeights(threshold=1.5, binary=False).fit(point_gdf)
        # Weights should vary based on distance
        for weights in w.weights.values():
            if len(weights) > 1:
                # Should have different weights
                assert not all(np.isclose(weights[0], w) for w in weights)


# Test Inverse Distance Weights


class TestInverseDistanceWeights:
    """Test inverse distance weights."""

    def test_initialization(self):
        """Test inverse distance weights initialization."""
        w = InverseDistanceWeights(alpha=1.0)
        assert w.alpha == 1.0
        assert w.threshold is None
        assert not w._fitted

    def test_initialization_invalid_alpha(self):
        """Test initialization with invalid alpha."""
        with pytest.raises(ValueError, match="alpha must be positive"):
            InverseDistanceWeights(alpha=0)

    def test_fit(self, point_gdf):
        """Test fitting inverse distance weights."""
        w = InverseDistanceWeights(alpha=1.0, threshold=2.0).fit(point_gdf)
        assert w._fitted
        assert w.n == len(point_gdf)

    def test_no_threshold(self, point_gdf):
        """Test inverse distance with no threshold (all pairs)."""
        w = InverseDistanceWeights(alpha=1.0, threshold=None).fit(point_gdf)
        # Each observation should have n-1 neighbors
        for neighbors in w.neighbors.values():
            assert len(neighbors) == len(point_gdf) - 1

    def test_distance_decay(self, point_gdf):
        """Test that weights decay with distance."""
        w = InverseDistanceWeights(alpha=1.0, threshold=None).fit(point_gdf)
        # Closer neighbors should have higher weights
        # Point 0 is at (0,0), point 1 at (1,0), point 4 at (2,2)
        # Weight to point 1 should be higher than to point 4
        idx_1 = w.neighbors[0].index(1)
        idx_4 = w.neighbors[0].index(4)
        assert w.weights[0][idx_1] > w.weights[0][idx_4]


# Test Kernel Weights


class TestKernelWeights:
    """Test kernel weights."""

    def test_initialization(self):
        """Test kernel weights initialization."""
        w = KernelWeights(kernel="gaussian", bandwidth=1.0)
        assert w.kernel == "gaussian"
        assert w.bandwidth == 1.0
        assert w.fixed
        assert not w._fitted

    def test_initialization_invalid_kernel(self):
        """Test initialization with invalid kernel."""
        with pytest.raises(ValueError, match="kernel must be one of"):
            KernelWeights(kernel="invalid")

    def test_initialization_adaptive_without_k(self):
        """Test initialization fails for adaptive without k."""
        with pytest.raises(ValueError, match="k must be specified"):
            KernelWeights(kernel="gaussian", fixed=False)

    def test_fit_fixed(self, point_gdf):
        """Test fitting with fixed bandwidth."""
        w = KernelWeights(kernel="gaussian", bandwidth=1.0, fixed=True).fit(point_gdf)
        assert w._fitted
        assert w.n == len(point_gdf)

    def test_fit_adaptive(self, point_gdf):
        """Test fitting with adaptive bandwidth."""
        w = KernelWeights(kernel="gaussian", fixed=False, k=3).fit(point_gdf)
        assert w._fitted
        assert not w.fixed

    def test_get_bandwidth(self, point_gdf):
        """Test getting bandwidth after fitting."""
        w = KernelWeights(kernel="gaussian", bandwidth=1.0).fit(point_gdf)
        bw = w.get_bandwidth()
        assert bw is not None


# Test Convenience Kernel Classes


class TestGaussianWeights:
    """Test Gaussian kernel weights convenience class."""

    def test_initialization(self):
        """Test Gaussian weights initialization."""
        w = GaussianWeights(bandwidth=1.0)
        assert w.kernel == "gaussian"
        assert w.bandwidth == 1.0

    def test_fit(self, point_gdf):
        """Test fitting Gaussian weights."""
        w = GaussianWeights(bandwidth=1.0).fit(point_gdf)
        assert w._fitted


class TestEpanechnikovWeights:
    """Test Epanechnikov kernel weights convenience class."""

    def test_initialization(self):
        """Test Epanechnikov weights initialization."""
        w = EpanechnikovWeights(bandwidth=1.0)
        assert w.kernel == "quadratic"
        assert w.bandwidth == 1.0

    def test_fit(self, point_gdf):
        """Test fitting Epanechnikov weights."""
        w = EpanechnikovWeights(bandwidth=1.0).fit(point_gdf)
        assert w._fitted


class TestTriangularWeights:
    """Test Triangular kernel weights convenience class."""

    def test_initialization(self):
        """Test Triangular weights initialization."""
        w = TriangularWeights(bandwidth=1.0)
        assert w.kernel == "triangular"
        assert w.bandwidth == 1.0

    def test_fit(self, point_gdf):
        """Test fitting Triangular weights."""
        w = TriangularWeights(bandwidth=1.0).fit(point_gdf)
        assert w._fitted
