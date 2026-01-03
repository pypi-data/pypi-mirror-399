# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""
Bulk Spatial Operations with R-tree Optimization.

This module provides batch processing utilities for spatial operations,
designed for memory-efficient handling of very large datasets.

Key Features:
- Streaming spatial joins for memory efficiency
- Parallel batch processing
- Progress tracking for long operations
- Chunked processing to avoid memory exhaustion
- Result aggregation with custom functions

Performance Targets:
- Process 1M+ geometries without memory issues
- Linear scaling with number of geometries
- Configurable memory limits

Example:
    >>> from krl_geospatial.indexing import BulkSpatialOps
    >>>
    >>> # Process large dataset in chunks
    >>> ops = BulkSpatialOps(chunk_size=10000)
    >>>
    >>> # Streaming spatial join
    >>> for chunk in ops.stream_spatial_join(left_gdf, right_gdf):
    ...     save_to_database(chunk)
    >>>
    >>> # Parallel nearest neighbor search
    >>> results = ops.parallel_nearest(points, polygons, k=5, n_jobs=4)
"""

from __future__ import annotations

import gc
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, box
from shapely.geometry.base import BaseGeometry

try:
    from rtree import index as rtree_index

    RTREE_AVAILABLE = True
except ImportError:
    RTREE_AVAILABLE = False

try:
    from krl_core.logging import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result from a batch operation."""

    batch_id: int
    n_processed: int
    n_matches: int
    data: Optional[gpd.GeoDataFrame] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OperationStats:
    """Statistics from bulk operation."""

    total_processed: int
    total_matches: int
    n_batches: int
    elapsed_seconds: float
    peak_memory_mb: float
    throughput_per_second: float


class BulkSpatialOps:
    """
    Bulk spatial operations with memory-efficient streaming.

    Provides batch processing for large geospatial datasets, with
    automatic chunking, progress tracking, and parallel execution.

    Attributes:
        chunk_size: Number of geometries per batch
        n_jobs: Number of parallel workers
        memory_limit_mb: Maximum memory usage target
    """

    def __init__(
        self,
        chunk_size: int = 10000,
        n_jobs: int = 1,
        memory_limit_mb: Optional[int] = None,
        temp_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        """
        Initialize bulk operations processor.

        Args:
            chunk_size: Number of geometries per batch
            n_jobs: Number of parallel workers
            memory_limit_mb: Memory limit (auto-detect if None)
            temp_dir: Directory for temporary files
            progress_callback: Callback(current, total, message)
        """
        self.chunk_size = chunk_size
        self.n_jobs = n_jobs
        self.memory_limit_mb = memory_limit_mb or self._detect_memory_limit()
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "krl_bulk_ops"
        self._progress_callback = progress_callback

        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _detect_memory_limit(self) -> int:
        """Detect available memory and set limit to 50%."""
        try:
            import psutil

            total_mb = psutil.virtual_memory().total / (1024 * 1024)
            return int(total_mb * 0.5)
        except ImportError:
            # Default to 4GB if psutil not available
            return 4096

    def _report_progress(self, current: int, total: int, message: str = "") -> None:
        """Report progress to callback."""
        if self._progress_callback:
            self._progress_callback(current, total, message)

    def stream_spatial_join(
        self,
        left_gdf: gpd.GeoDataFrame,
        right_gdf: gpd.GeoDataFrame,
        predicate: str = "intersects",
        how: str = "inner",
    ) -> Generator[gpd.GeoDataFrame, None, None]:
        """
        Stream spatial join results in chunks.

        Builds an R-tree on the smaller dataset and processes the
        larger dataset in chunks to maintain memory efficiency.

        Args:
            left_gdf: Left GeoDataFrame
            right_gdf: Right GeoDataFrame
            predicate: Spatial predicate (intersects, contains, within)
            how: Join type (inner, left)

        Yields:
            GeoDataFrame chunks of join results

        Complexity:
            O(n log m) where n is larger, m is smaller dataset
        """
        from .spatial_index import SpatialIndex

        # Build index on smaller dataset
        if len(left_gdf) <= len(right_gdf):
            indexed = left_gdf
            streaming = right_gdf
            index_is_left = True
        else:
            indexed = right_gdf
            streaming = left_gdf
            index_is_left = False

        logger.info(
            f"Building index on {len(indexed)} geometries, "
            f"streaming {len(streaming)} geometries"
        )

        # Build spatial index
        idx = SpatialIndex(indexed, bulk_load=True)

        # Process streaming dataset in chunks
        n_chunks = (len(streaming) + self.chunk_size - 1) // self.chunk_size

        for chunk_id in range(n_chunks):
            start = chunk_id * self.chunk_size
            end = min(start + self.chunk_size, len(streaming))
            chunk = streaming.iloc[start:end]

            self._report_progress(
                chunk_id + 1, n_chunks, f"Processing chunk {chunk_id + 1}/{n_chunks}"
            )

            # Perform join for this chunk
            if index_is_left:
                result = idx.spatial_join(chunk, predicate=predicate, how=how)
            else:
                # Build temp index on chunk and query against indexed
                chunk_idx = SpatialIndex(chunk, bulk_load=True)
                result = chunk_idx.spatial_join(indexed, predicate=predicate, how=how)

            if len(result) > 0:
                yield result

            # Force garbage collection
            gc.collect()

    def parallel_nearest(
        self,
        query_gdf: gpd.GeoDataFrame,
        target_gdf: gpd.GeoDataFrame,
        k: int = 1,
        max_distance: Optional[float] = None,
    ) -> gpd.GeoDataFrame:
        """
        Find k nearest neighbors in parallel.

        Distributes query points across workers, each with a copy
        of the target R-tree index.

        Args:
            query_gdf: Query points
            target_gdf: Target geometries to search
            k: Number of nearest neighbors
            max_distance: Maximum search distance

        Returns:
            GeoDataFrame with nearest neighbor results

        Complexity:
            O(m * k log n) where m is query size, n is target size
        """
        from .spatial_index import SpatialIndex

        logger.info(
            f"Finding {k} nearest neighbors for {len(query_gdf)} queries "
            f"against {len(target_gdf)} targets"
        )

        # Build target index
        target_idx = SpatialIndex(target_gdf, bulk_load=True)

        # Process queries
        results = target_idx.bulk_nearest(
            query_gdf,
            k=k,
            max_distance=max_distance,
            n_jobs=self.n_jobs,
            progress_callback=lambda c, t: self._report_progress(
                c, t, "Finding nearest neighbors"
            ),
        )

        # Compile results into GeoDataFrame
        rows = []
        for i, result in enumerate(results):
            query_geom = query_gdf.geometry.iloc[i]
            query_data = query_gdf.iloc[i].to_dict()

            # Handle distances array properly
            distances = result.distances if result.distances is not None else [None] * len(result.indices)
            
            for rank, (target_idx_val, dist) in enumerate(
                zip(result.indices, distances)
            ):
                row = {
                    "query_idx": i,
                    "target_idx": target_idx_val,
                    "rank": rank + 1,
                    "distance": dist,
                    "query_geometry": query_geom,
                }
                row.update({f"query_{k}": v for k, v in query_data.items() if k != "geometry"})

                target_data = target_gdf.iloc[target_idx_val].to_dict()
                row.update({f"target_{k}": v for k, v in target_data.items() if k != "geometry"})
                row["target_geometry"] = target_gdf.geometry.iloc[target_idx_val]

                rows.append(row)

        result_df = pd.DataFrame(rows)
        result_gdf = gpd.GeoDataFrame(result_df, geometry="query_geometry")

        return result_gdf

    def batch_buffer(
        self,
        gdf: gpd.GeoDataFrame,
        distance: float,
        cap_style: str = "round",
        join_style: str = "round",
    ) -> Generator[gpd.GeoDataFrame, None, None]:
        """
        Create buffers in batches to manage memory.

        Args:
            gdf: Input GeoDataFrame
            distance: Buffer distance
            cap_style: Cap style (round, flat, square)
            join_style: Join style (round, mitre, bevel)

        Yields:
            GeoDataFrame chunks with buffered geometries
        """
        cap_map = {"round": 1, "flat": 2, "square": 3}
        join_map = {"round": 1, "mitre": 2, "bevel": 3}

        cap = cap_map.get(cap_style, 1)
        join = join_map.get(join_style, 1)

        n_chunks = (len(gdf) + self.chunk_size - 1) // self.chunk_size

        for chunk_id in range(n_chunks):
            start = chunk_id * self.chunk_size
            end = min(start + self.chunk_size, len(gdf))
            chunk = gdf.iloc[start:end].copy()

            self._report_progress(
                chunk_id + 1, n_chunks, f"Buffering chunk {chunk_id + 1}/{n_chunks}"
            )

            # Apply buffer
            chunk["geometry"] = chunk.geometry.buffer(
                distance, cap_style=cap, join_style=join
            )

            yield chunk
            gc.collect()

    def batch_dissolve(
        self,
        gdf: gpd.GeoDataFrame,
        by: Optional[str] = None,
        aggfunc: str = "first",
    ) -> gpd.GeoDataFrame:
        """
        Dissolve geometries in batches.

        For very large datasets, processes in chunks and merges results.

        Args:
            gdf: Input GeoDataFrame
            by: Column to group by (None = dissolve all)
            aggfunc: Aggregation function for attributes

        Returns:
            Dissolved GeoDataFrame
        """
        if len(gdf) <= self.chunk_size:
            # Small enough to process directly
            return gdf.dissolve(by=by, aggfunc=aggfunc)

        if by is None:
            # Dissolve all - process in chunks then merge
            logger.info(f"Dissolving {len(gdf)} geometries in chunks")

            merged_geom = None
            n_chunks = (len(gdf) + self.chunk_size - 1) // self.chunk_size

            for chunk_id in range(n_chunks):
                start = chunk_id * self.chunk_size
                end = min(start + self.chunk_size, len(gdf))
                chunk = gdf.iloc[start:end]

                self._report_progress(
                    chunk_id + 1, n_chunks, f"Dissolving chunk {chunk_id + 1}/{n_chunks}"
                )

                # Dissolve chunk
                chunk_dissolved = chunk.dissolve()
                chunk_geom = chunk_dissolved.geometry.iloc[0]

                if merged_geom is None:
                    merged_geom = chunk_geom
                else:
                    merged_geom = merged_geom.union(chunk_geom)

                gc.collect()

            # Create result
            result = gpd.GeoDataFrame(
                {"geometry": [merged_geom]}, crs=gdf.crs
            )
            return result

        else:
            # Group by column - process each group
            groups = gdf.groupby(by)
            results = []

            for i, (name, group) in enumerate(groups):
                self._report_progress(
                    i + 1, len(groups), f"Dissolving group {name}"
                )

                dissolved = group.dissolve(by=by, aggfunc=aggfunc)
                results.append(dissolved)

            return pd.concat(results, ignore_index=True)

    def batch_intersection(
        self,
        gdf1: gpd.GeoDataFrame,
        gdf2: gpd.GeoDataFrame,
    ) -> Generator[gpd.GeoDataFrame, None, None]:
        """
        Compute geometric intersection in batches.

        Args:
            gdf1: First GeoDataFrame
            gdf2: Second GeoDataFrame

        Yields:
            GeoDataFrame chunks with intersection results
        """
        from .spatial_index import SpatialIndex

        # Build index on gdf2
        idx2 = SpatialIndex(gdf2, bulk_load=True)

        n_chunks = (len(gdf1) + self.chunk_size - 1) // self.chunk_size

        for chunk_id in range(n_chunks):
            start = chunk_id * self.chunk_size
            end = min(start + self.chunk_size, len(gdf1))
            chunk1 = gdf1.iloc[start:end]

            self._report_progress(
                chunk_id + 1, n_chunks, f"Intersecting chunk {chunk_id + 1}/{n_chunks}"
            )

            results = []

            for i, (idx1, row1) in enumerate(chunk1.iterrows()):
                geom1 = row1.geometry
                if geom1 is None or geom1.is_empty:
                    continue

                # Find candidates
                query_result = idx2.query(geom1, predicate="intersects")

                for idx2_val in query_result.indices:
                    geom2 = gdf2.geometry.iloc[idx2_val]

                    try:
                        intersection = geom1.intersection(geom2)
                        if intersection is not None and not intersection.is_empty:
                            result_row = {
                                "geometry": intersection,
                                "left_idx": idx1,
                                "right_idx": idx2_val,
                            }
                            # Add attributes from both
                            for col in chunk1.columns:
                                if col != "geometry":
                                    result_row[f"left_{col}"] = row1[col]
                            for col in gdf2.columns:
                                if col != "geometry":
                                    result_row[f"right_{col}"] = gdf2.iloc[idx2_val][col]

                            results.append(result_row)
                    except Exception as e:
                        logger.warning(f"Intersection error: {e}")

            if results:
                result_gdf = gpd.GeoDataFrame(results, crs=gdf1.crs)
                yield result_gdf

            gc.collect()

    def save_intermediate(
        self,
        gdf: gpd.GeoDataFrame,
        name: str,
    ) -> Path:
        """
        Save intermediate results to temp file.

        Args:
            gdf: GeoDataFrame to save
            name: File name (without extension)

        Returns:
            Path to saved file
        """
        path = self.temp_dir / f"{name}.parquet"
        gdf.to_parquet(path)
        logger.debug(f"Saved intermediate: {path}")
        return path

    def load_intermediate(self, name: str) -> gpd.GeoDataFrame:
        """
        Load intermediate results from temp file.

        Args:
            name: File name (without extension)

        Returns:
            Loaded GeoDataFrame
        """
        path = self.temp_dir / f"{name}.parquet"
        return gpd.read_parquet(path)

    def cleanup(self) -> None:
        """Remove temporary files."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp directory: {self.temp_dir}")


def parallel_spatial_join(
    left_gdf: gpd.GeoDataFrame,
    right_gdf: gpd.GeoDataFrame,
    predicate: str = "intersects",
    n_jobs: int = 4,
    chunk_size: int = 10000,
) -> gpd.GeoDataFrame:
    """
    Convenience function for parallel spatial join.

    Args:
        left_gdf: Left GeoDataFrame
        right_gdf: Right GeoDataFrame
        predicate: Spatial predicate
        n_jobs: Number of parallel workers
        chunk_size: Chunk size for streaming

    Returns:
        Joined GeoDataFrame
    """
    ops = BulkSpatialOps(chunk_size=chunk_size, n_jobs=n_jobs)

    chunks = list(ops.stream_spatial_join(left_gdf, right_gdf, predicate=predicate))

    if not chunks:
        return gpd.GeoDataFrame()

    return pd.concat(chunks, ignore_index=True)


def parallel_nearest_neighbors(
    query_gdf: gpd.GeoDataFrame,
    target_gdf: gpd.GeoDataFrame,
    k: int = 1,
    n_jobs: int = 4,
) -> gpd.GeoDataFrame:
    """
    Convenience function for parallel nearest neighbor search.

    Args:
        query_gdf: Query points
        target_gdf: Target geometries
        k: Number of nearest neighbors
        n_jobs: Number of parallel workers

    Returns:
        GeoDataFrame with nearest neighbor results
    """
    ops = BulkSpatialOps(n_jobs=n_jobs)
    return ops.parallel_nearest(query_gdf, target_gdf, k=k)
