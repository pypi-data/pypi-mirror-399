"""
Reader functions for geospatial data formats.

This module provides functions for reading geospatial data from various
file formats into GeoDataFrames.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
import pandas as pd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
from shapely.geometry import Point

logger = get_logger(__name__)


def read_file(filepath: Union[str, Path], **kwargs: Any) -> gpd.GeoDataFrame:
    """
    Read geospatial data from a file (auto-detect format).

    Automatically detects the file format based on extension and
    reads the data into a GeoDataFrame.

    Args:
        filepath: Path to the file
        **kwargs: Additional arguments passed to the format-specific reader

    Returns:
        GeoDataFrame containing the spatial data

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file does not exist

    Example:
        ```python
        from krl_geospatial.io import read_file

        # Auto-detect format
        gdf = read_file("data.shp")
        gdf = read_file("data.geojson")
        gdf = read_file("data.parquet")
        ```
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    suffix = filepath.suffix.lower()

    if suffix in [".shp", ".dbf", ".shx"]:
        return read_shapefile(filepath, **kwargs)
    elif suffix in [".geojson", ".json"]:
        return read_geojson(filepath, **kwargs)
    elif suffix in [".parquet", ".geoparquet"]:
        return read_geoparquet(filepath, **kwargs)
    elif suffix == ".csv":
        return read_csv(filepath, **kwargs)
    else:
        # Try geopandas generic reader
        try:
            logger.info(f"Attempting to read {filepath} with geopandas generic reader")
            return gpd.read_file(filepath, **kwargs)
        except Exception as e:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: .shp, .geojson, .json, .parquet, .geoparquet, .csv"
            ) from e


def read_shapefile(
    filepath: Union[str, Path],
    layer: Optional[str] = None,
    bbox: Optional[tuple] = None,
    rows: Optional[int] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """
    Read data from an ESRI Shapefile.

    Args:
        filepath: Path to the shapefile
        layer: Layer name to read (for multi-layer shapefiles)
        bbox: Bounding box (minx, miny, maxx, maxy) to filter features
        rows: Number of rows to read
        **kwargs: Additional arguments passed to geopandas.read_file

    Returns:
        GeoDataFrame containing the shapefile data

    Example:
        ```python
        from krl_geospatial.io import read_shapefile

        # Read entire shapefile
        gdf = read_shapefile("counties.shp")

        # Read with bounding box filter
        gdf = read_shapefile("counties.shp", bbox=(-180, -90, 180, 90))

        # Read first 100 rows
        gdf = read_shapefile("counties.shp", rows=100)
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Reading shapefile: {filepath}")

    read_kwargs = kwargs.copy()
    if layer is not None:
        read_kwargs["layer"] = layer
    if bbox is not None:
        read_kwargs["bbox"] = bbox
    if rows is not None:
        read_kwargs["rows"] = rows

    gdf = gpd.read_file(filepath, **read_kwargs)
    logger.info(f"Read {len(gdf)} features from shapefile")

    return gdf


def read_geojson(
    filepath: Union[str, Path],
    bbox: Optional[tuple] = None,
    rows: Optional[int] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """
    Read data from a GeoJSON file.

    Args:
        filepath: Path to the GeoJSON file
        bbox: Bounding box (minx, miny, maxx, maxy) to filter features
        rows: Number of rows to read
        **kwargs: Additional arguments passed to geopandas.read_file

    Returns:
        GeoDataFrame containing the GeoJSON data

    Example:
        ```python
        from krl_geospatial.io import read_geojson

        # Read entire GeoJSON
        gdf = read_geojson("data.geojson")

        # Read with bounding box
        gdf = read_geojson("data.geojson", bbox=(-120, 30, -110, 40))
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Reading GeoJSON: {filepath}")

    read_kwargs = kwargs.copy()
    if bbox is not None:
        read_kwargs["bbox"] = bbox
    if rows is not None:
        read_kwargs["rows"] = rows

    gdf = gpd.read_file(filepath, **read_kwargs)
    logger.info(f"Read {len(gdf)} features from GeoJSON")

    return gdf


def read_geoparquet(
    filepath: Union[str, Path],
    columns: Optional[List[str]] = None,
    bbox: Optional[tuple] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """
    Read data from a GeoParquet file.

    GeoParquet is a columnar format optimized for geospatial data,
    offering better compression and faster read times than Shapefile.

    Args:
        filepath: Path to the GeoParquet file
        columns: List of columns to read (None = all columns)
        bbox: Bounding box (minx, miny, maxx, maxy) to filter features
        **kwargs: Additional arguments passed to geopandas.read_parquet

    Returns:
        GeoDataFrame containing the GeoParquet data

    Example:
        ```python
        from krl_geospatial.io import read_geoparquet

        # Read entire file
        gdf = read_geoparquet("data.parquet")

        # Read specific columns
        gdf = read_geoparquet("data.parquet", columns=["name", "population"])

        # Read with bounding box
        gdf = read_geoparquet("data.parquet", bbox=(-120, 30, -110, 40))
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Reading GeoParquet: {filepath}")

    read_kwargs = kwargs.copy()
    if columns is not None:
        read_kwargs["columns"] = columns
    if bbox is not None:
        read_kwargs["bbox"] = bbox

    gdf = gpd.read_parquet(filepath, **read_kwargs)
    logger.info(f"Read {len(gdf)} features from GeoParquet")

    return gdf


def read_csv(
    filepath: Union[str, Path],
    x_col: str = "longitude",
    y_col: str = "latitude",
    crs: str = "EPSG:4326",
    geometry_col: Optional[str] = None,
    **kwargs: Any,
) -> gpd.GeoDataFrame:
    """
    Read data from a CSV file and convert to GeoDataFrame.

    Can create geometries from coordinate columns or from a WKT/WKB column.

    Args:
        filepath: Path to the CSV file
        x_col: Name of the column containing x coordinates (longitude)
        y_col: Name of the column containing y coordinates (latitude)
        crs: Coordinate reference system (default: WGS84)
        geometry_col: Name of column containing WKT/WKB geometries (overrides x_col/y_col)
        **kwargs: Additional arguments passed to pandas.read_csv

    Returns:
        GeoDataFrame with point geometries created from coordinates

    Raises:
        ValueError: If required columns are missing

    Example:
        ```python
        from krl_geospatial.io import read_csv

        # Read from lat/lon columns
        gdf = read_csv("cities.csv", x_col="lon", y_col="lat")

        # Read from WKT geometry column
        gdf = read_csv("shapes.csv", geometry_col="geometry")
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Reading CSV: {filepath}")

    # Read CSV with pandas
    df = pd.read_csv(filepath, **kwargs)

    if geometry_col is not None:
        # Create geometries from WKT/WKB column
        if geometry_col not in df.columns:
            raise ValueError(f"Geometry column '{geometry_col}' not found in CSV")

        gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df[geometry_col]), crs=crs)
    else:
        # Create point geometries from x/y columns
        if x_col not in df.columns:
            raise ValueError(f"X coordinate column '{x_col}' not found in CSV")
        if y_col not in df.columns:
            raise ValueError(f"Y coordinate column '{y_col}' not found in CSV")

        geometry = [Point(x, y) for x, y in zip(df[x_col], df[y_col])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)

    logger.info(f"Read {len(gdf)} features from CSV")

    return gdf
