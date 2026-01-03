"""
Writer functions for geospatial data formats.

This module provides functions for writing GeoDataFrames to various
file formats.
"""

from pathlib import Path
from typing import Any, Optional, Union

import geopandas as gpd
try:
    from krl_core.logging import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

logger = get_logger(__name__)


def write_file(gdf: gpd.GeoDataFrame, filepath: Union[str, Path], **kwargs: Any) -> None:
    """
    Write GeoDataFrame to a file (auto-detect format from extension).

    Args:
        gdf: GeoDataFrame to write
        filepath: Path to the output file
        **kwargs: Additional arguments passed to the format-specific writer

    Raises:
        ValueError: If file format is not supported

    Example:
        ```python
        from krl_geospatial.io import write_file

        # Auto-detect format from extension
        write_file(gdf, "output.shp")
        write_file(gdf, "output.geojson")
        write_file(gdf, "output.parquet")
        ```
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()

    if suffix in [".shp"]:
        write_shapefile(gdf, filepath, **kwargs)
    elif suffix in [".geojson", ".json"]:
        write_geojson(gdf, filepath, **kwargs)
    elif suffix in [".parquet", ".geoparquet"]:
        write_geoparquet(gdf, filepath, **kwargs)
    elif suffix == ".csv":
        write_csv(gdf, filepath, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. "
            f"Supported formats: .shp, .geojson, .json, .parquet, .geoparquet, .csv"
        )


def write_shapefile(
    gdf: gpd.GeoDataFrame, filepath: Union[str, Path], mode: str = "w", **kwargs: Any
) -> None:
    """
    Write GeoDataFrame to an ESRI Shapefile.

    Args:
        gdf: GeoDataFrame to write
        filepath: Path to the output shapefile
        mode: Write mode ('w' = write, 'a' = append)
        **kwargs: Additional arguments passed to geopandas.to_file

    Example:
        ```python
        from krl_geospatial.io import write_shapefile

        # Write shapefile
        write_shapefile(gdf, "output.shp")

        # Append to existing shapefile
        write_shapefile(gdf, "existing.shp", mode='a')
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Writing {len(gdf)} features to shapefile: {filepath}")

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    gdf.to_file(filepath, driver="ESRI Shapefile", mode=mode, **kwargs)
    logger.info(f"Successfully wrote shapefile: {filepath}")


def write_geojson(
    gdf: gpd.GeoDataFrame, filepath: Union[str, Path], indent: Optional[int] = 2, **kwargs: Any
) -> None:
    """
    Write GeoDataFrame to a GeoJSON file.

    Args:
        gdf: GeoDataFrame to write
        filepath: Path to the output GeoJSON file
        indent: Number of spaces for indentation (None = compact)
        **kwargs: Additional arguments passed to geopandas.to_file

    Example:
        ```python
        from krl_geospatial.io import write_geojson

        # Write formatted GeoJSON
        write_geojson(gdf, "output.geojson")

        # Write compact GeoJSON (no indentation)
        write_geojson(gdf, "output.geojson", indent=None)
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Writing {len(gdf)} features to GeoJSON: {filepath}")

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Don't pass indent to geopandas (not supported by pyogrio)
    # Just write the GeoJSON
    gdf.to_file(filepath, driver="GeoJSON", **kwargs)
    logger.info(f"Successfully wrote GeoJSON: {filepath}")


def write_geoparquet(
    gdf: gpd.GeoDataFrame, filepath: Union[str, Path], compression: str = "snappy", **kwargs: Any
) -> None:
    """
    Write GeoDataFrame to a GeoParquet file.

    GeoParquet is a columnar format optimized for geospatial data,
    offering better compression and faster read/write times than Shapefile.

    Args:
        gdf: GeoDataFrame to write
        filepath: Path to the output GeoParquet file
        compression: Compression algorithm ('snappy', 'gzip', 'brotli', 'lz4', 'zstd', None)
        **kwargs: Additional arguments passed to geopandas.to_parquet

    Example:
        ```python
        from krl_geospatial.io import write_geoparquet

        # Write with snappy compression (default)
        write_geoparquet(gdf, "output.parquet")

        # Write with gzip compression
        write_geoparquet(gdf, "output.parquet", compression='gzip')

        # Write without compression
        write_geoparquet(gdf, "output.parquet", compression=None)
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Writing {len(gdf)} features to GeoParquet: {filepath}")

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    gdf.to_parquet(filepath, compression=compression, **kwargs)
    logger.info(f"Successfully wrote GeoParquet: {filepath}")


def write_csv(
    gdf: gpd.GeoDataFrame,
    filepath: Union[str, Path],
    include_geometry: bool = True,
    geometry_format: str = "wkt",
    x_col: str = "longitude",
    y_col: str = "latitude",
    **kwargs: Any,
) -> None:
    """
    Write GeoDataFrame to a CSV file.

    Can optionally include geometry as WKT or extract coordinates.

    Args:
        gdf: GeoDataFrame to write
        filepath: Path to the output CSV file
        include_geometry: If True, include geometry column
        geometry_format: Format for geometry ('wkt', 'wkb', 'xy')
        x_col: Name for x coordinate column (if geometry_format='xy')
        y_col: Name for y coordinate column (if geometry_format='xy')
        **kwargs: Additional arguments passed to pandas.to_csv

    Example:
        ```python
        from krl_geospatial.io import write_csv

        # Write with WKT geometry
        write_csv(gdf, "output.csv")

        # Write with x/y coordinates (points only)
        write_csv(gdf, "output.csv", geometry_format='xy')

        # Write without geometry
        write_csv(gdf, "output.csv", include_geometry=False)
        ```
    """
    filepath = Path(filepath)
    logger.info(f"Writing {len(gdf)} features to CSV: {filepath}")

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    df = gdf.copy()

    if include_geometry:
        if geometry_format == "wkt":
            # Add WKT geometry column
            df["geometry_wkt"] = df.geometry.to_wkt()
            df = df.drop(columns=["geometry"])
        elif geometry_format == "wkb":
            # Add WKB geometry column
            df["geometry_wkb"] = df.geometry.to_wkb()
            df = df.drop(columns=["geometry"])
        elif geometry_format == "xy":
            # Extract x and y coordinates (for points only)
            if not all(df.geometry.geom_type == "Point"):
                logger.warning(
                    "geometry_format='xy' only works for Point geometries. "
                    "Non-point geometries will have null coordinates."
                )
            df[x_col] = df.geometry.x
            df[y_col] = df.geometry.y
            df = df.drop(columns=["geometry"])
        else:
            raise ValueError(
                f"Invalid geometry_format: {geometry_format}. " f"Must be 'wkt', 'wkb', or 'xy'."
            )
    else:
        # Drop geometry column
        df = df.drop(columns=["geometry"])

    # Set default index=False if not specified
    if "index" not in kwargs:
        kwargs["index"] = False

    df.to_csv(filepath, **kwargs)
    logger.info(f"Successfully wrote CSV: {filepath}")
