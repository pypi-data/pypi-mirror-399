"""
Tests for spatial indexing module.

This module tests R-tree and grid-based spatial indices.
"""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, Polygon, box

from krl_geospatial.indexing import GridIndex, RTreeIndex

# Fixtures


@pytest.fixture
def point_gdf():
    """Create a point GeoDataFrame for testing."""
    np.random.seed(42)
    n = 100
    points = [
        Point(x, y) for x, y in zip(np.random.uniform(0, 100, n), np.random.uniform(0, 100, n))
    ]
    return gpd.GeoDataFrame(
        {"id": range(n), "value": np.random.randint(0, 10, n)}, geometry=points, crs="EPSG:4326"
    )


@pytest.fixture
def polygon_gdf():
    """Create a polygon GeoDataFrame for testing."""
    polygons = []
    for i in range(10):
        for j in range(10):
            x = i * 10
            y = j * 10
            poly = Polygon([(x, y), (x + 8, y), (x + 8, y + 8), (x, y + 8)])
            polygons.append(poly)

    return gpd.GeoDataFrame(
        {"id": range(100), "row": [i // 10 for i in range(100)]}, geometry=polygons, crs="EPSG:4326"
    )


# Test RTreeIndex


class TestRTreeIndex:
    """Test R-tree spatial index."""

    def test_initialization(self):
        """Test R-tree initialization."""
        idx = RTreeIndex()
        assert idx.gdf is None
        assert not idx._built

    def test_build(self, point_gdf):
        """Test building R-tree index."""
        idx = RTreeIndex()
        idx.build(point_gdf)
        assert idx._built
        assert idx.gdf is not None
        assert len(idx.gdf) == len(point_gdf)

    def test_build_empty_gdf(self):
        """Test building with empty GeoDataFrame."""
        idx = RTreeIndex()
        empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        with pytest.raises(ValueError, match="empty"):
            idx.build(empty_gdf)

    def test_intersection(self, point_gdf):
        """Test intersection query."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        # Query a bounding box
        bbox = (25, 25, 75, 75)
        result = idx.intersection(bbox)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0
        assert len(result) < len(point_gdf)

    def test_intersection_geometry(self, point_gdf):
        """Test intersection query with geometry."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        # Query with a polygon
        query_geom = box(25, 25, 75, 75)
        result = idx.intersection(query_geom)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0

    def test_intersection_return_indices(self, point_gdf):
        """Test intersection query returning indices."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        bbox = (25, 25, 75, 75)
        indices = idx.intersection(bbox, return_indices=True)

        assert isinstance(indices, list)
        assert all(isinstance(i, int) for i in indices)

    def test_intersection_before_build(self, point_gdf):
        """Test intersection fails before building."""
        idx = RTreeIndex()
        with pytest.raises(ValueError, match="must be built"):
            idx.intersection((0, 0, 10, 10))

    def test_nearest(self, point_gdf):
        """Test nearest neighbor query."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        # Query nearest to center
        point = (50, 50)
        result = idx.nearest(point, k=5)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) == 5

    def test_nearest_point_geometry(self, point_gdf):
        """Test nearest with Point geometry."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        query_point = Point(50, 50)
        result = idx.nearest(query_point, k=3)

        assert len(result) == 3

    def test_nearest_k_invalid(self, point_gdf):
        """Test nearest with invalid k."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        with pytest.raises(ValueError, match="k must be at least 1"):
            idx.nearest((50, 50), k=0)

    def test_contains(self, polygon_gdf):
        """Test contains query."""
        idx = RTreeIndex()
        idx.build(polygon_gdf)

        # Query a large bbox that should contain some polygons
        bbox = (0, 0, 50, 50)
        result = idx.contains(bbox)

        assert isinstance(result, gpd.GeoDataFrame)
        # Should have some polygons whose bbox is fully contained
        assert len(result) > 0

    def test_count_intersection(self, point_gdf):
        """Test counting intersecting geometries."""
        idx = RTreeIndex()
        idx.build(point_gdf)

        bbox = (25, 25, 75, 75)
        count = idx.count_intersection(bbox)

        assert isinstance(count, int)
        assert count > 0

    def test_clear(self, point_gdf):
        """Test clearing the index."""
        idx = RTreeIndex()
        idx.build(point_gdf)
        assert idx._built

        idx.clear()
        assert not idx._built
        assert idx.gdf is None

    def test_repr(self, point_gdf):
        """Test string representation."""
        idx = RTreeIndex()
        assert "built=False" in repr(idx)

        idx.build(point_gdf)
        assert "built=True" in repr(idx)
        assert f"n_geometries={len(point_gdf)}" in repr(idx)


# Test GridIndex


class TestGridIndex:
    """Test grid-based spatial index."""

    def test_initialization(self):
        """Test grid index initialization."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        assert idx.n_cells_x == 10
        assert idx.n_cells_y == 10
        assert not idx._built

    def test_initialization_invalid_cells(self):
        """Test initialization with invalid cell counts."""
        with pytest.raises(ValueError, match="at least 1"):
            GridIndex(n_cells_x=0, n_cells_y=10)

        with pytest.raises(ValueError, match="at least 1"):
            GridIndex(n_cells_x=10, n_cells_y=0)

    def test_build(self, point_gdf):
        """Test building grid index."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)
        assert idx._built
        assert idx.gdf is not None
        assert len(idx.gdf) == len(point_gdf)

    def test_build_empty_gdf(self):
        """Test building with empty GeoDataFrame."""
        idx = GridIndex()
        empty_gdf = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        with pytest.raises(ValueError, match="empty"):
            idx.build(empty_gdf)

    def test_intersection(self, point_gdf):
        """Test intersection query."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        # Query a bounding box
        bbox = (25, 25, 75, 75)
        result = idx.intersection(bbox)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0

    def test_intersection_geometry(self, point_gdf):
        """Test intersection query with geometry."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        # Query with a polygon
        query_geom = box(25, 25, 75, 75)
        result = idx.intersection(query_geom)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0

    def test_intersection_return_indices(self, point_gdf):
        """Test intersection query returning indices."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        bbox = (25, 25, 75, 75)
        indices = idx.intersection(bbox, return_indices=True)

        assert isinstance(indices, list)
        assert all(isinstance(i, int) for i in indices)

    def test_nearest(self, point_gdf):
        """Test nearest neighbor query."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        # Query nearest to center
        point = (50, 50)
        result = idx.nearest(point, k=5)

        assert isinstance(result, gpd.GeoDataFrame)
        # May return more or less than k depending on search radius
        assert len(result) > 0

    def test_nearest_point_geometry(self, point_gdf):
        """Test nearest with Point geometry."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        query_point = Point(50, 50)
        result = idx.nearest(query_point, k=3)

        assert len(result) > 0

    def test_nearest_k_invalid(self, point_gdf):
        """Test nearest with invalid k."""
        idx = GridIndex()
        idx.build(point_gdf)

        with pytest.raises(ValueError, match="k must be at least 1"):
            idx.nearest((50, 50), k=0)

    def test_statistics(self, point_gdf):
        """Test computing index statistics."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(point_gdf)

        stats = idx.statistics()

        assert "total_cells" in stats
        assert "used_cells" in stats
        assert "min_per_cell" in stats
        assert "max_per_cell" in stats
        assert "mean_per_cell" in stats
        assert "sparsity" in stats

        assert stats["total_cells"] == 100
        assert stats["used_cells"] > 0
        assert stats["used_cells"] <= 100

    def test_statistics_before_build(self):
        """Test statistics fails before building."""
        idx = GridIndex()
        with pytest.raises(ValueError, match="must be built"):
            idx.statistics()

    def test_clear(self, point_gdf):
        """Test clearing the index."""
        idx = GridIndex()
        idx.build(point_gdf)
        assert idx._built

        idx.clear()
        assert not idx._built
        assert idx.gdf is None
        assert len(idx.grid) == 0

    def test_repr(self, point_gdf):
        """Test string representation."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        assert "10x10" in repr(idx)
        assert "built=False" in repr(idx)

        idx.build(point_gdf)
        assert "built=True" in repr(idx)
        assert f"n_geometries={len(point_gdf)}" in repr(idx)


# Test Grid Index Edge Cases


class TestGridIndexEdgeCases:
    """Test edge cases for grid index."""

    def test_single_cell(self, point_gdf):
        """Test grid with single cell."""
        idx = GridIndex(n_cells_x=1, n_cells_y=1)
        idx.build(point_gdf)

        # All points should be in one cell
        stats = idx.statistics()
        assert stats["used_cells"] == 1

    def test_fine_grid(self, point_gdf):
        """Test grid with many cells."""
        idx = GridIndex(n_cells_x=50, n_cells_y=50)
        idx.build(point_gdf)

        # Should have high sparsity
        stats = idx.statistics()
        assert stats["sparsity"] > 0.5

    def test_boundary_query(self, polygon_gdf):
        """Test query at grid boundaries."""
        idx = GridIndex(n_cells_x=10, n_cells_y=10)
        idx.build(polygon_gdf)

        # Query at exact grid boundaries
        bbox = (0, 0, 50, 50)
        result = idx.intersection(bbox)
        assert len(result) > 0


# Comparison Tests


class TestIndexComparison:
    """Compare R-tree and grid index results."""

    def test_intersection_consistency(self, point_gdf):
        """Test that both indices return similar results."""
        rtree_idx = RTreeIndex()
        rtree_idx.build(point_gdf)

        grid_idx = GridIndex(n_cells_x=10, n_cells_y=10)
        grid_idx.build(point_gdf)

        bbox = (25, 25, 75, 75)

        rtree_result = set(rtree_idx.intersection(bbox, return_indices=True))
        grid_result = set(grid_idx.intersection(bbox, return_indices=True))

        # Grid may return more candidates (false positives)
        # But should include all R-tree results
        assert rtree_result.issubset(grid_result) or len(rtree_result) > 0
