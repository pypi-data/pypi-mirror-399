# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""
KRL Geospatial Tools - Geographic analysis and mapping tools.

Core functionality for spatial analysis, mapping, and econometrics.
"""

from krl_geospatial import analysis, clustering, interpolation, network
from krl_geospatial.__version__ import __author__, __license__, __version__
from krl_geospatial.core import (
    BaseGeospatialAnalyzer,
    SpatialDataFrame,
    SpatialResult,
    create_geodataframe,
)

# =============================================================================
# CONVENIENCE ALIASES FOR BACKEND INTEGRATION
# These aliases match what krl-premium-backend expects to import
# =============================================================================

# SpatialCluster - alias for SpatialDBSCAN (most common clustering use case)
from krl_geospatial.clustering import SpatialDBSCAN as SpatialCluster

# HotSpotAnalysis - alias for GetisOrdGiStar
from krl_geospatial.analysis import GetisOrdGiStar as HotSpotAnalysis

# SpatialInterpolation - alias for OrdinaryKriging (most common interpolation)
from krl_geospatial.interpolation import OrdinaryKriging as SpatialInterpolation

# GeoMapper - alias for InteractiveMap
from krl_geospatial.mapping import InteractiveMap as GeoMapper

# SpatialRegression - alias for SpatialLag (most common spatial regression)
from krl_geospatial.econometrics import SpatialLag as SpatialRegression

# =============================================================================
# CORE EXPORTS
# =============================================================================

from krl_geospatial.indexing import (
    GridIndex,
    RTreeIndex,
    SpatialIndex,
    IndexBackend,
    IndexStats,
    QueryResult,
    SpatialPredicate,
    RTreeQueenWeights,
    RTreeRookWeights,
    RTreeDistanceBandWeights,
    RTreeKNNWeights,
    RTreeKernelWeights,
    BulkSpatialOps,
    parallel_spatial_join,
    parallel_nearest_neighbors,
)
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

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # Backend integration aliases (used by krl-premium-backend)
    "SpatialCluster",
    "HotSpotAnalysis",
    "SpatialInterpolation",
    "GeoMapper",
    "SpatialRegression",
    # Core classes
    "BaseGeospatialAnalyzer",
    "SpatialResult",
    "SpatialDataFrame",
    "create_geodataframe",
    "SpatialWeights",
    "QueenWeights",
    "RookWeights",
    "KNNWeights",
    "DistanceBandWeights",
    "InverseDistanceWeights",
    "KernelWeights",
    "GaussianWeights",
    "EpanechnikovWeights",
    "TriangularWeights",
    "read_file",
    "read_shapefile",
    "read_geojson",
    "read_geoparquet",
    "read_csv",
    "write_file",
    "write_shapefile",
    "write_geojson",
    "write_geoparquet",
    "write_csv",
    # Spatial indexing
    "RTreeIndex",
    "GridIndex",
    "SpatialIndex",
    "IndexBackend",
    "IndexStats",
    "QueryResult",
    "SpatialPredicate",
    # R-tree accelerated weights
    "RTreeQueenWeights",
    "RTreeRookWeights",
    "RTreeDistanceBandWeights",
    "RTreeKNNWeights",
    "RTreeKernelWeights",
    # Bulk operations
    "BulkSpatialOps",
    "parallel_spatial_join",
    "parallel_nearest_neighbors",
    # Submodules
    "clustering",
    "analysis",
    "interpolation",
    "network",
]
