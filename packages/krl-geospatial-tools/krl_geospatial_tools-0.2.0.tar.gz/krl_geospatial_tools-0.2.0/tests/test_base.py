# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""Tests for core base classes."""

import numpy as np
import pandas as pd
import pytest
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon

from krl_geospatial.core import (
    BaseGeospatialAnalyzer,
    SpatialDataFrame,
    SpatialResult,
    create_geodataframe,
)


class ConcreteAnalyzer(BaseGeospatialAnalyzer):
    """Concrete implementation for testing."""

    def fit(self, data: GeoDataFrame, **kwargs):
        """Fit implementation."""
        self._data = self._validate_geodataframe(data)
        self._fitted = True
        return self

    def analyze(self, **kwargs):
        """Analyze implementation."""
        self._check_fitted()
        return SpatialResult(
            method="test",
            statistic=1.0,
            p_value=0.05,
            n_obs=len(self._data),
        )


class TestBaseGeospatialAnalyzer:
    """Tests for BaseGeospatialAnalyzer."""

    @pytest.fixture
    def sample_geodataframe(self):
        """Create sample GeoDataFrame."""
        data = {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
            "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
        }
        return GeoDataFrame(data, crs="EPSG:4326")

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = ConcreteAnalyzer()
        assert analyzer.crs == "EPSG:4326"
        assert analyzer.validate_geometries is True
        assert analyzer._fitted is False

    def test_fit_validate(self, sample_geodataframe):
        """Test fit with validation."""
        analyzer = ConcreteAnalyzer()
        result = analyzer.fit(sample_geodataframe)
        assert result is analyzer  # Method chaining
        assert analyzer._fitted is True

    def test_analyze_before_fit(self):
        """Test analyze before fit raises error."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(RuntimeError, match="must be fitted before use"):
            analyzer.analyze()

    def test_analyze_after_fit(self, sample_geodataframe):
        """Test analyze after fit."""
        analyzer = ConcreteAnalyzer()
        analyzer.fit(sample_geodataframe)
        result = analyzer.analyze()
        assert isinstance(result, SpatialResult)
        assert result.method == "test"
        assert result.n_obs == 3

    def test_validate_geodataframe_not_geodataframe(self):
        """Test validation with non-GeoDataFrame raises error."""
        analyzer = ConcreteAnalyzer()
        df = pd.DataFrame({"a": [1, 2, 3]})
        with pytest.raises(TypeError, match="Expected GeoDataFrame"):
            analyzer._validate_geodataframe(df)

    def test_validate_geodataframe_missing_columns(self, sample_geodataframe):
        """Test validation with missing required columns."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer._validate_geodataframe(sample_geodataframe, required_cols=["missing_col"])

    def test_validate_geodataframe_no_crs(self):
        """Test validation with no CRS."""
        data = {"geometry": [Point(0, 0), Point(1, 1)]}
        gdf = GeoDataFrame(data)  # No CRS
        analyzer = ConcreteAnalyzer()
        result = analyzer._validate_geodataframe(gdf)
        assert result.crs is not None

    def test_validate_geodataframe_reproject(self, sample_geodataframe):
        """Test validation reprojects to target CRS."""
        analyzer = ConcreteAnalyzer(crs="EPSG:3857")
        result = analyzer._validate_geodataframe(sample_geodataframe)
        assert result.crs.to_string() == "EPSG:3857"

    def test_validate_geodataframe_invalid_geometries(self):
        """Test validation repairs invalid geometries."""
        # Create invalid polygon (self-intersecting)
        invalid_poly = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
        data = {"geometry": [invalid_poly]}
        gdf = GeoDataFrame(data, crs="EPSG:4326")

        analyzer = ConcreteAnalyzer()
        result = analyzer._validate_geodataframe(gdf)
        # After repair, should be valid
        assert result.geometry.is_valid.all()


class TestSpatialResult:
    """Tests for SpatialResult."""

    def test_init_minimal(self):
        """Test initialization with minimal arguments."""
        result = SpatialResult(method="test")
        assert result.method == "test"
        assert result.statistic is None
        assert result.p_value is None

    def test_init_full(self):
        """Test initialization with all arguments."""
        result = SpatialResult(
            method="regression",
            statistic=2.5,
            p_value=0.01,
            confidence_interval=(1.5, 3.5),
            coefficients={"x1": 0.5, "x2": -0.3},
            residuals=np.array([0.1, -0.2, 0.3]),
            r_squared=0.85,
            adjusted_r_squared=0.83,
            aic=100.5,
            bic=105.2,
            spatial_parameter=0.4,
            moran_i=0.25,
            n_obs=100,
            n_features=2,
        )
        assert result.method == "regression"
        assert result.statistic == 2.5
        assert result.r_squared == 0.85
        assert result.spatial_parameter == 0.4

    def test_repr(self):
        """Test string representation."""
        result = SpatialResult(
            method="test",
            statistic=1.96,
            p_value=0.05,
            r_squared=0.75,
            n_obs=50,
        )
        repr_str = repr(result)
        assert "SpatialResult" in repr_str
        assert "test" in repr_str
        assert "1.96" in repr_str

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = SpatialResult(
            method="test",
            statistic=1.5,
            p_value=0.1,
            coefficients={"a": 1.0, "b": 2.0},
        )
        result_dict = result.to_dict()
        assert result_dict["method"] == "test"
        assert result_dict["statistic"] == 1.5
        assert result_dict["coefficients"] == {"a": 1.0, "b": 2.0}

    def test_to_dataframe(self):
        """Test conversion to DataFrame."""
        result = SpatialResult(
            method="test",
            coefficients={"x1": 0.5, "x2": -0.3},
            std_errors={"x1": 0.1, "x2": 0.15},
            degrees_freedom=98,
        )
        df = result.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert "coefficient" in df.columns
        assert "std_error" in df.columns
        assert "t_statistic" in df.columns
        assert "p_value" in df.columns
        assert len(df) == 2

    def test_to_dataframe_no_coefficients(self):
        """Test to_dataframe with no coefficients raises error."""
        result = SpatialResult(method="test")
        with pytest.raises(ValueError, match="No coefficients"):
            result.to_dataframe()


class TestSpatialDataFrame:
    """Tests for SpatialDataFrame."""

    @pytest.fixture
    def sample_spatial_df(self):
        """Create sample SpatialDataFrame."""
        data = {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
            "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
        }
        return SpatialDataFrame(data, crs="EPSG:4326")

    def test_bounds_dict(self, sample_spatial_df):
        """Test bounds_dict property."""
        bounds = sample_spatial_df.bounds_dict
        assert isinstance(bounds, dict)
        assert "minx" in bounds
        assert "miny" in bounds
        assert "maxx" in bounds
        assert "maxy" in bounds
        assert bounds["minx"] == 0.0
        assert bounds["maxx"] == 2.0

    def test_centroid_coords(self, sample_spatial_df):
        """Test centroid_coords property."""
        coords = sample_spatial_df.centroid_coords
        assert isinstance(coords, np.ndarray)
        assert coords.shape == (3, 2)
        np.testing.assert_array_equal(coords[0], [0.0, 0.0])
        np.testing.assert_array_equal(coords[1], [1.0, 1.0])

    def test_buffer_distance(self, sample_spatial_df):
        """Test buffer_distance method."""
        buffered = sample_spatial_df.buffer_distance(0.5)
        assert isinstance(buffered, SpatialDataFrame)
        assert len(buffered) == len(sample_spatial_df)
        # Buffered points should be polygons
        assert all(geom.geom_type == "Polygon" for geom in buffered.geometry)

    def test_spatial_join_nearest(self):
        """Test spatial_join_nearest method."""
        # Create two SpatialDataFrames
        gdf1 = SpatialDataFrame(
            {"id": [1, 2], "geometry": [Point(0, 0), Point(5, 5)]}, crs="EPSG:4326"
        )
        gdf2 = SpatialDataFrame(
            {"name": ["A", "B"], "geometry": [Point(0.5, 0.5), Point(5.5, 5.5)]},
            crs="EPSG:4326",
        )

        result = gdf1.spatial_join_nearest(gdf2)
        assert "nearest_idx" in result.columns
        assert "nearest_distance" in result.columns
        assert len(result) == len(gdf1)

    def test_spatial_join_nearest_max_distance(self):
        """Test spatial_join_nearest with max_distance."""
        gdf1 = SpatialDataFrame(
            {"id": [1, 2], "geometry": [Point(0, 0), Point(10, 10)]}, crs="EPSG:4326"
        )
        gdf2 = SpatialDataFrame({"name": ["A"], "geometry": [Point(0.5, 0.5)]}, crs="EPSG:4326")

        result = gdf1.spatial_join_nearest(gdf2, max_distance=1.0)
        # First point should match, second should not (too far)
        assert result.loc[0, "nearest_idx"] >= 0
        assert result.loc[1, "nearest_idx"] == -1
        assert pd.isna(result.loc[1, "nearest_distance"])


class TestCreateGeoDataFrame:
    """Tests for create_geodataframe function."""

    def test_from_coordinates(self):
        """Test creating GeoDataFrame from coordinates."""
        df = pd.DataFrame({"x": [-118, -122], "y": [34, 37], "value": [1, 2]})
        gdf = create_geodataframe(df, x_col="x", y_col="y")

        assert isinstance(gdf, GeoDataFrame)
        assert len(gdf) == 2
        assert gdf.crs.to_string() == "EPSG:4326"
        assert all(geom.geom_type == "Point" for geom in gdf.geometry)

    def test_from_geometry_column(self):
        """Test creating GeoDataFrame from existing geometry column."""
        df = pd.DataFrame({"id": [1, 2], "geometry": [Point(-118, 34), Point(-122, 37)]})
        gdf = create_geodataframe(df, geometry_col="geometry")

        assert isinstance(gdf, GeoDataFrame)
        assert len(gdf) == 2
        assert gdf.crs.to_string() == "EPSG:4326"

    def test_from_dict(self):
        """Test creating GeoDataFrame from dictionary."""
        data = {"x": [-118, -122], "y": [34, 37], "value": [1, 2]}
        gdf = create_geodataframe(data, x_col="x", y_col="y")

        assert isinstance(gdf, GeoDataFrame)
        assert len(gdf) == 2

    def test_custom_crs(self):
        """Test creating GeoDataFrame with custom CRS."""
        df = pd.DataFrame({"x": [0, 1], "y": [0, 1], "value": [1, 2]})
        gdf = create_geodataframe(df, x_col="x", y_col="y", crs="EPSG:3857")

        assert gdf.crs.to_string() == "EPSG:3857"

    def test_missing_arguments(self):
        """Test error when neither geometry_col nor coordinates provided."""
        df = pd.DataFrame({"value": [1, 2]})
        with pytest.raises(ValueError, match="Must provide either"):
            create_geodataframe(df)

    def test_missing_x_col(self):
        """Test error when only y_col provided."""
        df = pd.DataFrame({"y": [34, 37], "value": [1, 2]})
        with pytest.raises(ValueError, match="Must provide either"):
            create_geodataframe(df, y_col="y")
