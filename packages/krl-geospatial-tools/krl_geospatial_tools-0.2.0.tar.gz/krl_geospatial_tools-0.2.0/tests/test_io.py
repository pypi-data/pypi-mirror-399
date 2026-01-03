"""
Tests for I/O module.

This module tests reading and writing geospatial data in various formats.
"""

import tempfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, Polygon

from krl_geospatial.io import (
    read_csv,
    read_file,
    read_geojson,
    read_geoparquet,
    read_shapefile,
    write_csv,
    write_file,
    write_geojson,
    write_geoparquet,
    write_shapefile,
)

# Fixtures


@pytest.fixture
def sample_gdf():
    """Create a simple GeoDataFrame for testing."""
    data = {
        "name": ["A", "B", "C"],
        "value": [1, 2, 3],
        "geometry": [
            Point(0, 0),
            Point(1, 1),
            Point(2, 2),
        ],
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_polygon_gdf():
    """Create a polygon GeoDataFrame for testing."""
    data = {
        "name": ["Square1", "Square2"],
        "area": [1.0, 1.0],
        "geometry": [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        ],
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# Test Writers


class TestWriteShapefile:
    """Test writing shapefiles."""

    def test_write_shapefile(self, sample_gdf, temp_dir):
        """Test basic shapefile writing."""
        filepath = temp_dir / "test.shp"
        write_shapefile(sample_gdf, filepath)
        assert filepath.exists()

        # Verify we can read it back
        gdf_read = gpd.read_file(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_write_shapefile_polygon(self, sample_polygon_gdf, temp_dir):
        """Test writing polygon shapefile."""
        filepath = temp_dir / "polygons.shp"
        write_shapefile(sample_polygon_gdf, filepath)
        assert filepath.exists()

        gdf_read = gpd.read_file(filepath)
        assert len(gdf_read) == len(sample_polygon_gdf)
        assert all(gdf_read.geometry.geom_type == "Polygon")


class TestWriteGeoJSON:
    """Test writing GeoJSON files."""

    def test_write_geojson(self, sample_gdf, temp_dir):
        """Test basic GeoJSON writing."""
        filepath = temp_dir / "test.geojson"
        write_geojson(sample_gdf, filepath)
        assert filepath.exists()

        # Verify we can read it back
        gdf_read = gpd.read_file(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_write_geojson_no_indent(self, sample_gdf, temp_dir):
        """Test GeoJSON writing without indentation."""
        filepath = temp_dir / "compact.geojson"
        write_geojson(sample_gdf, filepath, indent=None)
        assert filepath.exists()

        # Compact file should be smaller
        file_size = filepath.stat().st_size
        assert file_size > 0


class TestWriteGeoParquet:
    """Test writing GeoParquet files."""

    def test_write_geoparquet(self, sample_gdf, temp_dir):
        """Test basic GeoParquet writing."""
        filepath = temp_dir / "test.parquet"
        write_geoparquet(sample_gdf, filepath)
        assert filepath.exists()

        # Verify we can read it back
        gdf_read = gpd.read_parquet(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_write_geoparquet_compression(self, sample_gdf, temp_dir):
        """Test GeoParquet with different compression."""
        filepath_snappy = temp_dir / "test_snappy.parquet"
        filepath_gzip = temp_dir / "test_gzip.parquet"

        write_geoparquet(sample_gdf, filepath_snappy, compression="snappy")
        write_geoparquet(sample_gdf, filepath_gzip, compression="gzip")

        assert filepath_snappy.exists()
        assert filepath_gzip.exists()


class TestWriteCSV:
    """Test writing CSV files."""

    def test_write_csv_wkt(self, sample_gdf, temp_dir):
        """Test CSV writing with WKT geometry."""
        filepath = temp_dir / "test.csv"
        write_csv(sample_gdf, filepath, geometry_format="wkt")
        assert filepath.exists()

        # Verify we can read it back
        df = pd.read_csv(filepath)
        assert "geometry_wkt" in df.columns
        assert len(df) == len(sample_gdf)

    def test_write_csv_xy(self, sample_gdf, temp_dir):
        """Test CSV writing with x/y coordinates."""
        filepath = temp_dir / "test_xy.csv"
        write_csv(sample_gdf, filepath, geometry_format="xy")
        assert filepath.exists()

        df = pd.read_csv(filepath)
        assert "longitude" in df.columns
        assert "latitude" in df.columns
        assert len(df) == len(sample_gdf)

    def test_write_csv_no_geometry(self, sample_gdf, temp_dir):
        """Test CSV writing without geometry."""
        filepath = temp_dir / "test_no_geom.csv"
        write_csv(sample_gdf, filepath, include_geometry=False)
        assert filepath.exists()

        df = pd.read_csv(filepath)
        assert "geometry" not in df.columns
        assert "name" in df.columns
        assert len(df) == len(sample_gdf)


class TestWriteFile:
    """Test auto-detect write_file function."""

    def test_write_file_shapefile(self, sample_gdf, temp_dir):
        """Test write_file with .shp extension."""
        filepath = temp_dir / "auto.shp"
        write_file(sample_gdf, filepath)
        assert filepath.exists()

    def test_write_file_geojson(self, sample_gdf, temp_dir):
        """Test write_file with .geojson extension."""
        filepath = temp_dir / "auto.geojson"
        write_file(sample_gdf, filepath)
        assert filepath.exists()

    def test_write_file_parquet(self, sample_gdf, temp_dir):
        """Test write_file with .parquet extension."""
        filepath = temp_dir / "auto.parquet"
        write_file(sample_gdf, filepath)
        assert filepath.exists()

    def test_write_file_csv(self, sample_gdf, temp_dir):
        """Test write_file with .csv extension."""
        filepath = temp_dir / "auto.csv"
        write_file(sample_gdf, filepath)
        assert filepath.exists()

    def test_write_file_unsupported(self, sample_gdf, temp_dir):
        """Test write_file with unsupported extension."""
        filepath = temp_dir / "test.unsupported"
        with pytest.raises(ValueError, match="Unsupported file format"):
            write_file(sample_gdf, filepath)


# Test Readers


class TestReadShapefile:
    """Test reading shapefiles."""

    def test_read_shapefile(self, sample_gdf, temp_dir):
        """Test basic shapefile reading."""
        filepath = temp_dir / "test.shp"
        sample_gdf.to_file(filepath, driver="ESRI Shapefile")

        gdf_read = read_shapefile(filepath)
        assert len(gdf_read) == len(sample_gdf)
        assert gdf_read.crs is not None


class TestReadGeoJSON:
    """Test reading GeoJSON files."""

    def test_read_geojson(self, sample_gdf, temp_dir):
        """Test basic GeoJSON reading."""
        filepath = temp_dir / "test.geojson"
        sample_gdf.to_file(filepath, driver="GeoJSON")

        gdf_read = read_geojson(filepath)
        assert len(gdf_read) == len(sample_gdf)
        assert gdf_read.crs is not None


class TestReadGeoParquet:
    """Test reading GeoParquet files."""

    def test_read_geoparquet(self, sample_gdf, temp_dir):
        """Test basic GeoParquet reading."""
        filepath = temp_dir / "test.parquet"
        sample_gdf.to_parquet(filepath)

        gdf_read = read_geoparquet(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_read_geoparquet_columns(self, sample_gdf, temp_dir):
        """Test reading specific columns from GeoParquet."""
        filepath = temp_dir / "test.parquet"
        sample_gdf.to_parquet(filepath)

        gdf_read = read_geoparquet(filepath, columns=["name", "geometry"])
        assert "name" in gdf_read.columns
        assert "value" not in gdf_read.columns


class TestReadCSV:
    """Test reading CSV files."""

    def test_read_csv_default_columns(self, temp_dir):
        """Test reading CSV with default lon/lat columns."""
        filepath = temp_dir / "test.csv"
        df = pd.DataFrame(
            {
                "name": ["A", "B"],
                "longitude": [0, 1],
                "latitude": [0, 1],
            }
        )
        df.to_csv(filepath, index=False)

        gdf = read_csv(filepath)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 2
        assert all(gdf.geometry.geom_type == "Point")

    def test_read_csv_custom_columns(self, temp_dir):
        """Test reading CSV with custom coordinate columns."""
        filepath = temp_dir / "test.csv"
        df = pd.DataFrame(
            {
                "name": ["A", "B"],
                "x": [0, 1],
                "y": [0, 1],
            }
        )
        df.to_csv(filepath, index=False)

        gdf = read_csv(filepath, x_col="x", y_col="y")
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 2

    def test_read_csv_missing_columns(self, temp_dir):
        """Test reading CSV with missing coordinate columns."""
        filepath = temp_dir / "test.csv"
        df = pd.DataFrame({"name": ["A", "B"]})
        df.to_csv(filepath, index=False)

        with pytest.raises(ValueError, match="not found in CSV"):
            read_csv(filepath)


class TestReadFile:
    """Test auto-detect read_file function."""

    def test_read_file_shapefile(self, sample_gdf, temp_dir):
        """Test read_file with shapefile."""
        filepath = temp_dir / "test.shp"
        sample_gdf.to_file(filepath, driver="ESRI Shapefile")

        gdf_read = read_file(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_read_file_geojson(self, sample_gdf, temp_dir):
        """Test read_file with GeoJSON."""
        filepath = temp_dir / "test.geojson"
        sample_gdf.to_file(filepath, driver="GeoJSON")

        gdf_read = read_file(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_read_file_parquet(self, sample_gdf, temp_dir):
        """Test read_file with GeoParquet."""
        filepath = temp_dir / "test.parquet"
        sample_gdf.to_parquet(filepath)

        gdf_read = read_file(filepath)
        assert len(gdf_read) == len(sample_gdf)

    def test_read_file_not_found(self, temp_dir):
        """Test read_file with non-existent file."""
        filepath = temp_dir / "nonexistent.shp"
        with pytest.raises(FileNotFoundError):
            read_file(filepath)


# Test Round-trip (write then read)


class TestRoundTrip:
    """Test writing and reading data maintains integrity."""

    def test_roundtrip_shapefile(self, sample_gdf, temp_dir):
        """Test shapefile round-trip."""
        filepath = temp_dir / "roundtrip.shp"
        write_shapefile(sample_gdf, filepath)
        gdf_read = read_shapefile(filepath)

        assert len(gdf_read) == len(sample_gdf)
        assert gdf_read.crs == sample_gdf.crs

    def test_roundtrip_geojson(self, sample_gdf, temp_dir):
        """Test GeoJSON round-trip."""
        filepath = temp_dir / "roundtrip.geojson"
        write_geojson(sample_gdf, filepath)
        gdf_read = read_geojson(filepath)

        assert len(gdf_read) == len(sample_gdf)
        assert gdf_read.crs == sample_gdf.crs

    def test_roundtrip_geoparquet(self, sample_gdf, temp_dir):
        """Test GeoParquet round-trip."""
        filepath = temp_dir / "roundtrip.parquet"
        write_geoparquet(sample_gdf, filepath)
        gdf_read = read_geoparquet(filepath)

        assert len(gdf_read) == len(sample_gdf)
        assert gdf_read.crs == sample_gdf.crs
