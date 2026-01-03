"""
Spatial indexing module.

This module provides spatial index structures for efficient spatial queries,
achieving O(n log n) complexity instead of naive O(n²) approaches.

Key Components:
- SpatialIndex: High-performance R-tree/STRtree spatial index
- RTreeIndex: Legacy R-tree index (backward compatible)
- GridIndex: Grid-based spatial index
- Accelerated Weights: R-tree optimized spatial weights matrices
- BulkSpatialOps: Memory-efficient batch processing

Performance:
- Spatial joins: O(n log n) vs O(n²)
- K-NN queries: O(k log n)
- Range queries: O(log n + k)

Example:
    >>> from krl_geospatial.indexing import SpatialIndex, RTreeQueenWeights
    >>>
    >>> # Fast spatial index
    >>> idx = SpatialIndex(gdf, bulk_load=True)
    >>> results = idx.spatial_join(other_gdf)
    >>>
    >>> # Accelerated spatial weights
    >>> w = RTreeQueenWeights()
    >>> w.fit(gdf)  # 20x faster than libpysal
"""

from .grid_index import GridIndex
from .rtree_index import RTreeIndex
from .spatial_index import (
    IndexBackend,
    IndexStats,
    QueryResult,
    SpatialIndex,
    SpatialPredicate,
)
from .accelerated_weights import (
    RTreeDistanceBandWeights,
    RTreeKernelWeights,
    RTreeKNNWeights,
    RTreeQueenWeights,
    RTreeRookWeights,
    RTreeSpatialWeights,
    WeightsStats,
)
from .bulk_operations import (
    BatchResult,
    BulkSpatialOps,
    OperationStats,
    parallel_nearest_neighbors,
    parallel_spatial_join,
)

__all__ = [
    # Legacy index
    "RTreeIndex",
    "GridIndex",
    # New spatial index
    "SpatialIndex",
    "IndexBackend",
    "IndexStats",
    "QueryResult",
    "SpatialPredicate",
    # Accelerated weights
    "RTreeSpatialWeights",
    "RTreeQueenWeights",
    "RTreeRookWeights",
    "RTreeDistanceBandWeights",
    "RTreeKNNWeights",
    "RTreeKernelWeights",
    "WeightsStats",
    # Bulk operations
    "BulkSpatialOps",
    "BatchResult",
    "OperationStats",
    "parallel_spatial_join",
    "parallel_nearest_neighbors",
]
