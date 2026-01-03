# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""
Advanced Spatial Index with R-tree optimization.

This module provides a high-performance spatial index implementation
that achieves O(n log n) complexity for spatial joins, replacing the
naive O(n²) approach used in basic spatial operations.

Key Features:
- R-tree based spatial indexing
- Bulk loading for optimal tree construction
- K-nearest neighbor queries
- Range queries with various predicates
- Serialization/deserialization for index persistence
- Memory-efficient streaming for large datasets
- Progress callbacks for long operations

Complexity Analysis:
- Index construction: O(n log n)
- Point query: O(log n)
- Range query: O(log n + k) where k is result size
- K-NN query: O(k log n)
- Spatial join: O(n log n) vs O(n²) naive

Example:
    >>> import geopandas as gpd
    >>> from krl_geospatial.indexing import SpatialIndex
    >>>
    >>> # Load large dataset
    >>> gdf = gpd.read_file("large_polygons.shp")
    >>>
    >>> # Build optimized spatial index
    >>> idx = SpatialIndex(gdf, bulk_load=True)
    >>>
    >>> # Fast spatial join
    >>> points = gpd.read_file("points.shp")
    >>> result = idx.spatial_join(points, predicate="intersects")
    >>>
    >>> # Memory-efficient streaming for very large datasets
    >>> for batch in idx.stream_nearest_neighbors(points, k=5, batch_size=1000):
    ...     process_batch(batch)
"""

from __future__ import annotations

import json
import pickle
import struct
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import wkb, wkt
from shapely.geometry import Point, box, mapping
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

try:
    from rtree import index as rtree_index
    from rtree.index import Property as RTreeProperty

    RTREE_AVAILABLE = True
except ImportError:
    RTREE_AVAILABLE = False
    rtree_index = None
    RTreeProperty = None

try:
    from krl_core.logging import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class IndexBackend(Enum):
    """Available spatial index backends."""

    RTREE = "rtree"  # libspatialindex R-tree
    STRTREE = "strtree"  # Shapely STRtree (Sort-Tile-Recursive)
    AUTO = "auto"  # Auto-select best available


class SpatialPredicate(Enum):
    """Spatial predicates for queries."""

    INTERSECTS = "intersects"
    CONTAINS = "contains"
    WITHIN = "within"
    OVERLAPS = "overlaps"
    CROSSES = "crosses"
    TOUCHES = "touches"


@dataclass
class QueryResult:
    """Result of a spatial query."""

    indices: np.ndarray
    geometries: Optional[List[BaseGeometry]] = None
    distances: Optional[np.ndarray] = None
    attributes: Optional[pd.DataFrame] = None

    def __len__(self) -> int:
        return len(self.indices)

    def to_geodataframe(
        self, source_gdf: gpd.GeoDataFrame, copy: bool = True
    ) -> gpd.GeoDataFrame:
        """Convert query result to GeoDataFrame."""
        result = source_gdf.iloc[self.indices]
        if copy:
            result = result.copy()
        if self.distances is not None:
            result["_distance"] = self.distances
        return result


@dataclass
class IndexStats:
    """Statistics about the spatial index."""

    n_geometries: int
    n_empty: int
    n_null: int
    bbox: Tuple[float, float, float, float]
    memory_bytes: int
    build_time_seconds: float
    backend: str
    bulk_loaded: bool
    geometry_types: Dict[str, int] = field(default_factory=dict)


class SpatialIndex:
    """
    High-performance spatial index with O(n log n) operations.

    This class provides an optimized spatial index using R-tree or STRtree
    backends, enabling efficient spatial queries on large geospatial datasets.

    The index supports:
    - Bulk loading for optimal tree construction
    - Multiple query types (intersection, k-NN, range)
    - Streaming operations for memory efficiency
    - Index serialization for persistence
    - Thread-safe operations

    Complexity:
        - Build: O(n log n) with bulk loading, O(n log n) incremental
        - Query: O(log n + k) for range queries
        - K-NN: O(k log n) with priority queue

    Attributes:
        gdf: Source GeoDataFrame
        backend: Index backend being used
        stats: Index statistics

    Example:
        >>> idx = SpatialIndex(gdf, backend="rtree", bulk_load=True)
        >>> results = idx.query(query_geom, predicate="intersects")
        >>> print(f"Found {len(results)} matches")
    """

    def __init__(
        self,
        gdf: Optional[gpd.GeoDataFrame] = None,
        backend: Union[str, IndexBackend] = IndexBackend.AUTO,
        bulk_load: bool = True,
        interleaved: bool = True,
        leaf_capacity: int = 100,
        near_minimum_overlap_factor: int = 32,
        fill_factor: float = 0.7,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Initialize spatial index.

        Args:
            gdf: GeoDataFrame to index. If None, index is empty.
            backend: Index backend to use. Options: "rtree", "strtree", "auto"
            bulk_load: Use bulk loading for optimal tree structure
            interleaved: Use interleaved coordinate order (RTREE only)
            leaf_capacity: Maximum entries per leaf node (RTREE only)
            near_minimum_overlap_factor: R*-tree split factor (RTREE only)
            fill_factor: Node fill factor for splits (RTREE only)
            progress_callback: Callback(current, total) for progress updates

        Raises:
            ImportError: If requested backend is not available
            ValueError: If GeoDataFrame is invalid
        """
        # Resolve backend
        if isinstance(backend, str):
            backend = IndexBackend(backend.lower())

        self._backend_enum = backend
        self._backend_impl = None
        self._gdf = None
        self._stats: Optional[IndexStats] = None
        self._lock = threading.RLock()
        self._built = False

        # R-tree configuration
        self._interleaved = interleaved
        self._leaf_capacity = leaf_capacity
        self._near_minimum_overlap_factor = near_minimum_overlap_factor
        self._fill_factor = fill_factor
        self._bulk_load = bulk_load
        self._progress_callback = progress_callback

        # Initialize backend
        self._select_backend()

        # Build index if GeoDataFrame provided
        if gdf is not None:
            self.build(gdf)

    def _select_backend(self) -> None:
        """Select and initialize the appropriate backend."""
        if self._backend_enum == IndexBackend.AUTO:
            if RTREE_AVAILABLE:
                self._backend_enum = IndexBackend.RTREE
            else:
                self._backend_enum = IndexBackend.STRTREE
                logger.info("rtree not available, using STRtree backend")

        if self._backend_enum == IndexBackend.RTREE:
            if not RTREE_AVAILABLE:
                raise ImportError(
                    "rtree package is required for RTREE backend. "
                    "Install with: pip install rtree"
                )
            # R-tree index will be created during build
            self._backend_impl = None

        elif self._backend_enum == IndexBackend.STRTREE:
            # STRtree will be created during build
            self._backend_impl = None

    @property
    def backend(self) -> str:
        """Get the name of the active backend."""
        return self._backend_enum.value

    @property
    def gdf(self) -> Optional[gpd.GeoDataFrame]:
        """Get the indexed GeoDataFrame."""
        return self._gdf

    @property
    def stats(self) -> Optional[IndexStats]:
        """Get index statistics."""
        return self._stats

    @property
    def is_built(self) -> bool:
        """Check if index has been built."""
        return self._built

    def build(
        self,
        gdf: gpd.GeoDataFrame,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> "SpatialIndex":
        """
        Build spatial index from GeoDataFrame.

        Uses bulk loading when available for optimal tree structure.
        Bulk loading produces a more balanced tree with better query
        performance than incremental insertion.

        Args:
            gdf: GeoDataFrame to index
            progress_callback: Optional progress callback(current, total)

        Returns:
            self: Built SpatialIndex

        Raises:
            ValueError: If GeoDataFrame is empty or invalid

        Complexity:
            O(n log n) with bulk loading
        """
        import time

        start_time = time.perf_counter()

        if gdf is None or len(gdf) == 0:
            raise ValueError("Cannot build index from empty GeoDataFrame")

        if "geometry" not in gdf.columns and gdf.geometry is None:
            raise ValueError("GeoDataFrame must have a geometry column")

        callback = progress_callback or self._progress_callback

        with self._lock:
            self._gdf = gdf.copy()
            n = len(gdf)

            # Count geometry types and issues
            geom_types: Dict[str, int] = {}
            n_empty = 0
            n_null = 0
            valid_indices = []
            valid_bounds = []

            for i, geom in enumerate(gdf.geometry):
                if callback and i % 1000 == 0:
                    callback(i, n)

                if geom is None:
                    n_null += 1
                    continue

                if geom.is_empty:
                    n_empty += 1
                    continue

                geom_type = geom.geom_type
                geom_types[geom_type] = geom_types.get(geom_type, 0) + 1
                valid_indices.append(i)
                valid_bounds.append(geom.bounds)

            if not valid_indices:
                raise ValueError("No valid geometries found in GeoDataFrame")

            # Build backend-specific index
            if self._backend_enum == IndexBackend.RTREE:
                self._build_rtree(valid_indices, valid_bounds)
            else:
                self._build_strtree(valid_indices)

            # Calculate bounding box
            bounds_array = np.array(valid_bounds)
            total_bbox = (
                float(bounds_array[:, 0].min()),
                float(bounds_array[:, 1].min()),
                float(bounds_array[:, 2].max()),
                float(bounds_array[:, 3].max()),
            )

            # Estimate memory usage
            memory_bytes = self._estimate_memory()

            build_time = time.perf_counter() - start_time

            self._stats = IndexStats(
                n_geometries=len(valid_indices),
                n_empty=n_empty,
                n_null=n_null,
                bbox=total_bbox,
                memory_bytes=memory_bytes,
                build_time_seconds=build_time,
                backend=self._backend_enum.value,
                bulk_loaded=self._bulk_load,
                geometry_types=geom_types,
            )

            self._built = True

            logger.info(
                f"Spatial index built: {len(valid_indices)} geometries in "
                f"{build_time:.3f}s using {self._backend_enum.value}"
            )

        if callback:
            callback(n, n)

        return self

    def _build_rtree(
        self, indices: List[int], bounds: List[Tuple[float, float, float, float]]
    ) -> None:
        """Build R-tree index using libspatialindex."""
        props = RTreeProperty()
        props.dimension = 2
        props.interleaved = self._interleaved
        props.leaf_capacity = self._leaf_capacity
        props.near_minimum_overlap_factor = self._near_minimum_overlap_factor
        props.fill_factor = self._fill_factor

        if self._bulk_load:
            # Bulk loading uses STR algorithm for optimal packing
            def generator():
                for idx, bbox in zip(indices, bounds):
                    yield (idx, bbox, None)

            self._backend_impl = rtree_index.Index(generator(), properties=props)
        else:
            # Incremental insertion
            self._backend_impl = rtree_index.Index(properties=props)
            for idx, bbox in zip(indices, bounds):
                self._backend_impl.insert(idx, bbox)

    def _build_strtree(self, indices: List[int]) -> None:
        """Build STRtree index using Shapely."""
        geometries = [self._gdf.geometry.iloc[i] for i in indices]
        self._backend_impl = STRtree(geometries)
        self._strtree_indices = indices

    def _estimate_memory(self) -> int:
        """Estimate memory usage of the index in bytes."""
        if self._backend_enum == IndexBackend.RTREE:
            # Approximate: 40 bytes per entry + tree overhead
            return len(self._gdf) * 50 + 1024
        else:
            # STRtree: geometry references + tree structure
            return len(self._gdf) * 100 + 2048

    def query(
        self,
        geometry: Union[BaseGeometry, Tuple[float, float, float, float]],
        predicate: Union[str, SpatialPredicate] = SpatialPredicate.INTERSECTS,
        return_geometry: bool = False,
    ) -> QueryResult:
        """
        Query geometries that satisfy a spatial predicate.

        Uses the R-tree for candidate filtering, then applies precise
        geometry tests for the final result.

        Args:
            geometry: Query geometry or bounding box (minx, miny, maxx, maxy)
            predicate: Spatial predicate to test
            return_geometry: Include geometries in result

        Returns:
            QueryResult with matching indices

        Raises:
            ValueError: If index has not been built

        Complexity:
            O(log n + k) where k is the number of results
        """
        self._check_built()

        if isinstance(predicate, str):
            predicate = SpatialPredicate(predicate.lower())

        # Convert bbox to geometry if needed
        if isinstance(geometry, tuple):
            query_geom = box(*geometry)
            bbox = geometry
        else:
            query_geom = geometry
            bbox = geometry.bounds

        # Get candidates from spatial index
        if self._backend_enum == IndexBackend.RTREE:
            candidates = list(self._backend_impl.intersection(bbox))
        else:
            # STRtree query
            candidate_geoms = self._backend_impl.query(query_geom)
            candidates = [
                self._strtree_indices[i]
                for i, g in enumerate(self._backend_impl.geometries)
                if g in candidate_geoms
            ]

        # Apply precise predicate testing
        predicate_func = self._get_predicate_func(predicate)
        matching_indices = []

        for idx in candidates:
            geom = self._gdf.geometry.iloc[idx]
            if geom is not None and not geom.is_empty:
                if predicate_func(query_geom, geom):
                    matching_indices.append(idx)

        indices_array = np.array(matching_indices, dtype=np.int64)

        geometries = None
        if return_geometry:
            geometries = [self._gdf.geometry.iloc[i] for i in matching_indices]

        return QueryResult(indices=indices_array, geometries=geometries)

    def _get_predicate_func(
        self, predicate: SpatialPredicate
    ) -> Callable[[BaseGeometry, BaseGeometry], bool]:
        """Get the predicate function for geometry testing."""
        predicates = {
            SpatialPredicate.INTERSECTS: lambda a, b: a.intersects(b),
            SpatialPredicate.CONTAINS: lambda a, b: a.contains(b),
            SpatialPredicate.WITHIN: lambda a, b: a.within(b),
            SpatialPredicate.OVERLAPS: lambda a, b: a.overlaps(b),
            SpatialPredicate.CROSSES: lambda a, b: a.crosses(b),
            SpatialPredicate.TOUCHES: lambda a, b: a.touches(b),
        }
        return predicates[predicate]

    def nearest(
        self,
        point: Union[Point, Tuple[float, float]],
        k: int = 1,
        max_distance: Optional[float] = None,
        return_distance: bool = True,
    ) -> QueryResult:
        """
        Find k nearest neighbors to a point.

        Uses R-tree's optimized nearest neighbor search with priority queue
        for efficient k-NN queries.

        Args:
            point: Query point as (x, y) tuple or Point geometry
            k: Number of nearest neighbors
            max_distance: Maximum search distance (optional)
            return_distance: Calculate and return distances

        Returns:
            QueryResult with k nearest indices and optionally distances

        Raises:
            ValueError: If k < 1 or index not built

        Complexity:
            O(k log n) with R-tree backend
        """
        self._check_built()

        if k < 1:
            raise ValueError("k must be at least 1")

        # Convert to Point
        if isinstance(point, tuple):
            query_point = Point(point[0], point[1])
            x, y = point
        else:
            query_point = point
            x, y = point.x, point.y

        if self._backend_enum == IndexBackend.RTREE:
            # Use R-tree's optimized nearest neighbor search
            bbox = (x, y, x, y)
            nearest_ids = list(self._backend_impl.nearest(bbox, k))
        else:
            # STRtree: compute distances for all and sort
            distances = []
            for i, idx in enumerate(self._strtree_indices):
                geom = self._gdf.geometry.iloc[idx]
                if geom is not None and not geom.is_empty:
                    dist = query_point.distance(geom)
                    distances.append((dist, idx))

            distances.sort(key=lambda x: x[0])
            nearest_ids = [idx for _, idx in distances[:k]]

        # Filter by max_distance if specified
        if max_distance is not None:
            filtered_ids = []
            for idx in nearest_ids:
                geom = self._gdf.geometry.iloc[idx]
                if query_point.distance(geom) <= max_distance:
                    filtered_ids.append(idx)
            nearest_ids = filtered_ids

        indices_array = np.array(nearest_ids, dtype=np.int64)

        # Calculate distances if requested
        distances_array = None
        if return_distance:
            distances_list = []
            for idx in nearest_ids:
                geom = self._gdf.geometry.iloc[idx]
                distances_list.append(query_point.distance(geom))
            distances_array = np.array(distances_list)

        return QueryResult(indices=indices_array, distances=distances_array)

    def bulk_nearest(
        self,
        points: Union[gpd.GeoDataFrame, List[Point], np.ndarray],
        k: int = 1,
        max_distance: Optional[float] = None,
        n_jobs: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[QueryResult]:
        """
        Find k nearest neighbors for multiple query points.

        Efficiently processes many queries using parallel execution.

        Args:
            points: Query points as GeoDataFrame, list of Points, or Nx2 array
            k: Number of nearest neighbors per point
            max_distance: Maximum search distance
            n_jobs: Number of parallel workers (1 = sequential)
            progress_callback: Progress callback(current, total)

        Returns:
            List of QueryResult, one per query point

        Complexity:
            O(m * k log n) where m is number of query points
        """
        self._check_built()

        # Convert to list of coordinates
        if isinstance(points, gpd.GeoDataFrame):
            coords = [(geom.x, geom.y) for geom in points.geometry]
        elif isinstance(points, np.ndarray):
            coords = [(float(p[0]), float(p[1])) for p in points]
        else:
            coords = [(p.x, p.y) if isinstance(p, Point) else p for p in points]

        n_points = len(coords)
        results: List[Optional[QueryResult]] = [None] * n_points

        if n_jobs == 1:
            # Sequential processing
            for i, coord in enumerate(coords):
                results[i] = self.nearest(coord, k=k, max_distance=max_distance)
                if progress_callback and i % 100 == 0:
                    progress_callback(i, n_points)
        else:
            # Parallel processing
            def process_point(args):
                idx, coord = args
                return idx, self.nearest(coord, k=k, max_distance=max_distance)

            with ThreadPoolExecutor(max_workers=n_jobs) as executor:
                futures = {
                    executor.submit(process_point, (i, c)): i
                    for i, c in enumerate(coords)
                }

                completed = 0
                for future in as_completed(futures):
                    idx, result = future.result()
                    results[idx] = result
                    completed += 1
                    if progress_callback and completed % 100 == 0:
                        progress_callback(completed, n_points)

        if progress_callback:
            progress_callback(n_points, n_points)

        return results

    def spatial_join(
        self,
        right_gdf: gpd.GeoDataFrame,
        predicate: Union[str, SpatialPredicate] = SpatialPredicate.INTERSECTS,
        how: str = "inner",
        lsuffix: str = "left",
        rsuffix: str = "right",
    ) -> gpd.GeoDataFrame:
        """
        Perform spatial join using the spatial index.

        This is the key O(n log n) operation that replaces O(n²) naive joins.

        Args:
            right_gdf: GeoDataFrame to join with indexed data
            predicate: Spatial predicate for join
            how: Join type ("inner", "left", "right")
            lsuffix: Suffix for left (indexed) columns
            rsuffix: Suffix for right columns

        Returns:
            Joined GeoDataFrame

        Complexity:
            O(n log n + m) where n is indexed size, m is right size
        """
        self._check_built()

        if isinstance(predicate, str):
            predicate = SpatialPredicate(predicate.lower())

        left_indices = []
        right_indices = []

        predicate_func = self._get_predicate_func(predicate)

        # For each geometry in right, find matching in left (indexed)
        for right_idx, right_geom in enumerate(right_gdf.geometry):
            if right_geom is None or right_geom.is_empty:
                if how in ("right",):
                    # Keep unmatched right rows
                    left_indices.append(-1)
                    right_indices.append(right_idx)
                continue

            # Get candidates from spatial index
            result = self.query(right_geom, predicate=predicate)

            if len(result) > 0:
                # Add all matches
                for left_idx in result.indices:
                    left_indices.append(left_idx)
                    right_indices.append(right_idx)
            elif how in ("right",):
                left_indices.append(-1)
                right_indices.append(right_idx)

        # Build result DataFrame
        left_data = self._gdf.iloc[[i for i in left_indices if i >= 0]].copy()
        left_data = left_data.add_suffix(f"_{lsuffix}")

        right_data = right_gdf.iloc[right_indices].copy()
        right_data = right_data.add_suffix(f"_{rsuffix}")
        right_data.index = range(len(right_data))

        # Handle -1 indices for outer joins
        if how in ("right",):
            full_left = pd.DataFrame(index=range(len(right_indices)))
            valid_mask = [i >= 0 for i in left_indices]
            for col in left_data.columns:
                full_left[col] = None
                full_left.loc[valid_mask, col] = left_data[col].values
            left_data = full_left

        result = pd.concat([left_data.reset_index(drop=True), right_data], axis=1)

        # Set geometry column
        geom_col = f"geometry_{lsuffix}"
        if geom_col in result.columns:
            result = gpd.GeoDataFrame(result, geometry=geom_col)
        else:
            result = gpd.GeoDataFrame(result)

        return result

    def stream_nearest_neighbors(
        self,
        points: Union[gpd.GeoDataFrame, Iterable[Tuple[float, float]]],
        k: int = 1,
        batch_size: int = 1000,
        max_distance: Optional[float] = None,
    ) -> Generator[List[QueryResult], None, None]:
        """
        Stream nearest neighbor queries in batches for memory efficiency.

        Useful for very large query sets that don't fit in memory.

        Args:
            points: Iterable of query points
            k: Number of nearest neighbors
            batch_size: Number of points per batch
            max_distance: Maximum search distance

        Yields:
            Batches of QueryResult objects

        Example:
            >>> for batch in idx.stream_nearest_neighbors(large_points, k=5):
            ...     for result in batch:
            ...         process_result(result)
        """
        self._check_built()

        # Convert GeoDataFrame to coordinate generator
        if isinstance(points, gpd.GeoDataFrame):
            point_iter = ((geom.x, geom.y) for geom in points.geometry)
        else:
            point_iter = iter(points)

        batch = []
        for point in point_iter:
            result = self.nearest(point, k=k, max_distance=max_distance)
            batch.append(result)

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

    def save(self, path: Union[str, Path]) -> None:
        """
        Save spatial index to file.

        Serializes the index for later use without rebuilding.

        Args:
            path: Output file path (extension determines format)

        Supported formats:
            - .pkl: Python pickle (fastest)
            - .idx: R-tree index file (RTREE backend only)
        """
        self._check_built()

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix == ".idx" and self._backend_enum == IndexBackend.RTREE:
            # Save R-tree index directly
            # R-tree supports file-based storage
            warnings.warn(
                "Direct R-tree file saving requires recreating index. "
                "Using pickle format instead."
            )

        # Use pickle for general serialization
        save_path = path.with_suffix(".pkl")

        data = {
            "gdf_wkb": self._gdf.geometry.apply(lambda g: g.wkb if g else None).tolist(),
            "gdf_attrs": self._gdf.drop(columns=["geometry"]).to_dict("records"),
            "gdf_crs": str(self._gdf.crs) if self._gdf.crs else None,
            "backend": self._backend_enum.value,
            "stats": self._stats,
            "config": {
                "bulk_load": self._bulk_load,
                "interleaved": self._interleaved,
                "leaf_capacity": self._leaf_capacity,
                "fill_factor": self._fill_factor,
            },
        }

        with open(save_path, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        logger.info(f"Spatial index saved to {save_path}")

    @classmethod
    def load(cls, path: Union[str, Path]) -> "SpatialIndex":
        """
        Load spatial index from file.

        Args:
            path: Input file path

        Returns:
            Loaded SpatialIndex

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(path)
        if not path.exists():
            path = path.with_suffix(".pkl")

        if not path.exists():
            raise FileNotFoundError(f"Index file not found: {path}")

        with open(path, "rb") as f:
            data = pickle.load(f)

        # Reconstruct GeoDataFrame
        from shapely import wkb

        geometries = [wkb.loads(g) if g else None for g in data["gdf_wkb"]]
        attrs = pd.DataFrame(data["gdf_attrs"])
        gdf = gpd.GeoDataFrame(attrs, geometry=geometries)

        if data["gdf_crs"]:
            gdf.set_crs(data["gdf_crs"], inplace=True)

        # Create new index
        config = data.get("config", {})
        idx = cls(
            gdf=gdf,
            backend=data["backend"],
            bulk_load=config.get("bulk_load", True),
            interleaved=config.get("interleaved", True),
            leaf_capacity=config.get("leaf_capacity", 100),
            fill_factor=config.get("fill_factor", 0.7),
        )

        logger.info(f"Spatial index loaded from {path}")
        return idx

    def _check_built(self) -> None:
        """Verify index has been built."""
        if not self._built:
            raise ValueError(
                "Index must be built before querying. "
                "Call build() or pass gdf to constructor."
            )

    def __len__(self) -> int:
        """Return number of indexed geometries."""
        if self._stats:
            return self._stats.n_geometries
        return 0

    def __repr__(self) -> str:
        """Return string representation."""
        if not self._built:
            return f"SpatialIndex(backend={self.backend}, built=False)"

        return (
            f"SpatialIndex(backend={self.backend}, "
            f"n={len(self)}, "
            f"bulk_loaded={self._stats.bulk_loaded})"
        )

    def __contains__(self, geometry: BaseGeometry) -> bool:
        """Check if a geometry intersects any indexed geometry."""
        if not self._built:
            return False
        result = self.query(geometry, predicate=SpatialPredicate.INTERSECTS)
        return len(result) > 0
