"""
Spatial DBSCAN (Density-Based Spatial Clustering of Applications with Noise).

Implements ST-DBSCAN for spatio-temporal clustering with adaptive epsilon.

© 2025 KR-Labs. All rights reserved.

References
----------
Birant, D., & Kut, A. (2007). ST-DBSCAN: An algorithm for clustering
    spatial–temporal data. Data & Knowledge Engineering, 60(1), 208-221.
"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class SpatialDBSCAN:
    """
    Spatial and Spatio-Temporal DBSCAN clustering.

    Identifies clusters of arbitrary shape in spatial data based on density.
    Points are classified as core, border, or noise based on neighborhood density.

    Parameters
    ----------
    eps : float
        Maximum distance between two samples for one to be considered
        as in the neighborhood of the other (spatial epsilon)
    min_samples : int, default=5
        Minimum number of samples in a neighborhood for a point to be
        considered a core point
    temporal_eps : float, optional
        Temporal epsilon for ST-DBSCAN. If provided, enables spatio-temporal
        clustering
    metric : str, default='euclidean'
        Distance metric for spatial coordinates

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Cluster labels. Noisy samples are given the label -1
    core_sample_indices_ : ndarray
        Indices of core samples
    n_clusters_ : int
        Number of clusters found (excluding noise)

    Examples
    --------
    >>> from krl_geospatial.clustering import SpatialDBSCAN
    >>>
    >>> # Spatial DBSCAN
    >>> dbscan = SpatialDBSCAN(eps=0.5, min_samples=5)
    >>> dbscan.fit(gdf)
    >>> labels = dbscan.labels_
    >>>
    >>> # Spatio-temporal DBSCAN
    >>> st_dbscan = SpatialDBSCAN(
    ...     eps=0.5,
    ...     min_samples=5,
    ...     temporal_eps=30  # 30 day temporal window
    ... )
    >>> st_dbscan.fit(gdf, temporal_variable='date')
    """

    def __init__(
        self,
        eps: float,
        min_samples: int = 5,
        temporal_eps: Optional[float] = None,
        metric: str = "euclidean",
    ):
        if eps <= 0:
            raise ValueError("eps must be positive")
        if min_samples < 1:
            raise ValueError("min_samples must be >= 1")
        if temporal_eps is not None and temporal_eps <= 0:
            raise ValueError("temporal_eps must be positive")

        self.eps = eps
        self.min_samples = min_samples
        self.temporal_eps = temporal_eps
        self.metric = metric

        self.labels_ = None
        self.core_sample_indices_ = None
        self.n_clusters_ = 0

    def fit(
        self,
        gdf,
        temporal_variable: Optional[str] = None,
    ):
        """
        Perform DBSCAN clustering.

        Parameters
        ----------
        gdf : GeoDataFrame
            Geographic data with observations
        temporal_variable : str, optional
            Name of temporal variable for ST-DBSCAN

        Returns
        -------
        self : SpatialDBSCAN
            Fitted estimator
        """
        # Extract spatial coordinates
        coords = np.column_stack([gdf.geometry.x, gdf.geometry.y])
        n_samples = len(coords)

        # Extract temporal data if spatio-temporal
        if self.temporal_eps is not None:
            if temporal_variable is None:
                raise ValueError("temporal_variable must be provided when temporal_eps is set")

            temporal_data = gdf[temporal_variable].values

            # Convert to numeric if datetime
            if pd.api.types.is_datetime64_any_dtype(temporal_data):
                temporal_data = (
                    pd.to_datetime(temporal_data) - pd.Timestamp("1970-01-01")
                ) // pd.Timedelta("1D")
                temporal_data = temporal_data.astype(float)

            temporal_data = temporal_data.reshape(-1, 1)
        else:
            temporal_data = None

        # Initialize labels and tracking
        self.labels_ = np.full(n_samples, -1, dtype=int)
        visited = np.zeros(n_samples, dtype=bool)
        core_samples = []
        cluster_id = 0

        # Build spatial index for efficient neighbor search
        spatial_nn = NearestNeighbors(
            radius=self.eps,
            metric=self.metric,
        )
        spatial_nn.fit(coords)

        # Build temporal index if needed
        if temporal_data is not None:
            temporal_nn = NearestNeighbors(
                radius=self.temporal_eps,
                metric="euclidean",
            )
            temporal_nn.fit(temporal_data)

        # DBSCAN algorithm
        for point_idx in range(n_samples):
            if visited[point_idx]:
                continue

            visited[point_idx] = True

            # Find neighbors
            if temporal_data is not None:
                # Spatio-temporal neighbors
                neighbors = self._find_st_neighbors(point_idx, spatial_nn, temporal_nn)
            else:
                # Spatial neighbors only
                neighbors = spatial_nn.radius_neighbors(
                    coords[point_idx].reshape(1, -1), return_distance=False
                )[0]

            # Check if core point
            if len(neighbors) < self.min_samples:
                # Mark as noise (may be changed later if within eps of a core point)
                continue

            # Core point - start new cluster
            core_samples.append(point_idx)
            self.labels_[point_idx] = cluster_id

            # Expand cluster
            seed_set = list(neighbors)
            seed_idx = 0

            while seed_idx < len(seed_set):
                neighbor_idx = seed_set[seed_idx]
                seed_idx += 1

                if not visited[neighbor_idx]:
                    visited[neighbor_idx] = True

                    # Find neighbors of neighbor
                    if temporal_data is not None:
                        neighbor_neighbors = self._find_st_neighbors(
                            neighbor_idx, spatial_nn, temporal_nn
                        )
                    else:
                        neighbor_neighbors = spatial_nn.radius_neighbors(
                            coords[neighbor_idx].reshape(1, -1), return_distance=False
                        )[0]

                    # If neighbor is core point, add its neighbors to seed set
                    if len(neighbor_neighbors) >= self.min_samples:
                        core_samples.append(neighbor_idx)
                        for nn in neighbor_neighbors:
                            if nn not in seed_set:
                                seed_set.append(nn)

                # Add to cluster if not already in a cluster
                if self.labels_[neighbor_idx] == -1:
                    self.labels_[neighbor_idx] = cluster_id

            cluster_id += 1

        self.core_sample_indices_ = np.array(core_samples)
        self.n_clusters_ = cluster_id

        return self

    def _find_st_neighbors(self, point_idx, spatial_nn, temporal_nn):
        """Find spatio-temporal neighbors."""
        # Get spatial neighbors
        spatial_neighbors = spatial_nn.radius_neighbors(
            [[point_idx]], return_distance=False  # Query by index
        )[0]

        # Get temporal neighbors
        temporal_neighbors = temporal_nn.radius_neighbors([[point_idx]], return_distance=False)[0]

        # Intersection of spatial and temporal neighbors
        st_neighbors = np.intersect1d(spatial_neighbors, temporal_neighbors)

        return st_neighbors

    def fit_predict(self, gdf, temporal_variable: Optional[str] = None):
        """
        Perform clustering and return cluster labels.

        Parameters
        ----------
        gdf : GeoDataFrame
            Geographic data with observations
        temporal_variable : str, optional
            Name of temporal variable for ST-DBSCAN

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Cluster labels
        """
        self.fit(gdf, temporal_variable=temporal_variable)
        return self.labels_
