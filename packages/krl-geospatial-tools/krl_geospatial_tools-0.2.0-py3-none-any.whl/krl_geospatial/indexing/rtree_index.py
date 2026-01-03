"""
R-tree spatial index implementation.

R-tree is a tree data structure for indexing multi-dimensional information,
particularly useful for spatial indexing of geographic data.
"""

from typing import List, Optional, Tuple, Union

import geopandas as gpd
from shapely.geometry import Point, box
from shapely.geometry.base import BaseGeometry

try:
    from rtree import index

    RTREE_AVAILABLE = True
except ImportError:
    RTREE_AVAILABLE = False

try:
    from krl_core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class RTreeIndex:
    """
    R-tree spatial index for efficient spatial queries.

    R-trees are balanced tree structures that organize spatial data
    using minimum bounding rectangles (MBRs). They provide efficient
    spatial queries like intersection, containment, and nearest neighbor.

    Example:
        ```python
        import geopandas as gpd
        from krl_geospatial.indexing import RTreeIndex

        # Load spatial data
        gdf = gpd.read_file("cities.shp")

        # Build R-tree index
        idx = RTreeIndex()
        idx.build(gdf)

        # Query intersecting features
        bbox = (-120, 30, -110, 40)
        intersecting = idx.intersection(bbox)

        # Find nearest neighbors
        point = (-115, 35)
        nearest = idx.nearest(point, k=5)
        ```

    Attributes:
        gdf (Optional[gpd.GeoDataFrame]): Source GeoDataFrame
        index: R-tree index object
    """

    def __init__(self):
        """Initialize an empty R-tree index."""
        if not RTREE_AVAILABLE:
            raise ImportError(
                "rtree package is required for RTreeIndex. " "Install with: pip install rtree"
            )

        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.index = index.Index()
        self._built = False
        logger.info("Initialized RTreeIndex")

    def build(self, gdf: gpd.GeoDataFrame) -> "RTreeIndex":
        """
        Build R-tree index from a GeoDataFrame.

        Args:
            gdf: GeoDataFrame to index

        Returns:
            self: Built RTreeIndex

        Raises:
            ValueError: If GeoDataFrame is empty
        """
        if len(gdf) == 0:
            raise ValueError("Cannot build index from empty GeoDataFrame")

        logger.info(f"Building R-tree index for {len(gdf)} geometries")

        self.gdf = gdf.copy()
        self.index = index.Index()

        # Insert each geometry's bounding box
        for idx_val, geom in enumerate(gdf.geometry):
            if geom is not None and not geom.is_empty:
                bounds = geom.bounds  # (minx, miny, maxx, maxy)
                self.index.insert(idx_val, bounds)

        self._built = True
        logger.info(f"R-tree index built with {len(gdf)} geometries")

        return self

    def intersection(
        self,
        bbox: Union[Tuple[float, float, float, float], BaseGeometry],
        return_indices: bool = False,
    ) -> Union[gpd.GeoDataFrame, List[int]]:
        """
        Query geometries that intersect a bounding box or geometry.

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy) or geometry
            return_indices: If True, return indices instead of GeoDataFrame

        Returns:
            GeoDataFrame of intersecting geometries or list of indices

        Raises:
            ValueError: If index has not been built
        """
        if not self._built:
            raise ValueError("Index must be built before querying. Call build() first.")

        # Convert geometry to bbox if needed
        if isinstance(bbox, BaseGeometry):
            bbox = bbox.bounds

        # Query R-tree
        intersecting_ids = list(self.index.intersection(bbox))

        if return_indices:
            return intersecting_ids

        # Return subset of GeoDataFrame
        return self.gdf.iloc[intersecting_ids].copy()

    def nearest(
        self, point: Union[Tuple[float, float], Point], k: int = 1, return_indices: bool = False
    ) -> Union[gpd.GeoDataFrame, List[int]]:
        """
        Find k nearest neighbors to a point.

        Args:
            point: Query point as (x, y) tuple or Point geometry
            k: Number of nearest neighbors to return
            return_indices: If True, return indices instead of GeoDataFrame

        Returns:
            GeoDataFrame of k nearest geometries or list of indices

        Raises:
            ValueError: If index has not been built or k < 1
        """
        if not self._built:
            raise ValueError("Index must be built before querying. Call build() first.")

        if k < 1:
            raise ValueError("k must be at least 1")

        # Convert Point to tuple if needed
        if isinstance(point, Point):
            point = (point.x, point.y)

        # R-tree nearest expects a bbox, use point as both min and max
        bbox = (point[0], point[1], point[0], point[1])

        # Query R-tree for k nearest
        nearest_ids = list(self.index.nearest(bbox, k))

        if return_indices:
            return nearest_ids

        # Return subset of GeoDataFrame
        return self.gdf.iloc[nearest_ids].copy()

    def contains(
        self,
        bbox: Union[Tuple[float, float, float, float], BaseGeometry],
        return_indices: bool = False,
    ) -> Union[gpd.GeoDataFrame, List[int]]:
        """
        Query geometries contained within a bounding box or geometry.

        Note: This checks bounding box containment, not precise geometry containment.

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy) or geometry
            return_indices: If True, return indices instead of GeoDataFrame

        Returns:
            GeoDataFrame of contained geometries or list of indices

        Raises:
            ValueError: If index has not been built
        """
        if not self._built:
            raise ValueError("Index must be built before querying. Call build() first.")

        # Convert geometry to bbox if needed
        if isinstance(bbox, BaseGeometry):
            bbox = bbox.bounds

        # Get candidates from intersection query
        candidates = self.intersection(bbox, return_indices=True)

        # Filter to geometries whose bbox is fully contained
        contained_ids = []
        query_box = box(*bbox)

        for idx_val in candidates:
            geom = self.gdf.iloc[idx_val].geometry
            if geom is not None and not geom.is_empty:
                geom_box = box(*geom.bounds)
                if query_box.contains(geom_box):
                    contained_ids.append(idx_val)

        if return_indices:
            return contained_ids

        return self.gdf.iloc[contained_ids].copy()

    def count_intersection(
        self, bbox: Union[Tuple[float, float, float, float], BaseGeometry]
    ) -> int:
        """
        Count geometries that intersect a bounding box.

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy) or geometry

        Returns:
            Number of intersecting geometries
        """
        intersecting_ids = self.intersection(bbox, return_indices=True)
        return len(intersecting_ids)

    def clear(self) -> None:
        """Clear the index and release resources."""
        self.index = index.Index()
        self.gdf = None
        self._built = False
        logger.info("R-tree index cleared")

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._built:
            return "RTreeIndex(built=False)"
        return f"RTreeIndex(n_geometries={len(self.gdf)}, built=True)"
