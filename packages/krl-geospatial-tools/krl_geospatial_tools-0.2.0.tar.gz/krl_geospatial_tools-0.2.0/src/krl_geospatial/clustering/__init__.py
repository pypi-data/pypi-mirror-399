"""
Spatial clustering algorithms and regionalization methods.

This module provides spatially-constrained clustering algorithms for
regionalization, hot spot detection, and pattern discovery in geographic data.

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC.

Classes
-------
SKATER : Minimum spanning tree-based regionalization
MaxP : Maximum regions with threshold constraints
REDCAP : Spatially constrained hierarchical clustering
SpatialDBSCAN : Density-based spatial clustering

Functions
---------
silhouette_score : Silhouette coefficient for cluster quality
davies_bouldin_index : DB index for cluster compactness
calinski_harabasz_index : CH index for cluster separation

Examples
--------
>>> from krl_geospatial import clustering
>>> from krl_geospatial.weights import QueenWeights
>>>
>>> # SKATER regionalization
>>> skater = clustering.SKATER(n_clusters=5)
>>> skater.fit(gdf, weights, attributes=['income', 'density'])
>>> labels = skater.labels_
>>>
>>> # Evaluate clustering quality
>>> score = clustering.silhouette_score(gdf, labels, weights)
"""

from .dbscan import SpatialDBSCAN
from .maxp import MaxP
from .metrics import (
    calinski_harabasz_index,
    davies_bouldin_index,
    silhouette_score,
    spatial_connectivity_index,
)
from .redcap import REDCAP
from .skater import SKATER

__all__ = [
    "SKATER",
    "MaxP",
    "REDCAP",
    "SpatialDBSCAN",
    "silhouette_score",
    "davies_bouldin_index",
    "calinski_harabasz_index",
    "spatial_connectivity_index",
]
